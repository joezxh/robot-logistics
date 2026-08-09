"""Base (AGV) executor for waypoint following."""
from __future__ import annotations

from enum import Enum, auto


class BaseState(Enum):
    IDLE = auto()
    FOLLOWING = auto()
    STOPPED = auto()


class BaseExecutor:
    """Executes waypoint following for the diff-drive base."""

    def __init__(self) -> None:
        self._state = BaseState.IDLE
        self._target_x = 0.0
        self._target_y = 0.0
        self._target_yaw = 0.0

    @property
    def state(self) -> BaseState:
        return self._state

    def follow_waypoint(self, x: float, y: float, yaw: float) -> None:
        self._target_x = x
        self._target_y = y
        self._target_yaw = yaw
        self._state = BaseState.FOLLOWING

    def stop(self) -> None:
        self._state = BaseState.STOPPED

    def get_cmd_vel(self) -> tuple[float, float]:
        """Return (vx, wz) velocity command. Zero when stopped or idle."""
        if self._state != BaseState.FOLLOWING:
            return (0.0, 0.0)
        # Simple P-controller placeholder (real impl uses /odom feedback)
        return (0.0, 0.0)

    def complete_follow(self) -> None:
        self._state = BaseState.IDLE
