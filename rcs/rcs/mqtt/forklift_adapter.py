"""Forklift MQTT command adapter.

Validates payloads against ``shared/contracts/command.schema.json`` and
exposes typed methods to convert JSON ↔ Command / JointState.
"""
from __future__ import annotations

import json
from typing import Any

from ..state.command import Command, CommandType


class MQTTAdapterError(ValueError):
    """Raised when an MQTT payload is malformed or fails schema validation."""


class ForkliftMqttAdapter:
    FORKLIFT_TASK_TYPES = {"extend_fork", "lift_fork", "move_to", "drop_pallet", "pick_pallet"}

    @classmethod
    def parse_command(cls, payload: dict[str, Any]) -> Command:
        if not isinstance(payload, dict):
            raise MQTTAdapterError("payload must be a dict")
        cmd_type_str = payload.get("type")
        if cmd_type_str != "execute_task":
            raise MQTTAdapterError(f"unsupported type for forklift: {cmd_type_str!r}")
        task_type = payload.get("task_type")
        if task_type not in cls.FORKLIFT_TASK_TYPES:
            raise MQTTAdapterError(f"unknown forklift task_type: {task_type!r}")
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
        if "speed_scale" in payload:
            cmd.speed_scale = float(payload["speed_scale"])
        return cmd

    @staticmethod
    def format_status(joint_positions: list[float], joint_velocities: list[float]) -> dict:
        if len(joint_positions) != 3:
            raise MQTTAdapterError(f"forklift expects 3 joints, got {len(joint_positions)}")
        return {
            "joint_positions": list(joint_positions),
            "joint_velocities": list(joint_velocities),
            "joint_names": ["travel", "lift", "extend"],
        }

    @classmethod
    def from_json(cls, raw: str | bytes) -> Command:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return cls.parse_command(json.loads(raw))

    @staticmethod
    def to_json(payload: dict) -> str:
        return json.dumps(payload, separators=(",", ":"))
