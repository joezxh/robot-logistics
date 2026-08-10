"""LoRA fine-tuning entry point.

Assembles config, data, model and optimiser, then runs the training loop. The
loop structure, checkpointing policy and metric bookkeeping are concrete; the
forward/backward step delegates to the model adapter so the loop stays
model-agnostic.

Distillation
~~~~~~~~~~~~
When ``distill.enabled`` is set in the config the training step switches to
:func:`vla_training.distill.step.distillation_step`, which adds a teacher
guidance loss on top of the ground-truth action loss.  See
:mod:`vla_training.distill` for details.
"""
from __future__ import annotations

import json
import logging
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from ..config import get_by_path, resolve_device

logger = logging.getLogger(__name__)


@dataclass
class TrainState:
    """Mutable run state. Persisted with each checkpoint so a run can resume."""

    step: int = 0
    epoch: int = 0
    best_metric: float = float("inf")
    history: list[dict[str, float]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "epoch": self.epoch,
            "best_metric": self.best_metric,
            "history": self.history,
        }


def set_seed(seed: int) -> None:
    """Seed every RNG that affects a run."""
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass
    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def finetune(config: Mapping[str, Any]) -> TrainState:
    """Run LoRA fine-tuning end to end."""
    seed = int(get_by_path(config, "seed", 42))
    set_seed(seed)

    device = resolve_device(config)
    output_dir = Path(str(get_by_path(config, "paths.output_dir", "outputs")))
    ckpt_dir = Path(str(get_by_path(config, "paths.checkpoint_dir", "outputs/checkpoints")))
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    logger.info("starting fine-tune: device=%s seed=%d output=%s", device, seed, output_dir)

    # Record the exact resolved config next to the checkpoints -- without it a
    # checkpoint six months later is unreproducible.
    (output_dir / "resolved_config.json").parent.mkdir(parents=True, exist_ok=True)
    (output_dir / "resolved_config.json").write_text(
        json.dumps(dict(config), indent=2, default=str), encoding="utf-8"
    )

    train_loader, val_loader = build_dataloaders(config)
    adapter = build_model(config, device)

    # When distillation is enabled, load the teacher model.
    teacher = None
    if bool(get_by_path(config, "distill.enabled", False)):
        teacher = _build_teacher(config, device)
        logger.info("distillation enabled: teacher=%s", get_by_path(config, "distill.teacher_model", ""))

    optimizer, scheduler = build_optimizer(adapter, config, steps_per_epoch=len(train_loader))

    state = TrainState()
    epochs = int(get_by_path(config, "training.epochs", 10))
    accum = int(get_by_path(config, "training.gradient_accumulation_steps", 1))
    eval_every = int(get_by_path(config, "evaluation.eval_every_n_steps", 500))
    save_every = int(get_by_path(config, "checkpointing.save_every_n_steps", 500))
    log_every = int(get_by_path(config, "logging.log_every_n_steps", 10))

    for epoch in range(epochs):
        state.epoch = epoch
        for batch_idx, batch in enumerate(train_loader):
            loss = training_step(adapter, batch, device, teacher=teacher)
            # Scale so the effective gradient matches a true large batch.
            (loss / accum).backward()

            if (batch_idx + 1) % accum == 0:
                clip_gradients(adapter, config)
                optimizer.step()
                if scheduler is not None:
                    scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                state.step += 1

                if state.step % log_every == 0:
                    logger.info("epoch=%d step=%d loss=%.5f", epoch, state.step, float(loss))
                if eval_every and state.step % eval_every == 0:
                    metrics = evaluate_step(adapter, val_loader, device)
                    state.history.append({"step": state.step, **metrics})
                    state.best_metric = maybe_save_best(
                        adapter, state, metrics, ckpt_dir, config
                    )
                if save_every and state.step % save_every == 0:
                    save_checkpoint(adapter, state, ckpt_dir / f"step-{state.step}", config)

    save_checkpoint(adapter, state, ckpt_dir / "final", config)
    logger.info("fine-tune complete: %d steps, best=%.5f", state.step, state.best_metric)
    return state


# --- assembly ---------------------------------------------------------------


def build_dataloaders(config: Mapping[str, Any]):
    """Construct train/val loaders from the processed dataset."""
    from ..data.dataset import VLADataset, build_dataloader

    processed = Path(str(get_by_path(config, "paths.processed_data_dir", "data/processed")))
    chunk = int(get_by_path(config, "action.chunk_size", 1))
    cameras = [c["name"] for c in get_by_path(config, "observation.images", []) or []]
    batch_size = int(get_by_path(config, "training.batch_size", 8))
    workers = int(get_by_path(config, "runtime.num_workers", 4))

    train_ds = VLADataset(processed / "train", chunk_size=chunk, camera_names=cameras, config=config)
    val_ds = VLADataset(processed / "val", stats=train_ds.stats, chunk_size=chunk, camera_names=cameras, config=config)

    return (
        build_dataloader(train_ds, batch_size=batch_size, shuffle=True, num_workers=workers),
        build_dataloader(val_ds, batch_size=batch_size, shuffle=False, num_workers=workers),
    )


