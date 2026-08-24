"""Joint state snapshot read from HAL."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class JointState:
    positions: list[float]
    velocities: list[float]
    efforts: list[float]
    timestamp_ns: int = field(default_factory=time.monotonic_ns)
    device_id: str = ""

    def to_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "positions": list(self.positions),
            "velocities": list(self.velocities),
            "efforts": list(self.efforts),
            "timestamp_ns": self.timestamp_ns,
        }
