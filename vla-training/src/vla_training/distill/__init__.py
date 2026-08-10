"""Knowledge distillation for VLA models.

This module enables training a smaller *student* VLA under the guidance of a
larger, pre-trained *teacher* VLA.  The teacher is kept frozen and used only
to produce soft targets that regularise the student's action distribution.

Design
------
The distillation loss is a weighted combination of three terms:

1. **Imitation loss** (MSE) -- the student still learns from ground-truth
   demonstrated actions, exactly as in the non-distillation path.
2. **Action KL loss** -- KL divergence between the student's and teacher's
   predicted action distributions (modelled as diagonal Gaussians).
3. **Feature alignment loss** (optional) -- L2 distance between intermediate
   representations, encouraging the student to learn the teacher's visual
   grounding.

Config keys (under ``distill``)::

    distill:
      enabled: true
      teacher_model: tencent/HY-Embodied-0.5   # or another VLA checkpoint
      teacher_family: hy_embodied
      temperature: 2.0
      alpha: 0.5           # weight for the KL term
      beta: 0.1            # weight for the feature alignment term
      feature_layer: null  # name of the intermediate layer to align

Usage
~~~~~
Distillation is activated by setting ``distill.enabled: true`` in the training
config.  The training loop in :mod:`vla_training.train.finetune` detects this
flag and switches to :func:`distillation_step` instead of the standard
training step.
"""

from .loss import DistillationLoss, action_kl_loss, feature_alignment_loss
from .step import distillation_step
from .teacher import TeacherModel, build_teacher

__all__ = [
    "DistillationLoss",
    "TeacherModel",
    "action_kl_loss",
    "build_teacher",
    "distillation_step",
    "feature_alignment_loss",
]
