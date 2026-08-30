"""MQTT adapter for RCS.

Bridges the RCS control system to the message bus shared with the robot-side
application. Entirely opt-in: when ``RCS_MQTT_ENABLED`` is off, none of this is
imported and RCS behaves exactly as it did before.

The adapter is bolted on beside the control loop, never inside it:

    ControlLoop (up to 1 kHz)
        ├── StateStream.publish()  ──(10 Hz queue)──> StatePublisher  ──> MQTT
        └── EventBus.publish()     ──(callback)─────> AlertPublisher  ──> MQTT

    MQTT ──> CommandSubscriber ──> dispatch_command() ──> controller queue
"""
from __future__ import annotations

import logging

from ..config import settings
from ..registry import registry
from .client import MqttClient
from .publisher import AlertPublisher, StatePublisher
from .subscriber import CommandSubscriber
from .twin_ingest import TelemetryIngest

logger = logging.getLogger(__name__)


class MqttAdapter:
    """Wires the MQTT client to the running control loop."""

    def __init__(self, loop=None) -> None:
        # Import here to avoid a circular import at module load.
        if loop is None:
            from .. import _ensure_loaded

            loop = _ensure_loaded()
        self._loop = loop
        self._client = MqttClient(
            host=settings.mqtt_host,
            port=settings.mqtt_port,
            client_id=settings.mqtt_client_id,
            username=settings.mqtt_username,
            password=settings.mqtt_password,
            keepalive=settings.mqtt_keepalive,
            reconnect_min_delay=settings.mqtt_reconnect_min_delay,
            reconnect_max_delay=settings.mqtt_reconnect_max_delay,
        )
        prefix = settings.mqtt_topic_prefix
        self._state = StatePublisher(
            self._client,
            self._loop,
            publish_hz=settings.mqtt_state_publish_hz,
            topic_prefix=prefix,
        )
        self._alerts = AlertPublisher(self._client, self._loop, topic_prefix=prefix)
        self._commands = CommandSubscriber(self._client, topic_prefix=prefix)
        self._twin = TelemetryIngest(self._client, self._loop.stream, topic_prefix=prefix)

    @property
    def client(self) -> MqttClient:
        return self._client

    async def start(self) -> None:
        await self._client.start()
        await self._commands.start()
        await self._state.start()
        await self._alerts.start()
        await self._twin.start()
        logger.info(
            "MQTT adapter started (broker=%s:%s, devices=%d)",
            settings.mqtt_host,
            settings.mqtt_port,
            len(registry.list_devices()),
        )

    async def stop(self) -> None:
        await self._alerts.stop()
        await self._state.stop()
        await self._commands.stop()
        await self._twin.stop()
        await self._client.stop()
        logger.info("MQTT adapter stopped")


__all__ = [
    "MqttAdapter",
    "MqttClient",
    "StatePublisher",
    "AlertPublisher",
    "CommandSubscriber",
    "TelemetryIngest",
]
