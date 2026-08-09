"""Device HAL Protocol — hardware abstraction for RCS-1."""
from __future__ import annotations
from typing import Protocol, runtime_checkable

from ..state.joint import JointState
from ..state.profile import DeviceProfile


@runtime_checkable
class DeviceHAL(Protocol):
    async def read(self, device_id: str) -> JointState: ...
    async def write(self, device_id: str, target: list[float] | JointState) -> None: ...
    async def estop(self, device_id: str) -> None: ...
    def profile(self, device_id: str) -> DeviceProfile: ...
