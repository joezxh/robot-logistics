"""Environment configuration catalog (RCS parity: FR3/Panda/UR5e/XArm7/SO-101/Yam).

P2.3 deliverable: a full roster of pre-built ``SimEnvCreatorConfig`` entries keyed
by stable names, mirroring ``robot-control-stack.rcs.envs.configs``.

Unlike RCS (which encodes per-robot joint/actuator lists in a ``ROBOTS`` registry),
robot-logic's :class:`MuJoCoEngine` auto-detects arm joints / base / TCP site from
the MJCF at load time, so configs here only need the asset path + ``RobotType``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Callable

from robot_contracts import RobotType

from .base import SimEnv
from .composer import EnvConfig, RobotSpec
from .creator import SimEnvCreatorConfig
from ..engine import EngineConfig

# Absolute assets root: <rcs_env>/../assets
_ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
_ROBOTS_DIR = os.path.join(_ASSETS_DIR, "robots")


@dataclass
class RobotAsset:
    """Static description of a robot asset."""

    name: str
    mjcf: str  # relative to assets/robots
    robot_type: RobotType
    has_gripper: bool = True


# Full robot roster (assets present in assets/robots/<type>/<type>.xml)
ROBOT_ASSETS: dict[str, RobotAsset] = {
    "fr3": RobotAsset("fr3", "fr3/fr3.xml", RobotType.FR3, has_gripper=True),
    "panda": RobotAsset("panda", "panda/panda.xml", RobotType.PANDA, has_gripper=True),
    "ur5e": RobotAsset("ur5e", "ur5e/ur5e.xml", RobotType.UR5E, has_gripper=True),
    "xarm7": RobotAsset("xarm7", "xarm7/xarm7.xml", RobotType.XARM7, has_gripper=False),
    "so101": RobotAsset("so101", "so101/so101.xml", RobotType.SO101, has_gripper=True),
    "yam": RobotAsset("yam", "yam/yam.xml", RobotType.YAM, has_gripper=True),
}

# Logistics robots (fall back to arm config; LogicEngine path exists in RCS)
LOGISTICS_ASSETS: dict[str, RobotAsset] = {
    "agv": RobotAsset("agv", "agv/agv.xml", RobotType.AGV, has_gripper=False),
    "stacker": RobotAsset("stacker", "stacker/stacker.xml", RobotType.STACKER, has_gripper=False),
}

GRIPPER_ASSETS: dict[str, str] = {
    "franka_hand": os.path.join(_ASSETS_DIR, "grippers", "franka_hand.xml"),
    "robotiq_2f85": os.path.join(_ASSETS_DIR, "grippers", "robotiq_2f85.xml"),
}

_ALL_ASSETS = {**ROBOT_ASSETS, **LOGISTICS_ASSETS}


def _resolve(name: str) -> RobotAsset:
    if name not in _ALL_ASSETS:
        raise KeyError(f"Unknown robot asset '{name}'. Known: {sorted(_ALL_ASSETS)}")
    return _ALL_ASSETS[name]


def _creator_config(
    name: str,
    *,
    logic_device_id: str | None = None,
    planner: str = "RRTConnect",
    dt: float = 0.002,
    wrappers: list[Callable[[SimEnv], SimEnv]] | None = None,
    render_mode: str | None = None,
) -> SimEnvCreatorConfig:
    asset = _resolve(name)
    mjcf = os.path.join(_ROBOTS_DIR, asset.mjcf)
    cfg = EngineConfig(
        robot_type=asset.robot_type,
        mjcf_path=mjcf,
        dt=dt,
    )
    return SimEnvCreatorConfig(
        robot_type=asset.robot_type,
        mjcf_path=mjcf,
        logic_device_id=logic_device_id,
        planner=planner,  # type: ignore[arg-type]
        dt=dt,
        render_mode=render_mode,
        has_gripper=asset.has_gripper,
        wrappers=wrappers or [],
    )


# Per-robot SimEnvCreatorConfig factories (stable names -> config)
def fr3(**kw) -> SimEnvCreatorConfig:
    return _creator_config("fr3", **kw)

def panda(**kw) -> SimEnvCreatorConfig:
    return _creator_config("panda", **kw)

def ur5e(**kw) -> SimEnvCreatorConfig:
    return _creator_config("ur5e", **kw)

def xarm7(**kw) -> SimEnvCreatorConfig:
    return _creator_config("xarm7", **kw)

def so101(**kw) -> SimEnvCreatorConfig:
    return _creator_config("so101", **kw)

def yam(**kw) -> SimEnvCreatorConfig:
    return _creator_config("yam", **kw)

def agv(**kw) -> SimEnvCreatorConfig:
    return _creator_config("agv", **kw)

def stacker(**kw) -> SimEnvCreatorConfig:
    return _creator_config("stacker", **kw)


# Registry: name -> factory
ENV_FACTORIES: dict[str, Callable[..., SimEnvCreatorConfig]] = {
    "fr3": fr3,
    "panda": panda,
    "ur5e": ur5e,
    "xarm7": xarm7,
    "so101": so101,
    "yam": yam,
    "agv": agv,
    "stacker": stacker,
}

# Flat registry: name -> SimEnvCreatorConfig (built with defaults)
CONFIGS: dict[str, SimEnvCreatorConfig] = {name: f() for name, f in ENV_FACTORIES.items()}


def get_config(name: str, **kw) -> SimEnvCreatorConfig:
    """Return a :class:`SimEnvCreatorConfig` for a named environment."""
    if name in ENV_FACTORIES:
        return ENV_FACTORIES[name](**kw)
    return _creator_config(name, **kw)


__all__ = [
    "RobotAsset", "ROBOT_ASSETS", "LOGISTICS_ASSETS", "GRIPPER_ASSETS",
    "ENV_FACTORIES", "CONFIGS", "get_config", "fr3", "panda", "ur5e",
    "xarm7", "so101", "yam", "agv", "stacker",
]
