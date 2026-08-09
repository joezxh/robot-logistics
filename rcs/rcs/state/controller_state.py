"""Per-device controller mode + active command."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class ControllerMode(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    HALTED = "halted"
    FAULT = "fault"
    E_STOP = "e_stop"


@dataclass
class ControllerState:
    mode: ControllerMode = ControllerMode.IDLE
    active_command_id: str | None = None
    last_error: str | None = None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "active_command_id": self.active_command_id,
            "last_error": self.last_error,
        }
