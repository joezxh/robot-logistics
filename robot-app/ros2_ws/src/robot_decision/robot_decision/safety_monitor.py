"""Safety monitor for independent safety interlocks."""
from __future__ import annotations

from enum import Enum, auto


class SafetyState(Enum):
    SAFE = auto()
    SLOWDOWN = auto()
    EMERGENCY = auto()


class SafetyMonitor:
    """Independent safety monitor — bypasses the task coordinator."""

    SLOWDOWN_DISTANCE = 0.5  # metres
    STOP_DISTANCE = 0.2  # metres

    def __init__(self) -> None:
        self._state = SafetyState.SAFE
        self._estop_active = False

    @property
    def state(self) -> SafetyState:
        return self._state

    def trigger_estop(self) -> None:
        self._estop_active = True
        self._state = SafetyState.EMERGENCY

    def reset_estop(self) -> None:
        self._estop_active = False
        self._state = SafetyState.SAFE

    def update_scan(self, min_distance: float) -> None:
        if self._estop_active:
            return
        if min_distance < self.STOP_DISTANCE:
            self._state = SafetyState.EMERGENCY
        elif min_distance < self.SLOWDOWN_DISTANCE:
            self._state = SafetyState.SLOWDOWN
        else:
            self._state = SafetyState.SAFE

    def is_cmd_vel_allowed(self) -> bool:
        return self._state == SafetyState.SAFE

    def is_trajectory_allowed(self) -> bool:
        """Arms can continue current trajectory unless estop."""
        return not self._estop_active
