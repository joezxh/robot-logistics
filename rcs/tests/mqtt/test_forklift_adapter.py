"""Tests for ForkliftMqttAdapter."""
from __future__ import annotations

import json
import pytest

from rcs.mqtt.forklift_adapter import ForkliftMqttAdapter, MQTTAdapterError


def test_parse_extend_fork_command():
    raw = json.dumps({
        "type": "execute_task",
        "task_type": "extend_fork",
        "parameters": {"extension_m": 0.3},
    })
    cmd = ForkliftMqttAdapter.from_json(raw)
    assert cmd.task_type == "extend_fork"
    assert cmd.parameters == {"extension_m": 0.3}


def test_parse_rejects_non_execute_task():
    raw = json.dumps({"type": "move_j", "target_joints": [0.1]})
    with pytest.raises(MQTTAdapterError, match="unsupported type"):
        ForkliftMqttAdapter.from_json(raw)


def test_parse_rejects_unknown_task_type():
    raw = json.dumps({"type": "execute_task", "task_type": "fly"})
    with pytest.raises(MQTTAdapterError, match="unknown forklift task_type"):
        ForkliftMqttAdapter.from_json(raw)


def test_format_status_3_joints():
    out = ForkliftMqttAdapter.format_status([0.0, 0.5, 0.3], [0.1, 0.0, 0.0])
    assert out["joint_names"] == ["travel", "lift", "extend"]
    assert out["joint_positions"] == [0.0, 0.5, 0.3]


def test_format_status_wrong_joint_count():
    with pytest.raises(MQTTAdapterError):
        ForkliftMqttAdapter.format_status([0.0, 0.5], [0.0, 0.0])


def test_to_json_round_trip():
    raw = json.dumps({"type": "execute_task", "task_type": "lift_fork", "parameters": {"height_m": 1.5}})
    parsed = ForkliftMqttAdapter.from_json(raw)
    assert parsed.task_type == "lift_fork"
