"""Base task contract (RCS ``TaskWrapper`` parity)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from robot_contracts import Pose, RobotType


@dataclass
class TaskResult:
    success: bool
    final_state: str
    elapsed_s: float
    completed_stages: tuple[str, ...] = field(default_factory=tuple)
    error: str | None = None


class LogisticsTask:
    """Base class for all robot-app logistics tasks.

    Implements the RCS ``Task`` protocol consumed by
    ``simulation.rcs_env.envs.wrappers.TaskWrapper``. Subclasses wrap a concrete
    FSM executor and translate env ``info`` (EE pose, joints) into task progress.
    """

    name: str = "logistics"
    robot_type: RobotType = RobotType.ARM

    def reset(self) -> None:  # pragma: no cover - overridden
        """Reset the underlying executor to its initial state."""

    def reward(self, info: dict) -> float:
        """Return a scalar reward for the current step."""
        return 0.0

    def done(self, info: dict) -> bool:
        """Return True when the task is finished (success or failure)."""
        return False

    def progress(self, info: dict) -> float:
        """Optional 0..1 progress indicator for monitoring."""
        return 0.0
