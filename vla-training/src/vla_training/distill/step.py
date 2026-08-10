"""Distillation training step.

This module provides :func:`distillation_step`, the drop-in replacement for
the standard ``training_step`` when knowledge distillation is enabled.  It
runs both the student and teacher forward passes, computes the composite
distillation loss, and returns a scalar for backpropagation.

Integration
~~~~~~~~~~~
Called from :func:`vla_training.train.finetune.training_step` when
``distill.enabled`` is ``True`` in the config.  The teacher is passed as an
extra argument so the training loop signature stays the same.
"""
from __future__ import annotations

import logging
from typing import Any, Mapping

from ..config import get_by_path

logger = logging.getLogger(__name__)


def distillation_step(
    student: Any,
    teacher: Any,
    batch: dict[str, Any],
    device: str,
    config: Mapping[str, Any],
) -> Any:
    """One distillation forward pass returning a scalar loss.

    :param student: the student :class:`~vla_training.models.adapter.ModelAdapter`
        (with LoRA, in train mode).
    :param teacher: the frozen :class:`~vla_training.distill.teacher.TeacherModel`.
    :param batch: a collated batch from the DataLoader.
    :param device: target device string.
    :param config: full training config (reads ``distill.*`` keys).
    :returns: scalar loss tensor.
    """
    import torch

    from .loss import DistillationLoss

    # --- read distillation hyper-parameters --------------------------------
    temperature = float(get_by_path(config, "distill.temperature", 2.0))
    alpha = float(get_by_path(config, "distill.alpha", 0.5))
    beta = float(get_by_path(config, "distill.beta", 0.1))
    feature_layer = get_by_path(config, "distill.feature_layer", None)

    loss_fn = DistillationLoss(temperature=temperature, alpha=alpha, beta=beta)

    # --- student forward ---------------------------------------------------
    student.train()
    prepared = student.preprocess_batch(batch, device)
    model_inputs = prepared["model_inputs"]
    student_outputs = student.model(**model_inputs)

    # Extract student action predictions.
    student_actions = _extract_actions(student_outputs, student)
    ground_truth = prepared["ground_truth_actions"]

    # --- teacher forward (no grad) -----------------------------------------
    teacher_actions = teacher.predict_actions(batch)

    # Optional: extract intermediate features for alignment.
    student_features = None
    teacher_features = None
    if beta > 0 and feature_layer is not None:
        teacher_features = teacher.get_features(batch, layer=str(feature_layer))
        # Student features from the same relative position.
        student_features = _get_student_features(student_outputs, str(feature_layer))

    # --- composite loss ----------------------------------------------------
    loss = loss_fn(
        student_actions=student_actions,
        teacher_actions=teacher_actions,
        ground_truth=ground_truth,
        student_features=student_features,
        teacher_features=teacher_features,
    )

    return loss


# --- helpers ---------------------------------------------------------------


def _extract_actions(outputs: Any, adapter: Any) -> Any:
    """Extract action predictions from model outputs."""
    action_key = str(adapter.config.get("model", {}).get("action_key", "actions"))
    for attr in (action_key, "actions", "action", "logits"):
        if hasattr(outputs, attr):
            return getattr(outputs, attr)
    if isinstance(outputs, dict):
        for key in (action_key, "actions", "action", "logits"):
            if key in outputs:
                return outputs[key]
    raise AttributeError(
        f"could not extract actions from student output "
        f"(tried '{action_key}', 'actions', 'action', 'logits')"
    )


def _get_student_features(outputs: Any, layer: str) -> Any:
    """Try to extract intermediate features from student outputs."""
    hidden = getattr(outputs, "hidden_states", None)
    if hidden is not None:
        return hidden[-1]
    # Some models expose features via a different attribute.
    if hasattr(outputs, "features"):
        return outputs.features
    return None
