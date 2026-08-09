"""Single-arm MoveIt executor."""
from __future__ import annotations

from enum import Enum, auto
from typing import Any


class ArmState(Enum):
    IDLE = auto()
    PLANNING = auto()
    EXECUTING = auto()
    ERROR = auto()


class ArmExecutor:
    """Plans and executes single-arm motions via MoveIt."""

    def __init__(self, arm_id: str) -> None:
        self._arm_id = arm_id
        self._state = ArmState.IDLE

    @property
    def arm_id(self) -> str:
        return self._arm_id

    @property
    def state(self) -> ArmState:
        return self._state

    def plan_and_execute(self, target_joints: list[float]) -> None:
        self._state = ArmState.PLANNING
        # Placeholder: real impl calls MoveIt action
        # /{arm_id}_arm_controller/follow_joint_trajectory

    def cancel(self) -> None:
        self._state = ArmState.IDLE

    def complete_plan(self) -> None:
        self._state = ArmState.EXECUTING

    def complete_execution(self) -> None:
        self._state = ArmState.IDLE

    def set_error(self) -> None:
        self._state = ArmState.ERROR
