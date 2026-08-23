"""RCS-aligned task / inference / teleop layer for robot-app.

Mirrors ``robot-control-stack``'s ``examples/`` (teleop, inference, imitation):
* :mod:`rcs_layer.tasks`   — logistics tasks as RCS ``TaskWrapper``-compatible objects
* :mod:`rcs_layer.vla`     — policy inference (RCS ``inference`` parity)
* :mod:`rcs_layer.teleop`  — expert input adapters (RCS ``teleop`` parity)

These run as the *execution* edge of the stack: they consume observations from the
``simulation`` Gym env and produce actions, whether those actions come from a
learned VLA policy (trained by ``vla-training``) or a human teleoperator.
"""
from __future__ import annotations

from .tasks import get_task, TASK_REGISTRY
from .vla import load_policy, Policy
from .teleop import TeleopInput, KeyboardAdapter

__all__ = [
    "get_task",
    "TASK_REGISTRY",
    "load_policy",
    "Policy",
    "TeleopInput",
    "KeyboardAdapter",
]
