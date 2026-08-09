"""Task coordinator FSM for dual-arm AGV loading robot."""
from __future__ import annotations

from enum import Enum, auto
from typing import Any


class CoordinationPhase(Enum):
    IDLE = auto()
    NAVIGATING = auto()
    DOCKING = auto()
    APPROACHING = auto()
    HUGGING = auto()
    LIFTING = auto()
    TRANSPORTING = auto()
    PLACING = auto()
    RETREATING = auto()
    ABORTING = auto()


# Task type -> initial phase mapping
_TASK_PHASE_MAP: dict[str, CoordinationPhase] = {
    "goto": CoordinationPhase.NAVIGATING,
    "dock": CoordinationPhase.DOCKING,
    "pick_box": CoordinationPhase.APPROACHING,
    "place_box": CoordinationPhase.PLACING,
    "transport": CoordinationPhase.TRANSPORTING,
    "hug_close": CoordinationPhase.HUGGING,
    "hug_release": CoordinationPhase.RETREATING,
    "home_all": CoordinationPhase.RETREATING,
}


class TaskCoordinator:
    """Layered FSM coordinating base + dual-arm + hug grasp."""

    def __init__(self) -> None:
        self._phase = CoordinationPhase.IDLE
        self._current_task: str | None = None
        self._abort_reason: str | None = None

    @property
    def phase(self) -> CoordinationPhase:
        return self._phase

    def execute_task(self, task_type: str, parameters: dict[str, Any]) -> None:
        """Start a new task. Transitions FSM to the appropriate initial phase."""
        if task_type not in _TASK_PHASE_MAP:
            raise ValueError(f"unknown task_type: {task_type}")
        self._current_task = task_type
        self._phase = _TASK_PHASE_MAP[task_type]

    def advance_phase(self, next_phase: CoordinationPhase) -> None:
        """Advance to the next phase (called by sub-executors on completion)."""
        self._phase = next_phase

    def complete_task(self) -> None:
        """Mark current task as complete, return to IDLE."""
        self._phase = CoordinationPhase.IDLE
        self._current_task = None

    def abort(self, reason: str) -> None:
        """Abort from any phase."""
        self._abort_reason = reason
        self._phase = CoordinationPhase.ABORTING

    def complete_abort(self) -> None:
        """Complete abort, return to IDLE."""
        self._phase = CoordinationPhase.IDLE
        self._current_task = None
        self._abort_reason = None
