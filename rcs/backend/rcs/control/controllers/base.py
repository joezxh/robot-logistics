"""Controller abstract base class."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from ..state.joint import JointState
from ..state.command import Command
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from ..state.profile import DeviceProfile, Morphology


class Controller(ABC):
    morphology: ClassVar[Morphology]  # marker — overridden in subclasses

    def __init__(self, profile: DeviceProfile) -> None:
        self.profile = profile
        self.state = ControllerState()

    @abstractmethod
    def update(self, hal_state: JointState) -> JointState: ...

    @abstractmethod
    def tracking_error(self, target: JointState, current: JointState) -> TrackingError: ...

    def on_command(self, cmd: Command) -> None: ...

    def halt(self) -> None:
        self.state.mode = ControllerMode.HALTED
        self.state.last_error = "halt requested"

    def recover(self) -> None:
        if self.state.mode == ControllerMode.HALTED:
            self.state.mode = ControllerMode.IDLE
            self.state.last_error = None

    def estop(self) -> None:
        self.state.mode = ControllerMode.E_STOP
        self.state.last_error = "estop"

    def clear_estop(self) -> None:
        if self.state.mode == ControllerMode.E_STOP:
            self.state.mode = ControllerMode.IDLE
            self.state.last_error = None
