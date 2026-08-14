"""Tests for LoaderMqttAdapter."""
from __future__ import annotations

import json
import pytest

from rcs.mqtt.loader_adapter import LoaderMqttAdapter
from rcs.mqtt.forklift_adapter import MQTTAdapterError


def test_parse_hug_grasp_command():
    raw = json.dumps({
        "type": "execute_task",
        "task_type": "hug_grasp",
        "parameters": {"object_width_m": 0.4},
    })
    cmd = LoaderMqttAdapter.from_json(raw)
    assert cmd.task_type == "hug_grasp"
    assert cmd.parameters["object_width_m"] == 0.4


def test_parse_rejects_forklift_task_type():
    raw = json.dumps({"type": "execute_task", "task_type": "extend_fork"})
    with pytest.raises(MQTTAdapterError, match="unknown loader task_type"):
        LoaderMqttAdapter.from_json(raw)


def test_format_status_14_joints():
    out = LoaderMqttAdapter.format_status([0.0] * 14, [0.0] * 14)
    assert "left_arm_0" in out["joint_names"]
    assert "right_arm_5" in out["joint_names"]
    assert "left_gripper" in out["joint_names"]
    assert "right_gripper" in out["joint_names"]


def test_format_status_wrong_joint_count():
    with pytest.raises(MQTTAdapterError):
        LoaderMqttAdapter.format_status([0.0] * 10, [0.0] * 10)
