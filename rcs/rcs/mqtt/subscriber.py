"""Downlink: accept commands from the MQTT bus.

Commands are validated against the shared contract and then handed to
:func:`rcs.dispatch.dispatch_command` — the *same* function the REST router
calls. That is what guarantees a `move_j` over MQTT and a `move_j` over REST
produce identical behaviour, including the 1024-deep queue backpressure check.

Malformed payloads and unknown devices are logged and dropped: there is no
reply channel in this contract, and raising would only break the MQTT client's
message pump.
"""
from __future__ import annotations

import logging

from pydantic import ValidationError
from robot_contracts import (
    QOS_COMMAND,
    CommandPayload,
    command_topic_filter,
    device_id_from_topic,
)

from ..dispatch import DispatchError, dispatch_command
from ..state.pose import Pose6D
from .client import MqttClient

logger = logging.getLogger(__name__)


class CommandSubscriber:
    """Subscribes to ``rcs/+/command`` and dispatches into the controllers."""

    def __init__(self, client: MqttClient, *, topic_prefix: str = "") -> None:
        self._client = client
        self._topic_prefix = topic_prefix
        self.accepted = 0
        self.rejected = 0

    async def start(self) -> None:
        self._client.subscribe(
            command_topic_filter(self._topic_prefix),
            QOS_COMMAND,
            self._on_command,
        )

    async def stop(self) -> None:  # nothing to unwind; client.stop() tears down
        return None

    def _on_command(self, topic: str, raw: bytes) -> None:
        device_id = device_id_from_topic(topic, self._topic_prefix)
        if not device_id:
            self.rejected += 1
            logger.warning("MQTT command on unparseable topic: %s", topic)
            return

        try:
            payload = CommandPayload.model_validate_json(raw)
        except ValidationError as exc:
            self.rejected += 1
            logger.warning("MQTT command payload rejected for %s: %s", device_id, exc.error_count())
            return

        pose = None
        if payload.target_pose is not None:
            p = payload.target_pose
            pose = Pose6D(x=p.x, y=p.y, z=p.z, rx=p.rx, ry=p.ry, rz=p.rz)

        try:
            result = dispatch_command(
                device_id,
                type=payload.type.value,
                command_id=payload.command_id,
                target_pose=pose,
                target_joints=payload.target_joints,
                speed_scale=payload.speed_scale,
                constraints=payload.constraints,
            )
        except DispatchError as exc:
            self.rejected += 1
            logger.warning("MQTT command rejected for %s: %s (%s)", device_id, exc.detail, exc.code)
            return

        self.accepted += 1
        logger.debug(
            "MQTT command %s accepted for %s (command_id=%s)",
            result.status,
            device_id,
            result.command_id,
        )
