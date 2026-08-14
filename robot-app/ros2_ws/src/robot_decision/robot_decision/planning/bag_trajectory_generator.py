"""Bag trajectory generator with anti-swing input shaping."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Trajectory:
    waypoints: list[tuple[float, float, float]]   # (x, y, z) at each time step
    duration_s: float


class BagTrajectoryGenerator:
    """Generates bag-carry trajectories with input shaping to suppress swing."""

    def __init__(self, num_steps: int = 50, swing_damping: float = 0.8) -> None:
        self.num_steps = num_steps
        self.swing_damping = swing_damping

    def generate(
        self,
        start: tuple[float, float, float],
        end: tuple[float, float, float],
        duration_s: float = 4.0,
    ) -> Trajectory:
        waypoints = []
        for t in range(self.num_steps + 1):
            tau = t / self.num_steps
            # Input shaping: zero-velocity-derivative profile
            smooth_tau = 3 * tau ** 2 - 2 * tau ** 3   # S-curve
            x = start[0] + (end[0] - start[0]) * smooth_tau
            y = start[1] + (end[1] - start[1]) * smooth_tau
            z = start[2] + (end[2] - start[2]) * smooth_tau
            waypoints.append((x, y, z))
        return Trajectory(waypoints=waypoints, duration_s=duration_s)