def build_model(config: Mapping[str, Any], device: str) -> Any:
    """Load the base model, attach LoRA adapters and return a ModelAdapter.

    Uses :func:`~vla_training.models.loader.build_adapter` which handles
    model loading, LoRA injection, gradient checkpointing and device placement
    in one call.
    """
    from ..models.loader import build_adapter

    adapter = build_adapter(config)
    # Move to device if build_adapter didn't already (device=auto case).
    if device != "auto" and hasattr(adapter.model, "to"):
        try:
            adapter.model = adapter.model.to(device)
        except Exception:
            pass  # already on device (e.g. 4-bit)
    return adapter


def _build_teacher(config: Mapping[str, Any], device: str) -> Any:
    """Lazily import and build the distillation teacher to keep the import optional."""
    from ..distill.teacher import build_teacher

    return build_teacher(config, device)


def build_optimizer(model: Any, config: Mapping[str, Any], *, steps_per_epoch: int):
    """AdamW over the trainable (adapter) parameters, plus an LR schedule."""
    import torch

    # Support both raw models and ModelAdapter wrappers.
    if hasattr(model, "parameters") and hasattr(model, "trainable_only"):
        # ModelAdapter -- use its helper
        params = list(model.parameters(trainable_only=True))
    else:
        params = [p for p in model.parameters() if p.requires_grad]

    optimizer = torch.optim.AdamW(
        params,
        lr=float(get_by_path(config, "training.learning_rate", 2e-4)),
        weight_decay=float(get_by_path(config, "training.weight_decay", 0.01)),
    )

    epochs = int(get_by_path(config, "training.epochs", 10))
    accum = max(int(get_by_path(config, "training.gradient_accumulation_steps", 1)), 1)
    total_steps = max((steps_per_epoch // accum) * epochs, 1)
    warmup = int(total_steps * float(get_by_path(config, "training.warmup_ratio", 0.03)))

    scheduler = None
    if str(get_by_path(config, "training.lr_scheduler", "cosine")) == "cosine":
        try:
            from transformers import get_cosine_schedule_with_warmup

            scheduler = get_cosine_schedule_with_warmup(optimizer, warmup, total_steps)
        except ImportError:
            logger.warning("transformers unavailable; running with a constant LR")

    return optimizer, scheduler


def clip_gradients(model: Any, config: Mapping[str, Any]) -> None:
    max_norm = float(get_by_path(config, "training.max_grad_norm", 0.0))
    if max_norm <= 0:
        return
    import torch

    if hasattr(model, "parameters"):
        grads = [p for p in model.parameters(trainable_only=True)] if hasattr(model, "trainable_only") else [p for p in model.parameters() if p.requires_grad]
    else:
        grads = [p for p in model.parameters() if p.requires_grad]
    torch.nn.utils.clip_grad_norm_(grads, max_norm)


# --- steps ------------------------------------------------------------------


def training_step(adapter: Any, batch: Any, device: str, *, teacher: Any = None) -> Any:
    """One forward pass returning a scalar loss.

    When *teacher* is ``None`` this computes the standard imitation loss
    (MSE between predicted and ground-truth actions).  When a teacher is
    provided, the loss is a weighted combination of imitation loss and
    distillation loss (KL divergence + feature alignment).
    """
    if teacher is not None:
        from ..distill.step import distillation_step

        return distillation_step(adapter, teacher, batch, device, adapter.config)

    return adapter.compute_loss(batch, device)


def evaluate_step(adapter: Any, val_loader: Any, device: str) -> dict[str, float]:
    """Validation pass returning the metrics named in ``evaluation.metrics``."""
    from ..eval.evaluate import evaluate_offline

    return evaluate_offline(adapter, val_loader, device)


# --- checkpointing ----------------------------------------------------------


def save_checkpoint(adapter: Any, state: TrainState, path: Path, config: Mapping[str, Any]) -> None:
    """Persist adapters plus run state.

    Only the LoRA adapters are saved -- a few tens of MB against ~14GB for the
    frozen base, which is the whole point of the approach.
    """
    path.mkdir(parents=True, exist_ok=True)
    model = adapter.model if hasattr(adapter, "model") else adapter
    if hasattr(model, "save_pretrained"):
        model.save_pretrained(path)
    (path / "train_state.json").write_text(
        json.dumps(state.to_dict(), indent=2), encoding="utf-8"
    )
    logger.info("saved checkpoint to %s", path)


def maybe_save_best(
    adapter: Any,
    state: TrainState,
    metrics: Mapping[str, float],
    ckpt_dir: Path,
    config: Mapping[str, Any],
) -> float:
    """Save a 'best' checkpoint when the tracked metric improves."""
    metric_name = str(get_by_path(config, "checkpointing.metric_for_best", "val_action_mse"))
    greater_is_better = bool(get_by_path(config, "checkpointing.greater_is_better", False))
    value = metrics.get(metric_name)
    if value is None:
        logger.warning("metric %s not reported; skipping best-checkpoint check", metric_name)
        return state.best_metric

    improved = value > state.best_metric if greater_is_better else value < state.best_metric
    if not improved:
        return state.best_metric

    logger.info("new best %s=%.5f (was %.5f)", metric_name, value, state.best_metric)
    save_checkpoint(adapter, state, ckpt_dir / "best", config)
    return value
