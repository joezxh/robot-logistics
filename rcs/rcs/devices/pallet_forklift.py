"""Forklift device model: 3 independent joints (travel/lift/extend)."""
from __future__ import annotations
from dataclasses import dataclass, field

from .base import DeviceModel


@dataclass
class ForkliftSpec(DeviceModel):
    """Forklift with 3 independent PID-controlled joints.

    Joints:
        0 †travel (m, ±travel_range_m)
        1 †lift   (m, 0..lift_range_m)
        2 †extend (m, 0..extend_range_m)
    """
    travel_range_m: float = 50.0
    lift_range_m: float = 3.0
    extend_range_m: float = 0.5
    payload_kg: float = 2000.0
    max_travel_speed_mps: float = 1.5
    max_lift_speed_mps: float = 0.3
    max_extend_speed_mps: float = 0.2
    kp_travel: float = 0.6
    kd_travel: float = 0.1
    kp_lift: float = 0.5
    kd_lift: float = 0.15
    kp_extend: float = 0.4
    kd_extend: float = 0.1

    num_joints: int = 3
    home_joints: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])

    def joint_limits(self) -> tuple[list[float], list[float]]:
        return (
            [-self.travel_range_m, 0.0, 0.0],
            [self.travel_range_m, self.lift_range_m, self.extend_range_m],
        )
