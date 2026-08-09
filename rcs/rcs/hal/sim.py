"""In-memory SimHAL — math-only, no real hardware.

Models each joint as a first-order lag toward the last commanded target.
This is intentionally simple: the goal is to exercise the control loop
end-to-end, not to simulate physics.
"""
from __future__ import annotations
import asyncio

from ..state.joint import JointState
from ..state.profile import DeviceProfile


class SimHAL:
    def __init__(self) -> None:
        self._profiles: dict[str, DeviceProfile] = {}
        self._state: dict[str, JointState] = {}
        self._targets: dict[str, list[float]] = {}
        self._estopped: set[str] = set()
        self._lock = asyncio.Lock()

    def register(self, profile: DeviceProfile) -> None:
        self._profiles[profile.device_id] = profile
        self._state[profile.device_id] = JointState(
            positions=[0.0] * profile.num_joints,
            velocities=[0.0] * profile.num_joints,
            efforts=[0.0] * profile.num_joints,
            device_id=profile.device_id,
        )
        self._targets[profile.device_id] = list(profile.home_joints)

    def profile(self, device_id: str) -> DeviceProfile:
        return self._profiles[device_id]

    async def read(self, device_id: str) -> JointState:
        if device_id not in self._state:
            raise KeyError(f"unknown device_id: {device_id}")
        s = self._state[device_id]
        # First-order lag: move fully toward target each call (synchronous in async).
        target = self._targets[device_id]
        new_pos = [p + 1.0 * (t - p) for p, t in zip(s.positions, target)]
        s.positions = new_pos
        s.velocities = [0.0] * len(new_pos)
        s.efforts = [0.0] * len(new_pos)
        return JointState(
            positions=list(s.positions),
            velocities=list(s.velocities),
            efforts=list(s.efforts),
            device_id=device_id,
        )

    async def write(self, device_id: str, target) -> None:
        if device_id in self._estopped:
            return
        if device_id not in self._targets:
            raise KeyError(f"unknown device_id: {device_id}")
        if isinstance(target, JointState):
            target = list(target.positions)
        # Clip to limits.
        prof = self._profiles[device_id]
        lo, hi = prof.limits.pos_lower, prof.limits.pos_upper
        clipped = [max(lo[i], min(hi[i], target[i])) for i in range(len(target))]
        self._targets[device_id] = clipped

    async def estop(self, device_id: str) -> None:
        if device_id not in self._profiles:
            raise KeyError(f"unknown device_id: {device_id}")
        self._estopped.add(device_id)

    def clear_estop(self, device_id: str) -> None:
        self._estopped.discard(device_id)
