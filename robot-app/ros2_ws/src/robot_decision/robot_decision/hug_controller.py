"""Hug grasp controller for dual-arm coordinated manipulation."""
from __future__ import annotations

from enum import Enum, auto


class HugPhase(Enum):
    OPEN = auto()
    APPROACHING = auto()
    CLOSING = auto()
    HOLDING = auto()
    OPENING = auto()


class HugController:
    """Coordinates dual-arm hug grasp with force feedback."""

    def __init__(self, pressure_threshold: float = 45.0) -> None:
        self._phase = HugPhase.OPEN
        self._pressure_target = 50.0
        self._pressure_threshold = pressure_threshold

    @property
    def phase(self) -> HugPhase:
        return self._phase

    def approach(self, target_pose: dict) -> None:
        """Plan dual_arm MoveIt to hug starting pose."""
        self._phase = HugPhase.APPROACHING

    def close(self, pressure_target: float = 50.0,
              approach_speed: float = 0.2, close_speed: float = 0.05) -> None:
        """Start closing paddles with force control."""
        self._pressure_target = pressure_target
        self._phase = HugPhase.CLOSING

    def update_feedback(self, pressure_l: float, pressure_r: float) -> None:
        """Update force feedback. Transitions to HOLDING when target reached."""
        if self._phase == HugPhase.CLOSING:
            avg_pressure = (pressure_l + pressure_r) / 2.0
            if avg_pressure >= self._pressure_threshold:
                self._phase = HugPhase.HOLDING

    def release(self) -> None:
        """Start releasing."""
        self._phase = HugPhase.OPENING

    def complete_release(self) -> None:
        self._phase = HugPhase.OPEN

    def abort(self) -> None:
        """Emergency release."""
        self._phase = HugPhase.OPEN
