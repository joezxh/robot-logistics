"""Tracking error reported by the controller each tick."""
from __future__ import annotations
from dataclasses import dataclass
import time


@dataclass
class TrackingError:
    max_joint_error: float
    position_error_m: float
    timestamp_ns: int = 0

    def __post_init__(self) -> None:
        if self.timestamp_ns == 0:
            self.timestamp_ns = time.monotonic_ns()

    def to_dict(self) -> dict:
        return {
            "max_joint_error": self.max_joint_error,
            "position_error_m": self.position_error_m,
            "timestamp_ns": self.timestamp_ns,
        }
