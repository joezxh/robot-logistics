"""Model adapter interface and registry.

Every supported VLA family (Hy-Embodied, OpenVLA, ...) implements this
interface so the training loop, evaluator and exporter can work with any of
them without branching on model family.

Why an adapter: the forward-pass signature, loss computation and image
preprocessing differ across model families.  Wrapping those differences behind
a uniform interface keeps ``finetune.py`` and ``evaluate.py`` model-agnostic.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Abstract adapter
# ---------------------------------------------------------------------------

_ADAPTER_REGISTRY: dict[str, type] = {}


class ModelAdapter:
    """Uniform interface every model family must implement.

    A single adapter instance owns both the model and its processor, so
    ``preprocess_batch`` can apply model-specific image normalisation and
    ``compute_loss`` knows exactly which output tensor holds the actions.
    """

    # --- construction ------------------------------------------------------

    def __init__(self, model: Any, processor: Any, config: Mapping[str, Any]) -> None:
        self.model = model
        self.processor = processor
        self.config = config

    # --- required overrides ------------------------------------------------

    def preprocess_batch(self, batch: dict[str, Any], device: str) -> dict[str, Any]:
        """Move *batch* to *device* and apply model-specific preprocessing.

        Must return a dict with at least ``"model_inputs"`` (kwargs for the
        model's ``forward``) and optionally ``"ground_truth_actions"``.
        """
        raise NotImplementedError

    def compute_loss(self, batch: dict[str, Any], device: str) -> Any:
        """Run the forward pass and return a scalar loss tensor."""
        raise NotImplementedError

    def predict_actions(self, batch: dict[str, Any], device: str) -> Any:
        """Inference-only forward returning predicted actions (no grad)."""
        raise NotImplementedError

    def merge_adapters(self, export_dir: Any) -> None:
        """Merge LoRA adapters into the base weights and save to *export_dir*.

        Default implementation uses the standard PEFT / transformers save path.
        Families that need a custom merge (e.g. non-HF checkpoints) should
        override this.
        """
        raise NotImplementedError

    # --- optional hooks ----------------------------------------------------

    def train(self, mode: bool = True) -> None:
        self.model.train(mode)

    def eval(self) -> None:
        self.model.eval()

    def parameters(self, trainable_only: bool = False) -> Any:
        params = self.model.parameters()
        if trainable_only:
            return [p for p in params if p.requires_grad]
        return params


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def register_adapter(family: str, adapter_cls: type) -> None:
    """Register *adapter_cls* under *family*.

    Call at import time from each family module so the registry is populated
    before any config is resolved.
    """
    key = family.lower()
    if key in _ADAPTER_REGISTRY:
        logger.warning("overwriting adapter for family '%s'", family)
    _ADAPTER_REGISTRY[key] = adapter_cls
    logger.debug("registered adapter '%s' -> %s", key, adapter_cls.__name__)


def get_adapter(config: Mapping[str, Any]) -> ModelAdapter:
    """Build the adapter for the model family declared in *config*.

    The family is read from ``model.family`` (e.g. ``"hy_embodied"``,
    ``"openvla"``).  The adapter constructor receives the full config so it
    can read model-specific keys.
    """
    family = str(config.get("model", {}).get("family", "openvla")).lower()
    if family not in _ADAPTER_REGISTRY:
        available = ", ".join(sorted(_ADAPTER_REGISTRY)) or "(none)"
        raise ValueError(
            f"unknown model family '{family}'; available: {available}. "
            f"Register an adapter in vla_training.models.adapter first."
        )
    return _ADAPTER_REGISTRY[family](config)


def list_families() -> list[str]:
    """Return the names of all registered model families."""
    return sorted(_ADAPTER_REGISTRY)
