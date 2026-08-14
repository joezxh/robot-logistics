"""HAL interface abstract base class."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class JointStateMsg:
    positions: list[float]
    velocities: list[float]
    efforts: list[float]
    device_id: str


@dataclass
class CommandMsg:
    type: str
    task_type: str | None = None
    parameters: dict | None = None


class HALInterface(ABC):
    """Abstract HAL for a Top 3 device (forklift or loader)."""

    device_id: str
    num_joints: int

    @abstractmethod
    def read_state(self) -> JointStateMsg: ...

    @abstractmethod
    def send_command(self, cmd: CommandMsg) -> bool: ...

    @abstractmethod
    def estop(self) -> None: ...

    @abstractmethod
    def recover(self) -> None: ...


def make_hal(device_id: str, num_joints: int) -> HALInterface:
    """Factory: return SimHalDriver or RealHardwareDriver based on HAL_MODE."""
    import os
    mode = os.environ.get("HAL_MODE", "sim").lower()
    if mode == "real":
        from .real_hw_driver import RealHardwareDriver
        return RealHardwareDriver(device_id=device_id, num_joints=num_joints)
    from .sim_hal_driver import SimHalDriver
    return SimHalDriver(device_id=device_id, num_joints=num_joints)