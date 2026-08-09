"""Bridge logic between the MQTT bus and the robot's local action sinks.

Split out from :mod:`robot_gateway.mqtt_bridge_node` so the routing and
contract-handling rules can be unit-tested with a fake link and fake sink,
without a ROS 2 graph.

Responsibilities:

* **Downlink** — decode ``rcs/{device_id}/command``, then hand the command to a
  sink callable. E-stop is routed to a separate, always-available path so a
  busy or wedged motion sink can never delay it.
* **Uplink** — publish telemetry (buffered while offline) and state.

Nothing here blocks: a slow sink is the caller's problem to bound, and MQTT
publishes are fire-and-forget.
"""
from __future__ import annotations

import logging
from typing import Callable, Protocol

from robot_contracts import (
    QOS_STATE,
    QOS_TELEMETRY,
    RETAIN_STATE,
    RETAIN_TELEMETRY,
    QOS_COMMAND,
    command_topic_filter,
    device_id_from_topic,
    state_topic,
    telemetry_topic,
)
from robot_msgs import CommandMsg, RobotStateMsg, RobotTelemetryMsg, TaskCommandMsg

from .contract import ContractError, decode_command, decode_task_command, encode_state, encode_telemetry

logger = logging.getLogger(__name__)


class SupportsPublish(Protocol):
    """Structural type for :class:`robot_gateway.mqtt_link.MqttLink`."""

    def subscribe(self, topic_filter: str, qos: int, handler: Callable[[str, bytes], None]) -> None: ...

    def publish(
        self,
        topic: str,
        payload: bytes,
        qos: int = 0,
        retain: bool = False,
        *,
        buffer_if_offline: bool = False,
    ) -> bool: ...


class MqttBridge:
    """Routes commands inbound and telemetry/state outbound.

    :param device_id: the device this robot answers for. Commands addressed to
        any other device are ignored -- several robots may share a broker.
    :param motion_sink: called with every accepted non-emergency command.
    :param estop_sink: called for ``estop``. Defaults to ``motion_sink`` when
        not supplied, but a dedicated fast path is strongly recommended.
    """

    def __init__(
        self,
        link: SupportsPublish,
        *,
        device_id: str,
        motion_sink: Callable[[CommandMsg], None],
        estop_sink: Callable[[CommandMsg], None] | None = None,
        task_sink: Callable[[TaskCommandMsg], None] | None = None,
        topic_prefix: str = "",
    ) -> None:
        self._link = link
        self._device_id = device_id
        self._motion_sink = motion_sink
        self._estop_sink = estop_sink or motion_sink
        self._task_sink = task_sink
        self._topic_prefix = topic_prefix

        self.commands_accepted = 0
        self.commands_rejected = 0
        self.commands_ignored = 0
        self.states_published = 0
        self.telemetry_published = 0

    # --- lifecycle ----------------------------------------------------------

    def start(self) -> None:
        """Subscribe to the command topic.

        We subscribe with the wildcard rather than our own device topic so that
        misaddressed traffic is visible in ``commands_ignored`` instead of being
        silently filtered by the broker -- that has repeatedly proven to be the
        difference between a five-minute and a five-hour diagnosis.
        """
        self._link.subscribe(
            command_topic_filter(self._topic_prefix),
            QOS_COMMAND,
            self.handle_command_message,
        )

    # --- downlink -----------------------------------------------------------

    def handle_command_message(self, topic: str, raw: bytes) -> None:
        """Entry point for an inbound MQTT command. Never raises."""
        device_id = device_id_from_topic(topic, self._topic_prefix)
        if device_id is None:
            self.commands_rejected += 1
            logger.warning("command on unparseable topic: %s", topic)
            return
        if device_id != self._device_id:
            self.commands_ignored += 1
            return

        try:
            command = decode_command(raw)
        except ContractError as exc:
            self.commands_rejected += 1
            logger.warning("command payload rejected: %s", exc)
            return

        # Route execute_task to task_sink
        if command.type == "execute_task":
            if self._task_sink is None:
                self.commands_rejected += 1
                logger.warning("execute_task received but no task_sink configured")
                return
            try:
                task_msg = decode_task_command(raw)
            except ContractError as exc:
                self.commands_rejected += 1
                logger.warning("execute_task payload rejected: %s", exc)
                return
            try:
                self._task_sink(task_msg)
            except Exception:
                self.commands_rejected += 1
                logger.exception("task_sink raised for %s", task_msg.task_type)
                return
            self.commands_accepted += 1
            logger.debug(
                "execute_task %s accepted (command_id=%s)",
                task_msg.task_type,
                task_msg.command_id,
            )
            return

        sink = self._estop_sink if command.is_emergency else self._motion_sink
        try:
            sink(command)
        except Exception:
            self.commands_rejected += 1
            logger.exception("command sink raised for %s", command.type)
            return

        self.commands_accepted += 1
        logger.debug(
            "command %s accepted (command_id=%s)", command.type, command.command_id
        )

    # --- uplink -------------------------------------------------------------

    def publish_state(self, state: RobotStateMsg) -> bool:
        """Publish a state frame. Not buffered: stale state is worse than none."""
        try:
            payload = encode_state(state)
        except Exception as exc:
            logger.warning("failed to encode state: %s", exc)
            return False
        ok = self._link.publish(
            state_topic(state.device_id, self._topic_prefix),
            payload,
            qos=QOS_STATE,
            retain=RETAIN_STATE,
        )
        if ok:
            self.states_published += 1
        return ok

    def publish_telemetry(self, telemetry: RobotTelemetryMsg) -> bool:
        """Publish telemetry, buffering it while the broker is unreachable."""
        try:
            payload = encode_telemetry(telemetry)
        except Exception as exc:
            logger.warning("failed to encode telemetry: %s", exc)
            return False
        ok = self._link.publish(
            telemetry_topic(telemetry.device_id, self._topic_prefix),
            payload,
            qos=QOS_TELEMETRY,
            retain=RETAIN_TELEMETRY,
            buffer_if_offline=True,
        )
        if ok:
            self.telemetry_published += 1
        return ok

    # --- diagnostics --------------------------------------------------------

    def stats(self) -> dict[str, int]:
        return {
            "commands_accepted": self.commands_accepted,
            "commands_rejected": self.commands_rejected,
            "commands_ignored": self.commands_ignored,
            "states_published": self.states_published,
            "telemetry_published": self.telemetry_published,
        }
