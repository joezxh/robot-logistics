"""Base VLA model loading and LoRA adapter injection.

**No weights are downloaded by this repository.** Fetch the base checkpoint
explicitly before training; keeping that step manual avoids a multi-GB implicit
download inside a build or CI run.

Why LoRA: full fine-tuning of a 7B VLA needs ~80GB VRAM, while training only
low-rank adapters on the attention projections fits a single 24GB card. The
frozen base also retains its pretrained visual/language grounding instead of
catastrophically forgetting it on a comparatively tiny robot dataset.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

from ..config import get_by_path, require

logger = logging.getLogger(__name__)


class ModelLoadError(RuntimeError):
    """Raised when the base model or adapter cannot be prepared."""


def load_base_model(config: Mapping[str, Any]) -> Any:
    """Load the frozen base VLA checkpoint described by ``model.base_model``.

    Skeleton: the concrete call differs per model family (OpenVLA exposes an
    ``AutoModelForVision2Seq``, RT-family checkpoints do not), so it is left to
    be filled in once a base model is chosen and downloaded.
    """
    base_model = require(config, "model.base_model")
    load_in_4bit = bool(get_by_path(config, "model.load_in_4bit", False))
    logger.info("base model=%s load_in_4bit=%s", base_model, load_in_4bit)

    raise NotImplementedError(
        f"download {base_model} and wire up the loader; see vla-training/README.md"
    )


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


def load_processor(config: Mapping[str, Any]) -> Any:
    """Load the base model's image/text processor.

    The dataset must preprocess images exactly the way the base model expects;
    this processor is the single source of truth for that, which is why image
    loading is not implemented independently in the dataset.
    """
    base_model = require(config, "model.base_model")
    raise NotImplementedError(
        f"load the processor for {base_model}; see vla-training/README.md"
    )
