"""MQTT topic namespace shared by RCS and the robot-side application.

Both sides import from here so topic strings are never hard-coded twice. See
``shared/contracts/mqtt_topics.md`` for the normative specification.

Topic layout::

    rcs/{device_id}/command       QoS 1   downlink   external -> RCS
    rcs/{device_id}/state         QoS 0   uplink     RCS -> robot-app
    rcs/{device_id}/alert         QoS 1   uplink     RCS -> robot-app
    robot/{device_id}/telemetry   QoS 0   uplink     robot-app -> RCS

An optional deployment-wide prefix may be prepended (multi-tenant brokers).
"""
from __future__ import annotations

# --- QoS levels -------------------------------------------------------------
# Commands must not be lost -> QoS 1. State is high-rate and superseded by the
# next sample, so at-most-once delivery is the right trade-off -> QoS 0.
QOS_COMMAND = 1
QOS_STATE = 0
QOS_ALERT = 1
QOS_TELEMETRY = 0

# Retain the last state frame so a late-joining subscriber immediately learns
# the current device state instead of waiting for the next sample.
RETAIN_STATE = True
RETAIN_COMMAND = False
RETAIN_ALERT = False
RETAIN_TELEMETRY = False

# --- Topic templates --------------------------------------------------------
COMMAND_TOPIC = "rcs/{device_id}/command"
STATE_TOPIC = "rcs/{device_id}/state"
ALERT_TOPIC = "rcs/{device_id}/alert"
TELEMETRY_TOPIC = "robot/{device_id}/telemetry"

# MQTT single-level wildcard, used by RCS to subscribe to all device commands
# and by robot-app to subscribe to all device state.
COMMAND_TOPIC_WILDCARD = "rcs/+/command"
STATE_TOPIC_WILDCARD = "rcs/+/state"
ALERT_TOPIC_WILDCARD = "rcs/+/alert"
TELEMETRY_TOPIC_WILDCARD = "robot/+/telemetry"


def _join(prefix: str, topic: str) -> str:
    prefix = prefix.strip().strip("/")
    return f"{prefix}/{topic}" if prefix else topic


def command_topic(device_id: str, prefix: str = "") -> str:
    return _join(prefix, COMMAND_TOPIC.format(device_id=device_id))


def state_topic(device_id: str, prefix: str = "") -> str:
    return _join(prefix, STATE_TOPIC.format(device_id=device_id))


def alert_topic(device_id: str, prefix: str = "") -> str:
    return _join(prefix, ALERT_TOPIC.format(device_id=device_id))


def telemetry_topic(device_id: str, prefix: str = "") -> str:
    return _join(prefix, TELEMETRY_TOPIC.format(device_id=device_id))


def command_topic_filter(prefix: str = "") -> str:
    return _join(prefix, COMMAND_TOPIC_WILDCARD)


def state_topic_filter(prefix: str = "") -> str:
    return _join(prefix, STATE_TOPIC_WILDCARD)


def alert_topic_filter(prefix: str = "") -> str:
    return _join(prefix, ALERT_TOPIC_WILDCARD)


def telemetry_topic_filter(prefix: str = "") -> str:
    return _join(prefix, TELEMETRY_TOPIC_WILDCARD)


def device_id_from_topic(topic: str, prefix: str = "") -> str | None:
    """Extract ``device_id`` from a concrete topic, or ``None`` if it doesn't match.

    Handles the optional prefix transparently, so a subscriber can recover the
    device without tracking which prefix it subscribed under.
    """
    prefix = prefix.strip().strip("/")
    if prefix:
        if not topic.startswith(prefix + "/"):
            return None
        topic = topic[len(prefix) + 1 :]
    parts = topic.split("/")
    if len(parts) != 3:
        return None
    root, device_id, leaf = parts
    if root not in ("rcs", "robot"):
        return None
    if leaf not in ("command", "state", "alert", "telemetry"):
        return None
    return device_id or None
