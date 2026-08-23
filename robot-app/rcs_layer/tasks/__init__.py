"""RCS-aligned task layer for robot-app.

Mirrors ``robot-control-stack``'s ``examples/*`` + ``TaskWrapper`` protocol:
each logistics task is a ``Task`` object exposing ``reset()`` / ``reward(info)`` /
``done(info)`` so it can drive a ``simulation`` Gym env via
``rcs_env.envs.wrappers.TaskWrapper``.

The existing ROS2 FSM executors (``pallet_task_executor`` etc.) are wrapped — not
rewritten — so the proven logistics logic becomes a reinforcement/imitation
*objective* inside the simulated env, exactly as RCS binds its demos to Gym tasks.
"""
from __future__ import annotations

from .base import LogisticsTask, TaskResult
from .pallet_task import PalletTask
from .registry import TASK_REGISTRY, get_task, register_task

__all__ = [
    "LogisticsTask",
    "TaskResult",
    "PalletTask",
    "TASK_REGISTRY",
    "get_task",
    "register_task",
]
