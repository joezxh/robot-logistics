"""Dual-arm trajectory optimizer (simplified CHOMP)."""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass


@dataclass
class JointTrajectory:
    left_arm: list[list[float]]    # [step][6 joints]
    right_arm: list[list[float]]   # [step][6 joints]
    duration_s: float


class DualArmOptimizer:
    """Simplified CHOMP: smooth each arm trajectory with sync constraint.

    Real CHOMP is iterative gradient descent; here we approximate with a
    5-tap smoothing kernel and a sync-correction pass.
    """

    def __init__(self, num_steps: int = 50, sync_tolerance_m: float = 0.003) -> None:
        self.num_steps = num_steps
        self.sync_tolerance = sync_tolerance_m

    def optimize(
        self,
        left_target: list[float],
        right_target: list[float],
    ) -> JointTrajectory:
        # Linear interpolation as initial trajectory
        left = [
            [left_target[i] * t / self.num_steps for i in range(6)]
            for t in range(self.num_steps + 1)
        ]
        right = [
            [right_target[i] * t / self.num_steps for i in range(6)]
            for t in range(self.num_steps + 1)
        ]
        # Apply 5-tap smoothing (simplified CHOMP step)
        kernel = np.array([1, 4, 6, 4, 1], dtype=float) / 16.0
        for arm in (left, right):
            for joint in range(6):
                vals = np.array([step[joint] for step in arm])
                smoothed = np.convolve(vals, kernel, mode="same")
                for step_idx, step in enumerate(arm):
                    step[joint] = float(smoothed[step_idx])
        # Sync correction: align joint 0 of both arms
        for t_idx in range(len(left)):
            avg = (left[t_idx][0] + right[t_idx][0]) / 2.0
            left[t_idx][0] = avg
            right[t_idx][0] = avg
        return JointTrajectory(left_arm=left, right_arm=right, duration_s=self.num_steps / 50.0)