"""Base VLA model loading and LoRA adapter injection.

**No weights are downloaded by this repository.** Fetch the base checkpoint
explicitly before training; keeping that step manual avoids a multi-GB implicit
download inside a build or CI run.

Why LoRA: full fine-tuning of a 7B VLA needs ~80GB VRAM, while training only
low-rank adapters on the attention projections fits a single 24GB card. The
frozen base also retains its pretrained visual/language grounding instead of
catastrophically forgetting it on a comparatively tiny robot dataset.

Model adapter registry
----------------------
The old ``NotImplementedError`` stubs for ``load_base_model`` and
``load_processor`` have been replaced by a :class:`ModelAdapter` pattern.
Each supported VLA family registers an adapter that knows how to load its
checkpoint, preprocess batches, compute losses and merge adapters.  The
training loop and evaluator call through the adapter so they stay
model-agnostic.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Mapping

from ..config import get_by_path, require
from .adapter import ModelAdapter, get_adapter

# Importing families triggers registration as a side-effect.
from . import families  # noqa: F401

logger = logging.getLogger(__name__)


class ModelLoadError(RuntimeError):
    """Raised when the base model or adapter cannot be prepared."""


# ---------------------------------------------------------------------------
# Public API -- adapter-based
# ---------------------------------------------------------------------------


def build_adapter(config: Mapping[str, Any]) -> ModelAdapter:
    """Load the base model, attach LoRA and return a ready-to-train adapter.

    This is the main entry point for the training loop.  It replaces the old
    ``load_base_model`` + ``apply_lora`` two-step with a single call that
    returns a fully assembled :class:`ModelAdapter`.
    """
    adapter = get_adapter(config)
    adapter.model = apply_lora(adapter.model, config)

    # Optional gradient checkpointing.
    if bool(get_by_path(config, "training.gradient_checkpointing", False)):
        if hasattr(adapter.model, "gradient_checkpointing_enable"):
            adapter.model.gradient_checkpointing_enable()

    device = str(get_by_path(config, "runtime.device", "auto"))
    if device != "auto":
        adapter.model = adapter.model.to(device)

    return adapter


def load_base_model(config: Mapping[str, Any]) -> Any:
    """Load the frozen base VLA checkpoint described by ``model.base_model``.

    Delegates to the adapter registered for ``model.family``.
    """
    base_model = require(config, "model.base_model")
    load_in_4bit = bool(get_by_path(config, "model.load_in_4bit", False))
    logger.info("base model=%s load_in_4bit=%s", base_model, load_in_4bit)

    adapter = get_adapter(config)
    return adapter.model


def load_processor(config: Mapping[str, Any]) -> Any:
    """Load the base model's image/text processor.

    The dataset must preprocess images exactly the way the base model expects;
    this processor is the single source of truth for that, which is why image
    loading is not implemented independently in the dataset.
    """
    adapter = get_adapter(config)
    return adapter.processor


def load_image(path: str | Path, config: Mapping[str, Any]) -> Any:
    """Load and preprocess one camera image using the model's processor.

    Used by :class:`~vla_training.data.dataset.VLADataset` so that image
    decoding matches the base model expectations without the dataset needing
    to know the processor details.
    """
    from PIL import Image

    img = Image.open(str(path)).convert("RGB")

    # Resize to the resolution declared in the config.
    images_cfg = get_by_path(config, "observation.images", []) or []
    if images_cfg:
        w, h = images_cfg[0].get("resolution", [224, 224])
        img = img.resize((int(w), int(h)))
    return img


# ---------------------------------------------------------------------------
# LoRA (unchanged)
# ---------------------------------------------------------------------------


def apply_lora(model: Any, config: Mapping[str, Any]) -> Any:
    """Wrap ``model`` with PEFT LoRA adapters per the ``lora`` config block.

    ``modules_to_save`` must include the action head: it is randomly initialised
    for our action space, and a low-rank *update* to random weights cannot learn
    it -- that head has to be fully trainable.
    """
    if not bool(get_by_path(config, "lora.enabled", True)):
        logger.info("LoRA disabled; returning the base model unchanged")
        return model

    try:
        from peft import LoraConfig, get_peft_model
    except ImportError as exc:  # pragma: no cover - dependency not installed
        raise ModelLoadError(
            "peft is required for LoRA; install vla-training/requirements.txt"
        ) from exc

    lora_config = LoraConfig(
        r=int(get_by_path(config, "lora.r", 32)),
        lora_alpha=int(get_by_path(config, "lora.alpha", 64)),
        lora_dropout=float(get_by_path(config, "lora.dropout", 0.05)),
        bias=str(get_by_path(config, "lora.bias", "none")),
        target_modules=list(
            get_by_path(config, "lora.target_modules", ["q_proj", "k_proj", "v_proj", "o_proj"])
        ),
        modules_to_save=list(get_by_path(config, "lora.modules_to_save", []) or []),
        task_type="FEATURE_EXTRACTION",
    )
    wrapped = get_peft_model(model, lora_config)
    log_trainable_parameters(wrapped)
    return wrapped


def log_trainable_parameters(model: Any) -> tuple[int, int]:
    """Report trainable vs total parameters.

    Worth checking every run: a mistyped ``target_modules`` entry silently
    matches nothing, and the resulting run trains ~0 parameters while otherwise
    looking completely healthy.
    """
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    pct = 100.0 * trainable / total if total else 0.0
    logger.info("trainable params: %d / %d (%.4f%%)", trainable, total, pct)
    if trainable == 0:
        raise ModelLoadError(
            "no trainable parameters -- check lora.target_modules matches the "
            "base model's layer names"
        )
    return trainable, total
