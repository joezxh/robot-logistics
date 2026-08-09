from __future__ import annotations

import numpy as np

from .foundation import Trajectory, TrajectoryPoint


class TrajectoryOptimizer:
    def optimize(self, trajectory: Trajectory, iterations: int = 20) -> Trajectory:
        if len(trajectory.points) < 3:
            return trajectory
        positions = np.stack([point.positions for point in trajectory.points])
        for _ in range(iterations):
            positions[1:-1] = 0.25 * positions[:-2] + 0.5 * positions[1:-1] + 0.25 * positions[2:]
        points = [
            TrajectoryPoint(position.copy(), time_from_start=source.time_from_start)
            for position, source in zip(positions, trajectory.points)
        ]
        return Trajectory(trajectory.joint_names, points)
