"""Hardware extension registry — mirrors ``robot-control-stack``'s ``extensions/`` pattern.

In RCS each robot (fr3, panda, ur5e, xarm7, so100, so101, yam) and each sensor
(realsense, zed, robotiq2f85, tacto, taxim) is an *independent pip package* that
registers itself with the core. We replicate that with a lightweight entry-point
registry so logistics devices (container_robot, loading_robot, agv, stacker,
pallet_forklift) and future real hardware can plug into ``simulation`` the same
way, without modifying core code.

Extension contract (each extension implements ``Extension``):
    * ``robot_type`` / ``device_type`` key
    * ``mjcf_path`` (optional, for MuJoCo models)
    * ``build_engine_config()`` -> EngineConfig
    * ``make_robot()`` / ``make_sensor()`` factories
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from robot_contracts import RobotType

from ..engine import EngineConfig


@dataclass
class Extension:
    """A registered hardware/sensor extension (RCS extension package parity)."""

    key: str
    kind: str  # "robot" | "sensor"
    robot_type: RobotType | None = None
    device_type: str | None = None
    mjcf_path: str | None = None
    build_engine_config: Callable[[], EngineConfig] | None = None
    make: Callable[..., object] | None = None
    meta: dict = None  # type: ignore[assignment]


_REGISTRY: dict[str, Extension] = {}


def register(ext: Extension) -> Extension:
    """Register an extension (called at package import time, RCS pattern)."""
    if ext.key in _REGISTRY:
        raise ValueError(f"extension {ext.key!r} already registered")
    _REGISTRY[ext.key] = ext
    return ext


def get(key: str) -> Extension:
    if key not in _REGISTRY:
        raise KeyError(f"unknown extension {key!r}; available: {sorted(_REGISTRY)}")
    return _REGISTRY[key]


def all_extensions() -> list[Extension]:
    return list(_REGISTRY.values())


def available_robots() -> list[Extension]:
    return [e for e in _REGISTRY.values() if e.kind == "robot"]


def available_sensors() -> list[Extension]:
    return [e for e in _REGISTRY.values() if e.kind == "sensor"]


# ---- built-in logistics extensions (RCS stock-arm parity) ------------------- #
def _register_builtins() -> None:
    register(Extension("container_robot", "robot", RobotType.ARM, "container_robot",
                       build_engine_config=lambda: EngineConfig(robot_type=RobotType.ARM, logic_device_id="robot-01")))
    register(Extension("loading_robot", "robot", RobotType.ARM, "loading_robot",
                       build_engine_config=lambda: EngineConfig(robot_type=RobotType.ARM, logic_device_id="loader-01")))
    register(Extension("agv", "robot", RobotType.AGV, "agv",
                       build_engine_config=lambda: EngineConfig(robot_type=RobotType.AGV, logic_device_id="agv-01")))
    register(Extension("stacker", "robot", RobotType.STACKER, "stacker",
                       build_engine_config=lambda: EngineConfig(robot_type=RobotType.STACKER, logic_device_id="stacker-01")))
    register(Extension("pallet_forklift", "robot", RobotType.AGV, "pallet_forklift",
                       build_engine_config=lambda: EngineConfig(robot_type=RobotType.AGV, logic_device_id="forklift-01")))
    register(Extension("realsense_rgbd", "sensor", mjcf_path=None,
                       make=lambda: {"type": "rgbd", "resolution": (480, 640)}))
    register(Extension("robotiq_2f85", "sensor", RobotType.UR5E and None, "gripper",
                       make=lambda: {"type": "gripper", "fingers": 2}))


_register_builtins()


__all__ = [
    "Extension",
    "register",
    "get",
    "all_extensions",
    "available_robots",
    "available_sensors",
]
