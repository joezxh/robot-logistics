"""Thin asyncio-friendly wrapper around paho-mqtt.

paho's network loop runs on its own thread (``loop_start``), so callbacks fire
off the asyncio event loop. Every callback here therefore does the minimum
possible work and hands anything asynchronous back to the event loop via
``call_soon_threadsafe``.

Design constraints:

* **Never block the caller.** ``publish`` is fire-and-forget; failures are
  counted, not raised, so a broker outage can never stall the control loop.
* **Never touch the 1 kHz tick.** Nothing in this module is called from
  ``ControlLoop._run``.
* **Degrade silently.** If the broker is unreachable, paho reconnects in the
  background with exponential backoff and RCS keeps serving REST/WS as usual.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Log at most one publish failure per this many failures, to avoid flooding the
# log while a broker is down.
_FAILURE_LOG_EVERY = 100


class MqttClient:
    """Managed MQTT connection with background reconnect and failure counters."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        client_id: str,
        username: str = "",
        password: str = "",
        keepalive: int = 60,
        reconnect_min_delay: float = 1.0,
        reconnect_max_delay: float = 30.0,
    ) -> None:
        self._host = host
        self._port = port
        self._client_id = client_id
        self._username = username
        self._password = password
        self._keepalive = keepalive
        self._reconnect_min_delay = reconnect_min_delay
        self._reconnect_max_delay = reconnect_max_delay

        self._client: Any = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._connected = False
        self._started = False

        self.publish_failures = 0
        self.publish_successes = 0
        self.messages_received = 0

        # topic filter -> handler(topic, payload_bytes). Handlers are invoked on
        # the asyncio loop, not on paho's network thread.
        self._handlers: dict[str, Callable[[str, bytes], None]] = {}
        self._subscriptions: list[tuple[str, int]] = []

    # --- properties ---------------------------------------------------------

    @property
    def connected(self) -> bool:
        return self._connected

    # --- lifecycle ----------------------------------------------------------

    async def start(self) -> None:
        """Connect in the background. Returns immediately; never raises on a
        broker being down — paho retries on its own."""
        if self._started:
            return

        import paho.mqtt.client as mqtt  # imported lazily: optional dependency

        self._loop = asyncio.get_running_loop()
        self._client = mqtt.Client(client_id=self._client_id, clean_session=True)
        if self._username:
            self._client.username_pw_set(self._username, self._password or None)
        self._client.reconnect_delay_set(
            min_delay=int(self._reconnect_min_delay),
            max_delay=int(self._reconnect_max_delay),
        )
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_message = self._on_message

        try:
            # connect_async never blocks and never raises on an unreachable
            # broker; loop_start drives the reconnect attempts.
            self._client.connect_async(self._host, self._port, self._keepalive)
            self._client.loop_start()
            self._started = True
            logger.info("MQTT client connecting to %s:%s", self._host, self._port)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("MQTT client failed to start: %s", exc)

    async def stop(self) -> None:
        if not self._started or self._client is None:
            return
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:  # pragma: no cover - defensive
            pass
        self._started = False
        self._connected = False
        logger.info(
            "MQTT client stopped (published=%d failures=%d received=%d)",
            self.publish_successes,
            self.publish_failures,
            self.messages_received,
        )

    # --- pub / sub ----------------------------------------------------------

    def subscribe(self, topic_filter: str, qos: int, handler: Callable[[str, bytes], None]) -> None:
        """Register a handler and subscribe. Safe to call before connecting —
        subscriptions are replayed on every (re)connect."""
        self._handlers[topic_filter] = handler
        self._subscriptions.append((topic_filter, qos))
        if self._connected and self._client is not None:
            self._client.subscribe(topic_filter, qos)

    def publish(self, topic: str, payload: str | bytes, qos: int = 0, retain: bool = False) -> bool:
        """Fire-and-forget publish. Returns False on failure instead of raising."""
        if self._client is None:
            self._record_failure("client not started")
            return False
        try:
            info = self._client.publish(topic, payload, qos=qos, retain=retain)
        except Exception as exc:
            self._record_failure(str(exc))
            return False
        if info.rc != 0:
            self._record_failure(f"rc={info.rc}")
            return False
        self.publish_successes += 1
        return True

    def _record_failure(self, reason: str) -> None:
        self.publish_failures += 1
        if self.publish_failures % _FAILURE_LOG_EVERY == 1:
            logger.warning(
                "MQTT publish failed (%s); total failures=%d",
                reason,
                self.publish_failures,
            )

    # --- paho callbacks (run on paho's network thread) ----------------------

    def _on_connect(self, client: Any, userdata: Any, flags: Any, rc: int) -> None:
        if rc != 0:
            logger.warning("MQTT connect refused, rc=%s", rc)
            return
        self._connected = True
        logger.info("MQTT connected to %s:%s", self._host, self._port)
        # Replay subscriptions — required after a reconnect with clean_session.
        for topic_filter, qos in self._subscriptions:
            client.subscribe(topic_filter, qos)

    def _on_disconnect(self, client: Any, userdata: Any, rc: int) -> None:
        self._connected = False
        if rc != 0:
            logger.warning("MQTT unexpectedly disconnected (rc=%s); reconnecting", rc)
        else:
            logger.info("MQTT disconnected")

    def _on_message(self, client: Any, userdata: Any, msg: Any) -> None:
        self.messages_received += 1
        handler = self._match_handler(msg.topic)
        if handler is None:
            return
        loop = self._loop
        if loop is None or loop.is_closed():
            return
        # Hop back onto the asyncio loop: handlers touch RCS state.
        loop.call_soon_threadsafe(self._safe_invoke, handler, msg.topic, msg.payload)

    @staticmethod
    def _safe_invoke(handler: Callable[[str, bytes], None], topic: str, payload: bytes) -> None:
        try:
            handler(topic, payload)
        except Exception:  # pragma: no cover - handler isolation
            logger.exception("MQTT message handler raised for topic %s", topic)

    def _match_handler(self, topic: str) -> Callable[[str, bytes], None] | None:
        for topic_filter, handler in self._handlers.items():
            if _topic_matches(topic_filter, topic):
                return handler
        return None


def _topic_matches(topic_filter: str, topic: str) -> bool:
    """MQTT topic filter matching supporting the ``+`` and ``#`` wildcards."""
    f_parts = topic_filter.split("/")
    t_parts = topic.split("/")
    for i, f in enumerate(f_parts):
        if f == "#":
            return True
        if i >= len(t_parts):
            return False
        if f != "+" and f != t_parts[i]:
            return False
    return len(f_parts) == len(t_parts)
