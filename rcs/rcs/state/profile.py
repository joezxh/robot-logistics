"""Per-device static profile."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Morphology(str, Enum):
    ARM = "arm"
    AGV = "agv"
    STACKER = "stacker"


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

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "morphology": self.morphology.value,
            "num_joints": self.num_joints,
            "control_hz": self.control_hz,
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
