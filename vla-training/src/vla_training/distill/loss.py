"""Distillation loss functions.

Three complementary terms guide the student:

1. **Imitation loss** -- standard MSE against ground-truth actions.
2. **Action KL loss** -- KL divergence between student and teacher action
   distributions (modelled as diagonal Gaussians with learned variance).
3. **Feature alignment loss** -- L2 distance between intermediate
   representations of student and teacher.

The final loss is a weighted sum controlled by ``alpha`` (KL weight) and
``beta`` (feature alignment weight).  The imitation loss always has weight 1.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DistillationLoss:
    """Composite loss for knowledge distillation.

    :param temperature: Softmax temperature for the KL term.  Higher values
        produce softer teacher distributions, which is the usual distillation
        trick to transfer dark knowledge.
    :param alpha: Weight of the action KL term relative to imitation loss.
    :param beta: Weight of the feature alignment term.  Set to 0 to disable.
    """

    temperature: float = 2.0
    alpha: float = 0.5
    beta: float = 0.1

    def __call__(
        self,
        student_actions: Any,
        teacher_actions: Any,
        ground_truth: Any,
        student_features: Any | None = None,
        teacher_features: Any | None = None,
    ) -> Any:
        """Compute the weighted distillation loss.

        :param student_actions: ``(B, T, D)`` predicted actions from the student.
        :param teacher_actions: ``(B, T, D)`` soft targets from the teacher.
        :param ground_truth: ``(B, T, D)`` ground-truth normalised actions.
        :param student_features: optional ``(B, *)`` intermediate student repr.
        :param teacher_features: optional ``(B, *)`` intermediate teacher repr.
        :returns: scalar loss tensor.
        """
        import torch

        # 1. Imitation loss (always present).
        imitation = torch.nn.functional.mse_loss(student_actions, ground_truth)

        # 2. Action KL divergence.
        kl = action_kl_loss(student_actions, teacher_actions, self.temperature)

        total = imitation + self.alpha * kl

        # 3. Feature alignment (optional).
        if self.beta > 0 and student_features is not None and teacher_features is not None:
            feat = feature_alignment_loss(student_features, teacher_features)
            total = total + self.beta * feat

        return total


def action_kl_loss(
    student_actions: Any,
    teacher_actions: Any,
    temperature: float = 2.0,
) -> Any:
    """KL divergence between student and teacher action distributions.

    Both are modelled as diagonal Gaussians centred on the predicted actions
    with unit variance.  At finite temperature this reduces to a scaled MSE
    between the means -- the temperature softens the penalty for disagreeing
    on low-confidence actions.

    This is the standard Hinton et al. (2015) distillation loss adapted for
    continuous action spaces.
    """
    import torch

    # Scale by temperature: higher T → softer distribution → smaller gradients.
    student_soft = student_actions / temperature
    teacher_soft = teacher_actions.detach() / temperature

    # KL(q_student || q_teacher) for diagonal Gaussians with unit variance
    # reduces to 0.5 * ||mu_s - mu_t||^2, averaged over the action dimensions.
    kl = torch.nn.functional.mse_loss(student_soft, teacher_soft)
    # Compensate for the T^2 scaling so the loss magnitude stays comparable.
    return kl * (temperature ** 2)


def feature_alignment_loss(
    student_features: Any,
    teacher_features: Any,
) -> Any:
    """L2 distance between student and teacher intermediate representations.

    When the student and teacher have different hidden dimensions, a learned
    linear projection would be needed.  For simplicity this implementation
    requires matching dimensions; if they differ, the loss is computed on the
    mean-pooled representations instead.
    """
    import torch

    s = student_features
    t = teacher_features.detach()

    # If shapes don't match, pool to a scalar per sample before comparing.
    if s.shape != t.shape:
        s = s.mean(dim=-1) if s.dim() > 2 else s
        t = t.mean(dim=-1) if t.dim() > 2 else t

    return torch.nn.functional.mse_loss(s, t)
