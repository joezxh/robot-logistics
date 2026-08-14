"""Dual-arm loading robot device model."""
from __future__ import annotations
from dataclasses import dataclass, field

from .base import DeviceModel


@dataclass
class DualArmLoaderSpec(DeviceModel):
    """Dual-arm loading robot with 6+6 joints and 2 gripper joints.

    Joints layout:
        0..5  †left arm (6 DOF)
        6..11 †right arm (6 DOF)
        12    †left gripper (0=open, 1=closed)
        13    †right gripper (0=open, 1=closed)
    """
    num_joints_per_arm: int = 6
    num_gripper_joints: int = 2
    payload_per_arm_kg: float = 30.0
    dual_arm_sync_tolerance_m: float = 0.003
    kp: float = 0.3  # match ArmController normalization
    kd: float = 0.5
    arm_pos_lower: list[float] = field(
        default_factory=lambda: [-3.14] * 6 + [-3.14] * 6 + [0.0, 0.0]
    )
    arm_pos_upper: list[float] = field(
        default_factory=lambda: [3.14] * 6 + [3.14] * 6 + [1.0, 1.0]
    )

    num_joints: int = 14
    home_joints: list[float] = field(default_factory=lambda: [0.0] * 14)

    def joint_limits(self) -> tuple[list[float], list[float]]:
        return (list(self.arm_pos_lower), list(self.arm_pos_upper))
