"""RCS-aligned simulation layer for robot-logic.

Mirrors ``robot-control-stack``'s ``python/rcs`` + ``extensions/``:
* :mod:`rcs_env.engine`   — physics-engine abstraction (MuJoCo / logic-sim)
* :mod:`rcs_env.ompl`     — OMPL-style planner (MjOMPL parity)
* :mod:`rcs_env.envs`     — Gymnasium env + SimEnvCreator + wrappers + scenes
* :mod:`rcs_env.extensions` — hardware/sensor extension registry

This layer is the integration point for the other three subprojects:
``rcs`` drives it as the unified control plane, ``robot-app`` binds tasks /
teleop / inference via the Gym env, and ``vla-training`` consumes its camera /
observation streams for imitation + RL.
"""
from __future__ import annotations

from .engine import EngineConfig, MuJoCoEngine, LogicEngine, PhysicsEngine, build_engine
from .ompl import MjOMPL, Planner
from .envs import (
    SimEnv,
    SimEnvCreator,
    SimEnvCreatorConfig,
    RobotWrapper,
    GripperWrapper,
    CameraSetWrapper,
    TaskWrapper,
)
from .envs.configs import CONFIGS, get_config
from .envs.scenes import SCENES, get_scene
from .extensions import register, get as get_extension, all_extensions

__all__ = [
    "EngineConfig", "PhysicsEngine", "LogicEngine", "MuJoCoEngine", "build_engine",
    "MjOMPL", "Planner",
    "SimEnv", "SimEnvCreator", "SimEnvCreatorConfig",
    "RobotWrapper", "GripperWrapper", "CameraSetWrapper", "TaskWrapper",
    "CONFIGS", "get_config", "SCENES", "get_scene",
    "register", "get_extension", "all_extensions",
]
