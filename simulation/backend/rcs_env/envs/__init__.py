"""RCS-aligned Gymnasium environment stack (mirrors ``robot-control-stack.rcs.envs``).

Public surface:
    * :class:`SimEnv` — the base Gym env over a :class:`PhysicsEngine`.
    * :class:`SimEnvCreator` / :class:`SimEnvCreatorConfig` — factory (RCS parity).
    * :mod:`rcs_env.envs.configs` — scene configs (RCS ``configs.py``).
    * :mod:`rcs_env.envs.scenes` — scene presets (RCS ``scenes.py``).
    * wrappers: RobotWrapper / GripperWrapper / CameraSetWrapper / TaskWrapper.
"""
from __future__ import annotations

from .base import SimEnv
from .creator import SimEnvCreator, SimEnvCreatorConfig
from .wrappers import CameraSetWrapper, GripperWrapper, RobotWrapper, TaskWrapper

__all__ = [
    "SimEnv",
    "SimEnvCreator",
    "SimEnvCreatorConfig",
    "RobotWrapper",
    "GripperWrapper",
    "CameraSetWrapper",
    "TaskWrapper",
]
