"""6D pose (position + quaternion)."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Pose6D:
    position: list[float]   # [x, y, z]
    orientation: list[float]  # quaternion [w, x, y, z]

    def to_dict(self) -> dict:
        return {"position": list(self.position), "orientation": list(self.orientation)}
