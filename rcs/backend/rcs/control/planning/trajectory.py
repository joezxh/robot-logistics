"""Joint-space trajectory planning: trapezoidal and quintic time-optimal scaling."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Trajectory:
    q_start: list[float]
    q_goal: list[float]
    duration_s: float
    profile: str  # "trapezoidal" | "quintic"
    vel_max: list[float]
    acc_max: list[float]

    def sample(self, t: float) -> list[float]:
        t = max(0.0, min(self.duration_s, t))
        s = self._scalar(t / self.duration_s)
        return [a + (b - a) * s for a, b in zip(self.q_start, self.q_goal)]

    def _scalar(self, s: float) -> float:
        if self.profile == "trapezoidal":
            return _trapezoidal_scalar(s)
        return _quintic_scalar(s)


def _trapezoidal_scalar(s: float) -> float:
    # Symmetric trapezoid on s in [0, 1] with three phases:
    #   s in [0, 0.25]:  acceleration, y goes 0 -> 0.125 (y' = 4s)
    #   s in [0.25, 0.75]:  cruise, y goes 0.125 -> 0.625 (y' = 1)
    #   s in [0.75, 1]:  deceleration, y goes 0.625 -> 1.0 (y' = 1 + 4(s-0.75))
    # Continuous at s=0.25 and s=0.75; the cruise-phase slope (1.0) is
    # matched at both ends.
    if s < 0.25:
        return 2.0 * s * s
    if s < 0.75:
        return 0.125 + (s - 0.25)
    u = s - 0.75
    return 0.625 + u + 2.0 * u * u


def _quintic_scalar(s: float) -> float:
    # s^3 * (6s^2 - 15s + 10) — C2-continuous, zero velocity at endpoints.
    return s * s * s * (6.0 * s * s - 15.0 * s + 10.0)


def _axis_duration(dq: float, vmax: float, amax: float) -> float:
    if abs(dq) < 1e-9:
        return 0.0
    t_accel = vmax / amax
    d_accel = 0.5 * amax * t_accel * t_accel
    if 2 * d_accel >= abs(dq):
        # Triangle profile (no cruise).
        return 2.0 * math.sqrt(abs(dq) / amax)
    d_cruise = abs(dq) - 2 * d_accel
    return 2 * t_accel + d_cruise / vmax


import math  # noqa: E402  (kept after dataclass to keep public surface clean)


def _plan(q_start, q_goal, vel_max, acc_max, profile: str) -> Trajectory:
    duration = 0.0
    for qs, qg, vm, am in zip(q_start, q_goal, vel_max, acc_max):
        d = _axis_duration(qg - qs, vm, am)
        if d > duration:
            duration = d
    if duration < 1e-9:
        duration = 1e-3
    return Trajectory(
        q_start=list(q_start),
        q_goal=list(q_goal),
        duration_s=duration,
        profile=profile,
        vel_max=list(vel_max),
        acc_max=list(acc_max),
    )


def plan_trapezoidal(q_start, q_goal, vel_max, acc_max) -> Trajectory:
    return _plan(q_start, q_goal, vel_max, acc_max, "trapezoidal")


def plan_quintic(q_start, q_goal, vel_max, acc_max) -> Trajectory:
    return _plan(q_start, q_goal, vel_max, acc_max, "quintic")
