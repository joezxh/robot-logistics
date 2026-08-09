"""MQTT wildcard matching and topic round-tripping."""
from __future__ import annotations

import pytest

from rcs.mqtt.client import _topic_matches
from robot_contracts import (
    alert_topic,
    command_topic,
    command_topic_filter,
    device_id_from_topic,
    state_topic,
    telemetry_topic,
)


@pytest.mark.parametrize(
    "topic_filter,topic,expected",
    [
        ("rcs/+/command", "rcs/robot-01/command", True),
        ("rcs/+/command", "rcs/agv-01/command", True),
        ("rcs/+/command", "rcs/robot-01/state", False),
        # `+` matches exactly one level, so a nested id must not match.
        ("rcs/+/command", "rcs/a/b/command", False),
        ("rcs/+/command", "rcs/command", False),
        ("rcs/#", "rcs/robot-01/command", True),
        ("rcs/#", "other/robot-01/command", False),
        ("site-a/rcs/+/command", "site-a/rcs/robot-01/command", True),
        ("site-a/rcs/+/command", "site-b/rcs/robot-01/command", False),
        ("rcs/robot-01/state", "rcs/robot-01/state", True),
    ],
)
def test_topic_matches(topic_filter: str, topic: str, expected: bool) -> None:
    assert _topic_matches(topic_filter, topic) is expected


@pytest.mark.parametrize("prefix", ["", "site-a"])
@pytest.mark.parametrize(
    "builder", [command_topic, state_topic, alert_topic, telemetry_topic]
)
def test_topic_round_trip(builder, prefix: str) -> None:
    """Every topic we build must be parseable back into its device id."""
    topic = builder("robot-01", prefix)
    assert device_id_from_topic(topic, prefix) == "robot-01"


def test_command_filter_matches_command_topic() -> None:
    """The filter RCS subscribes to must match the topic robot-app publishes."""
    for prefix in ("", "site-a"):
        assert _topic_matches(command_topic_filter(prefix), command_topic("agv-01", prefix))


def test_device_id_from_foreign_topic_is_none() -> None:
    assert device_id_from_topic("weather/london/temp") is None
    assert device_id_from_topic("rcs/robot-01/unknown") is None
    assert device_id_from_topic("site-a/rcs/robot-01/command") is None  # prefix not declared
