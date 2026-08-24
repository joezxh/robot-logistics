"""Uplink: publish device state and fault alerts to the MQTT bus.

Two independent sources feed this module:

* **State** — consumed from ``ControlLoop.stream`` via ``StateStream.subscribe()``,
  the exact mechanism the WebSocket endpoint already uses. ``StateStream`` is
  itself rate-limited to 10 Hz, so the 1 kHz tick never reaches us; an optional
  second-stage downsample relieves broker pressure further.
* **Alerts** — consumed from ``ControlLoop.bus`` (``EventBus``). RCS has always
  published ``hal_read_timeout`` / ``hal_write_failure`` / ``controller_halted``
  there for "future subscribers"; this is the first one.

Nothing here runs inside the control tick.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time

from robot_contracts import (
    QOS_ALERT,
    QOS_STATE,
    RETAIN_ALERT,
    RETAIN_STATE,
    alert_topic,
    state_topic,
)

from ..loop import ControlLoop
from .client import MqttClient

logger = logging.getLogger(__name__)

_ALERT_EVENTS = ("hal_read_timeout", "hal_write_failure", "controller_halted")


def _iso_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class StatePublisher:
    """Forwards ``StateStream`` frames to ``rcs/{device_id}/state``."""

    def __init__(
        self,
        client: MqttClient,
        loop: ControlLoop,
        *,
        publish_hz: float = 10.0,
        topic_prefix: str = "",
    ) -> None:
        self._client = client
        self._loop = loop
        self._topic_prefix = topic_prefix
        # 0 (or negative) disables state publishing entirely.
        self._enabled = publish_hz > 0
        self._min_interval = 1.0 / publish_hz if self._enabled else 0.0
        self._last_sent: dict[str, float] = {}
        self._queue: asyncio.Queue | None = None
        self._task: asyncio.Task | None = None
        self.dropped = 0

    async def start(self) -> None:
        if not self._enabled:
            logger.info("MQTT state publishing disabled (publish_hz=0)")
            return
        self._queue = self._loop.stream.subscribe()
        self._task = asyncio.create_task(self._run(), name="rcs-mqtt-state-publisher")

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):
                pass
            self._task = None
        if self._queue is not None:
            self._loop.stream.unsubscribe(self._queue)
            self._queue = None

    async def _run(self) -> None:
        assert self._queue is not None
        while True:
            payload = await self._queue.get()
            try:
                self._forward(payload)
            except Exception:  # pragma: no cover - never kill the publisher
                logger.exception("MQTT state forward failed")

    def _forward(self, payload: bytes) -> None:
        # StateStream emits pre-encoded JSON; decode only the device_id so we
        # can route it, then republish the original bytes unmodified.
        try:
            device_id = json.loads(payload)["device_id"]
        except (ValueError, KeyError, TypeError):
            self.dropped += 1
            return

        now = time.monotonic()
        last = self._last_sent.get(device_id)
        if last is not None and now - last < self._min_interval:
            self.dropped += 1  # second-stage downsample
            return
        self._last_sent[device_id] = now

        self._client.publish(
            state_topic(device_id, self._topic_prefix),
            payload,
            qos=QOS_STATE,
            retain=RETAIN_STATE,
        )


class AlertPublisher:
    """Forwards ``EventBus`` fault events to ``rcs/{device_id}/alert``."""

    def __init__(self, client: MqttClient, loop: ControlLoop, *, topic_prefix: str = "") -> None:
        self._client = client
        self._loop = loop
        self._topic_prefix = topic_prefix
        self._subs: list = []

    async def start(self) -> None:
        for event in _ALERT_EVENTS:
            self._subs.append(
                self._loop.bus.subscribe(event, self._make_handler(event))
            )

    async def stop(self) -> None:
        for sub in self._subs:
            sub.unsubscribe()
        self._subs.clear()

    def _make_handler(self, event: str):
        def handler(payload: dict) -> None:
            device_id = (payload or {}).get("device_id")
            if not device_id:
                return
            body = json.dumps(
                {
                    "event": event,
                    "device_id": device_id,
                    "error": (payload or {}).get("error"),
                    "iso_ts": _iso_now(),
                }
            )
            self._client.publish(
                alert_topic(device_id, self._topic_prefix),
                body,
                qos=QOS_ALERT,
                retain=RETAIN_ALERT,
            )

        return handler
