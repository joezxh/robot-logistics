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

# NOTE: ``envs`` / ``extensions`` pull in the GL-backed renderer (MuJoCo offscreen
# rendering) and gymnasium, which are not needed for headless physics + planning.
# They are imported lazily so that ``import rcs_env`` (and anything that only needs
# the engine/planner, e.g. CI on a headless box) does not require an OpenGL context.
def __getattr__(name: str):  # Python 3.7+ module-level lazy import
    if name in {
        "SimEnv", "SimEnvCreator", "SimEnvCreatorConfig",
        "RobotWrapper", "GripperWrapper", "CameraSetWrapper", "TaskWrapper",
        "ModelComposer", "EnvConfig",
        "CONFIGS", "get_config", "SCENES", "get_scene",
        "register", "get_extension", "all_extensions",
    }:
        import importlib

        mods = {
            "SimEnv": "rcs_env.envs",
            "SimEnvCreator": "rcs_env.envs",
            "SimEnvCreatorConfig": "rcs_env.envs",
            "RobotWrapper": "rcs_env.envs",
            "GripperWrapper": "rcs_env.envs",
            "CameraSetWrapper": "rcs_env.envs",
            "TaskWrapper": "rcs_env.envs",
            "ModelComposer": "rcs_env.envs.composer",
            "EnvConfig": "rcs_env.envs.composer",
            "CONFIGS": "rcs_env.envs.configs",
            "get_config": "rcs_env.envs.configs",
            "SCENES": "rcs_env.envs.scenes",
            "get_scene": "rcs_env.envs.scenes",
            "register": "rcs_env.extensions",
            "get_extension": "rcs_env.extensions",
            "all_extensions": "rcs_env.extensions",
        }
        module = importlib.import_module(mods[name])
        return getattr(module, name)
    raise AttributeError(f"module 'rcs_env' has no attribute {name!r}")


__all__ = [
    "EngineConfig", "PhysicsEngine", "LogicEngine", "MuJoCoEngine", "build_engine",
    "MjOMPL", "Planner",
    "SimEnv", "SimEnvCreator", "SimEnvCreatorConfig",
    "RobotWrapper", "GripperWrapper", "CameraSetWrapper", "TaskWrapper",
    "ModelComposer", "EnvConfig",
    "CONFIGS", "get_config", "SCENES", "get_scene",
    "register", "get_extension", "all_extensions",
]
