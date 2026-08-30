"""Uplink: ingest digital-twin telemetry from the MQTT bus into StateStream.

The simulation backend mirrors robots into the live control stack by publishing
:class:`robot_contracts.TelemetryPayload` frames on ``robot/{device_id}/telemetry``.
This module subscribes to that wildcard and re-injects each frame into the same
:class:`~rcs.control.state.state_stream.StateStream` that real HAL state feeds,
so the frontend / control flow sees twin robots interchangeably with real ones.

Malformed payloads and unknown devices are logged and dropped — the same
defensive posture as :class:`CommandSubscriber`.
"""
from __future__ import annotations

import logging
import time

from pydantic import ValidationError
from robot_contracts import (
    QOS_TELEMETRY,
    TelemetryPayload,
    device_id_from_topic,
    telemetry_topic_filter,
)

from ..state.controller_state import ControllerMode, ControllerState
from ..state.error import TrackingError
from ..state.joint import JointState
from ..state.state_stream import StateStream
from .client import MqttClient

logger = logging.getLogger(__name__)


class TelemetryIngest:
    """Subscribes to ``robot/+/telemetry`` and feeds ``StateStream``."""

    def __init__(self, client: MqttClient, stream: StateStream, *, topic_prefix: str = "") -> None:
        self._client = client
        self._stream = stream
        self._topic_prefix = topic_prefix
        self.received = 0
        self.ingested = 0
        self.rejected = 0

    async def start(self) -> None:
        self._client.subscribe(
            telemetry_topic_filter(self._topic_prefix),
            QOS_TELEMETRY,
            self._on_telemetry,
        )
        logger.info("TelemetryIngest subscribed to %s", telemetry_topic_filter(self._topic_prefix))

    async def stop(self) -> None:  # client.stop() tears the subscription down
        return None

    # --- handler ----------------------------------------------------------

    def _on_telemetry(self, topic: str, raw: bytes) -> None:
        self.received += 1
        device_id = device_id_from_topic(topic, self._topic_prefix)
        if not device_id:
            self.rejected += 1
            logger.warning("Telemetry on unparseable topic: %s", topic)
            return
        try:
            payload = TelemetryPayload.model_validate_json(raw)
        except ValidationError as exc:
            self.rejected += 1
            logger.warning("Telemetry payload rejected for %s: %s", device_id, exc.error_count())
            return

        # A pure metrics/status frame (no twin block) is accepted but has no
        # joint state to inject; we still count it as ingested.
        if not payload.qpos and not payload.ee_pose:
            self.ingested += 1
            return

        n = len(payload.qpos)
        joint = JointState(
            device_id=device_id,
            positions=list(payload.qpos),
            velocities=list(payload.qvel[:n]) if payload.qvel else [0.0] * n,
            efforts=[0.0] * n,
            timestamp_ns=int(payload.sim_time * 1e9) if payload.sim_time else time.monotonic_ns(),
        )
        err = TrackingError(max_joint_error=0.0, position_error_m=0.0)
        ctrl = ControllerState(mode=ControllerMode.RUNNING, active_command_id=None, last_error=None)
        self._stream.publish(device_id, joint, err, ctrl)
        self.ingested += 1
