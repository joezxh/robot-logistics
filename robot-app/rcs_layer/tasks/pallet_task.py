"""Pallet task — wraps ``PalletTaskExecutor`` FSM as an RCS ``Task``.

The FSM executor (``robot_decision.pallet_task_executor``) is imported lazily so
this module works in unit tests without ROS2 / rclpy. When the ROS2 stack is not
available (e.g. in the simulation / vla-training integration loop), a built-in
pure-Python ``_ScriptedExecutor`` fallback is used so the task is still runnable
end-to-end in the Gym env — mirroring how RCS tasks run both in sim and on real HW.
"""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from robot_contracts import Pose, RobotType

from .base import LogisticsTask, TaskResult


class _ScriptedExecutor:
    """Pure-Python stand-in for ``PalletTaskExecutor``.

    Replicates the minimal state machine the task needs (approach -> engage ->
    lift -> transfer -> place -> idle) without ROS2, so a pallet task can be
    driven inside the simulation environment.
    """

    STATES = ["approach", "engage", "lift", "transfer", "place", "idle"]

    def __init__(self):
        self.state = "approach"
        self._failed = False

    def start_task(self, params=None) -> None:
        self.state = "approach"
        self._failed = False

    def advance(self) -> None:
        i = self.STATES.index(self.state)
        if i < len(self.STATES) - 1:
            self.state = self.STATES[i + 1]


class PalletTask(LogisticsTask):
    name = "pallet"
    robot_type = RobotType.ARM

    def __init__(self, executor: Any = None) -> None:
        self._exec = executor
        self._started = False
        self._started_at = 0.0
        self._completed: tuple[str, ...] = ()
        self._failed = False
        self._target_ee = Pose.from_keywords(x=5.0, y=0.0, z=2.0)  # pallet approach setpoint

    # ---- RCS Task protocol ------------------------------------------------- #
    def reset(self) -> None:
        if self._exec is None:
            # Prefer the ROS2 FSM executor when available; fall back to the
            # built-in scripted executor so the task runs in sim without ROS2.
            try:
                from robot_decision.pallet_task_executor import PalletTaskExecutor

                self._exec = PalletTaskExecutor(planner=None)
            except Exception:
                self._exec = _ScriptedExecutor()
        self._exec.start_task({"pallet_x": 5.0, "pallet_z": 2.0})
        self._started = True
        self._started_at = time.monotonic()
        self._completed = ("approach",)
        self._failed = False

    def reward(self, info: dict) -> float:
        """Shaped reward: EE proximity to the current pallet setpoint + staged progress."""
        if self._exec is None:
            return 0.0
        ee: Pose = info.get("ee_pose")
        if ee is None:
            return 0.0
        dist = float(np.linalg.norm(ee.translation - self._target_ee.translation))
        proximity = max(0.0, 1.0 - dist / 2.0)
        stage_bonus = len(self._completed) * 0.5
        return float(proximity + stage_bonus)

    def done(self, info: dict) -> bool:
        if self._exec is None or not self._started:
            return False
        if self._exec.state == "idle" and len(self._completed) > 1:
            return True  # full cycle completed
        return self._failed

    def progress(self, info: dict) -> float:
        return min(1.0, len(self._completed) / 5.0)

    def step_stage(self) -> None:
        """Advance the wrapped FSM by one stage (driven by an agent or a scripted loop)."""
        if self._exec is None:
            return
        prev_completed = len(self._completed)
        self._exec.advance()
        state = self._exec.state
        if state not in self._completed and state in ("approach", "engage", "lift", "transfer", "place"):
            self._completed = self._completed + (state,)
        if prev_completed == len(self._completed) and getattr(self._exec, "_failed", False):
            self._failed = True

    def result(self) -> TaskResult:
        return TaskResult(
            success=not self._failed and self._exec is not None,
            final_state=self._exec.state if self._exec else "idle",
            elapsed_s=(time.monotonic() - self._started_at) if self._started else 0.0,
            completed_stages=self._completed,
            error=None if not self._failed else "task failed",
        )


__all__ = ["PalletTask"]
