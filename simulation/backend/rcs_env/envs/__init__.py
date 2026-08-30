"""RCS-aligned Gymnasium environment stack (mirrors ``robot-control-stack.rcs.envs``).

Public surface:
    * :class:`SimEnv` — the base Gym env over a :class:`PhysicsEngine`.
    * :class:`SimEnvCreator` / :class:`SimEnvCreatorConfig` — factory (RCS parity).
    * :mod:`rcs_env.envs.configs` — scene configs (RCS ``configs.py``).
    * :mod:`rcs_env.envs.scenes` — scene presets (RCS ``scenes.py``).
    * :mod:`rcs_env.envs.wrappers` — Gripper/Hand/Storage/DigitalTwin wrappers (P3.2).
"""
from __future__ import annotations

from .base import SimEnv
from .creator import SimEnvCreator, SimEnvCreatorConfig
from .wrappers import (
    DigitalTwinWrapper,
    GripperWrapper,
    HandWrapper,
    StorageWrapper,
)
from .vec import make_vec_env, random_rollout, make_sb3_vec_env
from .twin import DigitalTwinSink, InMemoryTransport, MqttTransport, TwinRecord

__all__ = [
    "SimEnv",
    "SimEnvCreator",
    "SimEnvCreatorConfig",
    "GripperWrapper",
    "HandWrapper",
    "StorageWrapper",
    "DigitalTwinWrapper",
    "make_vec_env",
    "random_rollout",
    "make_sb3_vec_env",
    "DigitalTwinSink",
    "InMemoryTransport",
    "MqttTransport",
    "TwinRecord",
]
