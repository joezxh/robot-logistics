from __future__ import annotations

import numpy as np

from .foundation import Trajectory, TrajectoryPoint


class TrajectoryInterpolator:
    def interpolate(
        self,
        trajectory: Trajectory,
        frequency_hz: int = 20,
        mode: str = "s_curve",
    ) -> Trajectory:
        if len(trajectory.points) < 2:
            return trajectory
        duration = max(trajectory.get_duration(), 0.001)
        count = max(2, int(duration * frequency_hz) + 1)
        points = []
        for time in np.linspace(0.0, duration, count):
            progress = time / duration
            eased = progress * progress * (3.0 - 2.0 * progress) if mode == "s_curve" else progress
            source_time = eased * duration
            points.append(TrajectoryPoint(trajectory.sample(source_time), time_from_start=float(time)))
        return Trajectory(trajectory.joint_names, points)
