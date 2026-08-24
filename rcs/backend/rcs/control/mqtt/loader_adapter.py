"""Dual-arm loader MQTT command adapter."""
from __future__ import annotations

import json
from typing import Any

from ..state.command import Command, CommandType
from .forklift_adapter import ForkliftMqttAdapter, MQTTAdapterError


class LoaderMqttAdapter(ForkliftMqttAdapter):
    LOADER_TASK_TYPES = {"open_grip", "close_grip", "hug_grasp", "dual_arm_sync"}

    @classmethod
    def parse_command(cls, payload: dict[str, Any]) -> Command:
        if not isinstance(payload, dict):
            raise MQTTAdapterError("payload must be a dict")
        cmd_type_str = payload.get("type")
        if cmd_type_str != "execute_task":
            raise MQTTAdapterError(f"unsupported type for loader: {cmd_type_str!r}")
        task_type = payload.get("task_type")
        if task_type not in cls.LOADER_TASK_TYPES:
            raise MQTTAdapterError(f"unknown loader task_type: {task_type!r}")
        parameters = payload.get("parameters") or {}
        if not isinstance(parameters, dict):
            raise MQTTAdapterError("parameters must be a dict")
        cmd = Command(
            type=CommandType.EXECUTE_TASK,
            task_type=task_type,
            parameters=parameters,
        )
        if "command_id" in payload and payload["command_id"] is not None:
            cmd.command_id = str(payload["command_id"])
        return cmd

    @staticmethod
    def format_status(joint_positions: list[float], joint_velocities: list[float]) -> dict:
        if len(joint_positions) != 14:
            raise MQTTAdapterError(f"loader expects 14 joints, got {len(joint_positions)}")
        return {
            "joint_positions": list(joint_positions),
            "joint_velocities": list(joint_velocities),
            "joint_names": [f"left_arm_{i}" for i in range(6)] + [f"right_arm_{i}" for i in range(6)] + ["left_gripper", "right_gripper"],
        }
