"""Per-device static profile.

RCS-aligned: each profile now also carries a ``RobotType`` (unifying the RCS stock
arm taxonomy with robot-logic's logistics morphologies) and a ``base_pose_in_world``
so the control layer can perform world<->robot frame conversions exactly like RCS
``MjORobot``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from robot_contracts import Pose, RobotType


class Morphology(str, Enum):
    ARM = "arm"
    AGV = "agv"
    STACKER = "stacker"

    def to_robot_type(self) -> RobotType:
        return {
            Morphology.ARM: RobotType.ARM,
            Morphology.AGV: RobotType.AGV,
            Morphology.STACKER: RobotType.STACKER,
        }[self]


@dataclass
class Limits:
    pos_lower: list[float] = field(default_factory=list)
    pos_upper: list[float] = field(default_factory=list)
    vel_max: list[float] = field(default_factory=list)
    acc_max: list[float] = field(default_factory=list)
    rad_th: float = 0.05
    pos_th: float = 0.01


@dataclass
class DeviceProfile:
    device_id: str
    morphology: Morphology
    num_joints: int
    control_hz: int
    limits: Limits = field(default_factory=Limits)
    home_joints: list[float] = field(default_factory=list)
    locked: bool = False
    extra: dict = field(default_factory=dict)
    # RCS alignment: typed robot taxonomy + world-frame base pose
    robot_type: RobotType | None = None
    base_pose_in_world: Pose | None = None

    def __post_init__(self) -> None:
        if self.robot_type is None:
            self.robot_type = self.morphology.to_robot_type()
        if self.base_pose_in_world is None:
            self.base_pose_in_world = Pose()  # identity: base at world origin

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "morphology": self.morphology.value,
            "robot_type": self.robot_type.value if self.robot_type else None,
            "num_joints": self.num_joints,
            "control_hz": self.control_hz,
            "base_pose_in_world": self.base_pose_in_world.to_dict() if self.base_pose_in_world else None,
            "limits": {
                "pos_lower": list(self.limits.pos_lower),
                "pos_upper": list(self.limits.pos_upper),
                "vel_max": list(self.limits.vel_max),
                "acc_max": list(self.limits.acc_max),
                "rad_th": self.limits.rad_th,
                "pos_th": self.limits.pos_th,
            },
            "home_joints": list(self.home_joints),
            "locked": self.locked,
        }
