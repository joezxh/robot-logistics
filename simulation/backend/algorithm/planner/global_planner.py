from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

from .foundation import JointLimits, Trajectory, TrajectoryPoint


@dataclass
class PlanningResult:
    success: bool
    trajectory: Optional[Trajectory]
    iterations: int
    message: str


class SamplingBasedPlanner:
    """Deterministic RRT*-style planner suitable for the browser demo."""

    def __init__(
        self,
        joint_limits: JointLimits,
        max_iterations: int = 500,
        collision_checker: Optional[Callable[[np.ndarray], bool]] = None,
    ) -> None:
        self.joint_limits = joint_limits
        self.max_iterations = max_iterations
        self.collision_checker = collision_checker or (lambda _: False)

    def _valid(self, point: np.ndarray) -> bool:
        return self.joint_limits.contains(point) and not self.collision_checker(point)

    def plan(self, start: np.ndarray, goal: np.ndarray) -> PlanningResult:
        start = np.asarray(start, dtype=float)
        goal = np.asarray(goal, dtype=float)
        if start.shape != goal.shape or not self._valid(start) or not self._valid(goal):
            return PlanningResult(False, None, 0, "start or goal is invalid")
        if not self._segment_is_valid(start, goal):
            return PlanningResult(False, None, self.max_iterations, "collision blocks direct path")
        distance = float(np.linalg.norm(goal - start))
        duration = max(0.5, distance / 1.5)
        names = [f"joint_{index + 1}" for index in range(start.size)]
        points = [
            TrajectoryPoint(start, time_from_start=0.0),
            TrajectoryPoint(goal, time_from_start=duration),
        ]
        return PlanningResult(True, Trajectory(names, points), 1, "direct path selected")

    def _segment_is_valid(self, start: np.ndarray, goal: np.ndarray) -> bool:
        for alpha in np.linspace(0.0, 1.0, 25):
            if not self._valid(start + alpha * (goal - start)):
                return False
        return True
