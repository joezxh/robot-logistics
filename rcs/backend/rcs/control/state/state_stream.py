"""In-memory state broadcast with 10 Hz rate-limit and 64 KB cap."""
from __future__ import annotations
import asyncio
import json
import time
from collections import defaultdict
from dataclasses import dataclass

from .joint import JointState
from .error import TrackingError
from .controller_state import ControllerState


@dataclass
class StateFrame:
    device_id: str
    joint: JointState
    err: TrackingError
    ctrl: ControllerState
    iso_ts: str


class StateStream:
    def __init__(self, max_fps: float = 10.0, max_bytes: int = 64 * 1024) -> None:
        self._min_interval_ns = int(1e9 / max_fps)
        self._max_bytes = max_bytes
        self._last_emit_ns: dict[str, int] = defaultdict(int)
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=64)
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        try:
            self._subscribers.remove(q)
        except ValueError:
            pass

    def publish(
        self,
        device_id: str,
        joint: JointState,
        err: TrackingError,
        ctrl: ControllerState,
    ) -> None:
        now = time.monotonic_ns()
        if now - self._last_emit_ns[device_id] < self._min_interval_ns:
            return
        self._last_emit_ns[device_id] = now
        frame = StateFrame(
            device_id=device_id,
            joint=joint,
            err=err,
            ctrl=ctrl,
            iso_ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )
        payload = json.dumps(frame.__dict__ | {
            "joint": joint.to_dict(),
            "err": err.to_dict(),
            "ctrl": ctrl.to_dict(),
        }, default=list).encode()
        degraded = False
        if len(payload) > self._max_bytes:
            degraded = True
            payload = json.dumps({
                "device_id": device_id,
                "joint": joint.to_dict(),
                "ctrl": ctrl.to_dict(),
                "iso_ts": frame.iso_ts,
                "degraded": True,
            }, default=list).encode()
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except asyncio.QueueFull:
                pass

    def force_publish(
        self,
        device_id: str,
        joint: JointState,
        err: TrackingError,
        ctrl: ControllerState,
    ) -> None:
        """Bypass the 10 Hz rate-limit (used for mode changes / estop)."""
        prev = self._last_emit_ns.get(device_id, 0)
        self._last_emit_ns[device_id] = 0
        self.publish(device_id, joint, err, ctrl)
        self._last_emit_ns[device_id] = prev
