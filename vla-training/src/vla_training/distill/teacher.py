"""Frozen teacher model loading and inference.

The teacher is loaded from a pre-trained VLA checkpoint, frozen completely
(no gradients), and used only to produce soft action predictions and
(optionally) intermediate features for the student to imitate.

Why a separate wrapper: the teacher may come from a different model family
than the student (e.g. Hy-Embodied teacher → OpenVLA student).  The wrapper
isolates those differences so the distillation step stays model-agnostic.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

logger = logging.getLogger(__name__)


class TeacherModel:
    """A frozen VLA used as a soft target generator for distillation.

    Wraps a model adapter (or a raw HF model) and provides two inference-only
    methods: action prediction and intermediate feature extraction.
    """

    def __init__(self, model: Any, processor: Any, device: str) -> None:
        self.model = model
        self.processor = processor
        self.device = device

        # Freeze everything.
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad = False

        logger.info(
            "teacher loaded: %s (%.1fM params, all frozen)",
            type(model).__name__,
            sum(p.numel() for p in model.parameters()) / 1e6,
        )

    @classmethod
    def from_config(cls, config: Mapping[str, Any], device: str) -> "TeacherModel":
        """Build a teacher from the ``distill`` config block.

        The teacher can use the same adapter registry as the student, allowing
        cross-family distillation (e.g. Hy-Embodied teacher → OpenVLA student).
        """
        from ..models.adapter import get_adapter

        teacher_config = _build_teacher_config(config)
        adapter = get_adapter(teacher_config)
        return cls(adapter.model, adapter.processor, device)

    @classmethod
    def from_adapter(cls, adapter: Any, device: str) -> "TeacherModel":
        """Wrap an already-loaded adapter as a frozen teacher."""
        return cls(adapter.model, adapter.processor if hasattr(adapter, "processor") else None, device)

    # --- inference ---------------------------------------------------------

    def predict_actions(self, batch: dict[str, Any]) -> Any:
        """Return the teacher's action prediction for *batch* (no grad)."""
        import torch

        with torch.no_grad():
            if hasattr(self, "_adapter") and self._adapter is not None:
                return self._adapter.predict_actions(batch, self.device)
            # Fallback: use the student adapter's preprocess + raw model call.
            outputs = self.model(**self._prepare_inputs(batch))
            return _extract_actions(outputs)

    def get_features(self, batch: dict[str, Any], layer: str | None = None) -> Any:
        """Extract intermediate representations from the teacher.

        When *layer* is ``None``, returns the last hidden state before the
        action head.  The exact tensor depends on the model architecture.
        """
        import torch

        with torch.no_grad():
            inputs = self._prepare_inputs(batch)
            if hasattr(self.model, "get_intermediate_features"):
                return self.model.get_intermediate_features(**inputs, layer=layer)
            # Fallback: run the full forward and grab hidden_states.
            inputs["output_hidden_states"] = True
            outputs = self.model(**inputs)
            hidden = getattr(outputs, "hidden_states", None)
            if hidden is not None:
                return hidden[-1]  # last layer
            return None

    # --- internals ---------------------------------------------------------

    def _prepare_inputs(self, batch: dict[str, Any]) -> dict[str, Any]:
        """Move batch tensors to the teacher's device."""
        import torch

        prepared: dict[str, Any] = {}
        for key, value in batch.items():
            if isinstance(value, torch.Tensor):
                prepared[key] = value.to(self.device)
            elif isinstance(value, dict):
                prepared[key] = {
                    k: v.to(self.device) if isinstance(v, torch.Tensor) else v
                    for k, v in value.items()
                }
            else:
                prepared[key] = value
        return prepared


def build_teacher(config: Mapping[str, Any], device: str) -> TeacherModel:
    """Construct a frozen teacher from the training config.

    Called by :func:`vla_training.train.finetune._build_teacher` when
    ``distill.enabled`` is ``True``.
    """
    return TeacherModel.from_config(config, device)


# --- helpers ---------------------------------------------------------------


def _build_teacher_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Derive a model config for the teacher from the distill config block.

    The teacher reuses the student's adapter registry but with its own
    ``model.base_model`` and ``model.family``.
    """
    distill_cfg = config.get("distill", {})
    teacher_model = str(distill_cfg.get("teacher_model", ""))
    teacher_family = str(distill_cfg.get("teacher_family", "hy_embodied"))

    if not teacher_model:
        raise ValueError("distill.teacher_model is required when distill.enabled=true")

    # Build a minimal config that the adapter registry can consume.
    teacher_config: dict[str, Any] = {
        "model": {
            "base_model": teacher_model,
            "family": teacher_family,
            "trust_remote_code": bool(distill_cfg.get("teacher_trust_remote_code", True)),
            "load_in_4bit": bool(distill_cfg.get("teacher_load_in_4bit", False)),
        },
    }
    return teacher_config


def _extract_actions(outputs: Any) -> Any:
    """Pull the action tensor from a model output."""
    for attr in ("actions", "action", "logits"):
        if hasattr(outputs, attr):
            return getattr(outputs, attr)
    if isinstance(outputs, dict):
        for key in ("actions", "action", "logits"):
            if key in outputs:
                return outputs[key]
    raise AttributeError("could not extract actions from teacher output")
