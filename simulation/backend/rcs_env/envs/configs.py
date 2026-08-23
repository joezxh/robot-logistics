"""Scene / robot configs — mirrors ``robot-control-stack.rcs.envs.configs``.

Each config names a (robot_type, mjcf or logic device, planner) combination so
downstream code can request an environment by a stable string key, exactly like
RCS ``EmptyWorldFR3`` etc.
"""
from __future__ import annotations

from dataclasses import dataclass

from robot_contracts import RobotType

from ..ompl import Planner


@dataclass(frozen=True)
class EnvConfig:
    name: str
    robot_type: RobotType
    mjcf_path: str | None = None
    logic_device_id: str | None = None
    planner: Planner = Planner.RRTConnect
    has_camera: bool = False
    has_gripper: bool = True


# robot-logic logistics scenes ------------------------------------------------- #
LOGISTICS_ARM = EnvConfig("LogisticsArm", RobotType.ARM, logic_device_id="robot-01", has_gripper=True)
LOGISTICS_AGV = EnvConfig("LogisticsAGV", RobotType.AGV, logic_device_id="agv-01")
LOGISTICS_STACKER = EnvConfig("LogisticsStacker", RobotType.STACKER, logic_device_id="stacker-01")
LOGISTICS_ARM_CAM = EnvConfig("LogisticsArmCam", RobotType.ARM, logic_device_id="robot-01", has_camera=True)

# RCS stock arms (require mjcf_path + mujoco) --------------------------------- #
FR3_EMPTY = EnvConfig("EmptyWorldFR3", RobotType.FR3, mjcf_path="fr3.xml")
PANDA_EMPTY = EnvConfig("EmptyWorldPanda", RobotType.PANDA, mjcf_path="panda.xml")
UR5E_EMPTY = EnvConfig("EmptyWorldUR5e", RobotType.UR5E, mjcf_path="ur5e.xml")


CONFIGS: dict[str, EnvConfig] = {
    c.name: c
    for c in (
        LOGISTICS_ARM, LOGISTICS_AGV, LOGISTICS_STACKER, LOGISTICS_ARM_CAM,
        FR3_EMPTY, PANDA_EMPTY, UR5E_EMPTY,
    )
}


def get_config(name: str) -> EnvConfig:
    if name not in CONFIGS:
        raise KeyError(f"unknown env config {name!r}; available: {sorted(CONFIGS)}")
    return CONFIGS[name]


__all__ = ["EnvConfig", "CONFIGS", "get_config"]
