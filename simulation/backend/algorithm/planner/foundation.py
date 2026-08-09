from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np


@dataclass
class JointLimits:
    positions_lower: np.ndarray
    positions_upper: np.ndarray
    velocities: np.ndarray
    accelerations: np.ndarray
    efforts: np.ndarray

    def contains(self, positions: np.ndarray) -> bool:
        return bool(
            np.all(positions >= self.positions_lower)
            and np.all(positions <= self.positions_upper)
        )


@dataclass
class TrajectoryPoint:
    positions: np.ndarray
    velocities: np.ndarray = field(default_factory=lambda: np.array([]))
    accelerations: np.ndarray = field(default_factory=lambda: np.array([]))
    time_from_start: float = 0.0


@dataclass
class Trajectory:
    joint_names: List[str]
    points: List[TrajectoryPoint]

    @property
    def num_joints(self) -> int:
        return len(self.joint_names)

    def get_duration(self) -> float:
        return self.points[-1].time_from_start if self.points else 0.0

    def sample(self, time: float) -> np.ndarray:
        if not self.points:
            raise ValueError("trajectory is empty")
        if time <= self.points[0].time_from_start:
            return self.points[0].positions
        if time >= self.points[-1].time_from_start:
            return self.points[-1].positions
        for first, second in zip(self.points, self.points[1:]):
            if first.time_from_start <= time <= second.time_from_start:
                span = second.time_from_start - first.time_from_start
                alpha = (time - first.time_from_start) / span
                return (1 - alpha) * first.positions + alpha * second.positions
        return self.points[-1].positions
