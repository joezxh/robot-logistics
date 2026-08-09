"""MQTT bridge for the simulation backend.

Connects to the same Mosquitto broker used by RCS and robot-app so that
simulation tasks can flow through the real command/state pipeline.

Uses paho-mqtt ``loop_start()`` for background I/O.  State callbacks run in
the paho thread; callers that need to touch asyncio state should use
``asyncio.run_coroutine_threadsafe()``.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class SimulationMqttBridge:
    """Lightweight MQTT adapter for the simulation backend."""

    def __init__(self, *, host: str, port: int, enabled: bool = True) -> None:
        self._host = host
        self._port = port
        self._enabled = enabled
        self._client: Any = None
        self._connected = False
        self._state_callbacks: dict[str, Callable[[dict], None]] = {}

    # --- lifecycle ----------------------------------------------------------

    def start(self) -> None:
        if not self._enabled:
            logger.info("MQTT bridge disabled")
            return
        try:
            import paho.mqtt.client as mqtt

            self._client = mqtt.Client(client_id="simulation-backend", clean_session=True)
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect
            self._client.on_message = self._on_message
            self._client.connect_async(self._host, self._port, 60)
            self._client.loop_start()
            logger.info("MQTT bridge connecting to %s:%s", self._host, self._port)
        except Exception as exc:
            logger.warning("MQTT bridge failed to start: %s", exc)

    def stop(self) -> None:
        if self._client is not None:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
        self._connected = False

    # --- pub / sub ----------------------------------------------------------

    def publish_command(self, topic: str, payload: dict) -> bool:
        """Publish a JSON-serialisable command to an MQTT topic."""
        if not self._enabled or self._client is None or not self._connected:
            return False
        data = json.dumps(payload).encode()
        info = self._client.publish(topic, data, qos=1)
        return info.rc == 0

    def subscribe_state(self, topic: str, callback: Callable[[dict], None]) -> None:
        """Register a callback for state messages on *topic*."""
        self._state_callbacks[topic] = callback
        if self._client is not None and self._connected:
            self._client.subscribe(topic, qos=0)

    # --- paho callbacks -----------------------------------------------------

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        if rc == 0:
            self._connected = True
            logger.info("MQTT bridge connected")
            for topic in self._state_callbacks:
                client.subscribe(topic, qos=0)
        else:
            logger.warning("MQTT bridge connect refused, rc=%s", rc)

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        self._connected = False
        if rc != 0:
            logger.warning("MQTT bridge lost (rc=%s); reconnecting", rc)

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        cb = self._state_callbacks.get(msg.topic)
        if cb is None:
            cb = self._match_wildcard(msg.topic)
        if cb is not None:
            try:
                payload = json.loads(msg.payload.decode())
                cb(payload)
            except Exception:
                logger.exception("state callback failed for %s", msg.topic)

    def _match_wildcard(self, topic: str) -> Callable[[dict], None] | None:
        """Match MQTT wildcard subscriptions (+, #)."""
        for pattern, cb in self._state_callbacks.items():
            if "#" in pattern or "+" in pattern:
                if self._topic_matches(pattern, topic):
                    return cb
        return None

    @staticmethod
    def _topic_matches(pattern: str, topic: str) -> bool:
        pattern_parts = pattern.split("/")
        topic_parts = topic.split("/")
        for i, pp in enumerate(pattern_parts):
            if pp == "#":
                return True
            if i >= len(topic_parts):
                return False
            if pp != "+" and pp != topic_parts[i]:
                return False
        return len(pattern_parts) == len(topic_parts)
