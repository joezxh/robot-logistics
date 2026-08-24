"""ControlLoop: per-device tick coroutine at the device's control_hz."""
from __future__ import annotations
import asyncio
import time
import numpy as np

from .registry import registry
from .state.state_stream import StateStream
from .state.controller_state import ControllerMode
from .events import EventBus


class ControlLoop:
    def __init__(self, bus: EventBus | None = None) -> None:
        self._tasks: dict[str, asyncio.Task] = {}
        self._health: dict[str, dict] = {}
        self._stop_event = asyncio.Event()
        self._stream = StateStream()
        self._bus = bus or EventBus()

    @property
    def stream(self) -> StateStream:
        return self._stream

    @property
    def bus(self) -> EventBus:
        return self._bus

    def start(self) -> None:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return  # No loop; ControlLoop must be started from an async context.
        for profile in registry.list_devices():
            self._tasks[profile.device_id] = asyncio.create_task(self._run(profile.device_id))

    def shutdown(self) -> None:
        self._stop_event.set()
        for t in self._tasks.values():
            t.cancel()

    def tick_health(self) -> dict:
        return dict(self._health)

    async def _run(self, device_id: str) -> None:
        prof = registry.get_profile(device_id)
        ctrl = registry.get_controller(device_id)
        hal = registry.get_hal()
        period_s = 1.0 / prof.control_hz
        next_tick = time.monotonic()
        ticks = 0
        last_window_start = time.monotonic()
        last_window_count = 0
        while not self._stop_event.is_set():
            try:
                cur = await asyncio.wait_for(hal.read(device_id), timeout=0.05 if prof.control_hz >= 500 else 0.2)
            except (asyncio.TimeoutError, KeyError) as exc:
                self._bus.publish("hal_read_timeout", {"device_id": device_id, "error": str(exc)})
                ctrl.state.mode = ControllerMode.FAULT
                ctrl.state.last_error = f"read timeout: {exc}"
                continue
            try:
                target = ctrl.update(cur)
                if not np.all(np.isfinite(target.positions)):
                    continue
                await asyncio.wait_for(hal.write(device_id, target.positions), timeout=0.02 if prof.control_hz >= 500 else 0.1)
            except (asyncio.TimeoutError, KeyError) as exc:
                self._bus.publish("hal_write_failure", {"device_id": device_id, "error": str(exc)})
                continue
            err = ctrl.tracking_error(target, cur)
            if ctrl.state.mode == ControllerMode.HALTED:
                self._bus.publish("controller_halted", {"device_id": device_id})
            self._stream.publish(device_id, cur, err, ctrl.state)
            ticks += 1
            now = time.monotonic()
            if now - last_window_start >= 1.0:
                self._health[device_id] = {
                    "actual_hz": (ticks - last_window_count) / (now - last_window_start),
                    "ticks": ticks,
                }
                last_window_start = now
                last_window_count = ticks
            next_tick += period_s
            sleep_for = next_tick - time.monotonic()
            if sleep_for > 0:
                await asyncio.sleep(sleep_for)
            else:
                # Drift accumulated; resync.
                next_tick = time.monotonic()
