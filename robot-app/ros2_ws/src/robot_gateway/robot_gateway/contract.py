"""Wire <-> local conversion for the MQTT bridge.

Two type families meet here:

* ``robot_contracts`` (from ``shared/python``) — the *wire* contract, shared
  byte-for-byte with RCS.
* ``robot_msgs`` — the *local* ROS-side contract.

Keeping the conversion in one module means a contract change breaks exactly one
file, and it lets the bridge node stay free of serialization details.

``robot_contracts`` is an optional import: it needs pydantic, which is present
in the RCS/venv environment but not necessarily inside a bare ROS 2 runtime.
When it is unavailable we fall back to plain ``json`` plus the dataclass
validation in ``robot_msgs`` — slightly weaker, but the bridge still runs.
"""
from __future__ import annotations

import json
import logging
from typing import Any

from robot_msgs import (
    AlertMsg,
    CommandMsg,
    Pose6DMsg,
    RobotStateMsg,
    RobotTelemetryMsg,
    TaskCommandMsg,
)

logger = logging.getLogger(__name__)

try:  # pragma: no cover - depends on deployment environment
    from robot_contracts import AlertPayload, CommandPayload, StatePayload, TelemetryPayload

    _HAVE_PYDANTIC_CONTRACTS = True
except Exception:  # pragma: no cover - bare ROS 2 runtime without pydantic
    _HAVE_PYDANTIC_CONTRACTS = False
    logger.info(
        "robot_contracts unavailable; falling back to json + dataclass validation"
    )


class ContractError(ValueError):
    """Raised when a payload cannot be decoded into the agreed contract."""


# --- downlink: MQTT bytes -> local command ---------------------------------


def decode_command(raw: bytes) -> CommandMsg:
    """Decode a command payload received on ``rcs/{device_id}/command``."""
    if _HAVE_PYDANTIC_CONTRACTS:
        try:
            payload = CommandPayload.model_validate_json(raw)
        except Exception as exc:
            raise ContractError(f"invalid command payload: {exc}") from exc
        pose = None
        if payload.target_pose is not None:
            pose = Pose6DMsg(**payload.target_pose.model_dump())
        return CommandMsg(
            type=payload.type.value,
            command_id=payload.command_id or "",
            target_pose=pose,
            target_joints=payload.target_joints,
            speed_scale=payload.speed_scale,
            constraints=payload.constraints or {},
        )

    data = _loads(raw)
    pose_raw = data.get("target_pose")
    try:
        return CommandMsg(
            type=str(data["type"]),
            command_id=str(data.get("command_id") or ""),
            target_pose=Pose6DMsg.from_dict(pose_raw) if pose_raw else None,
            target_joints=data.get("target_joints"),
            speed_scale=float(data.get("speed_scale", 1.0)),
            constraints=dict(data.get("constraints") or {}),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError(f"invalid command payload: {exc}") from exc


def decode_task_command(raw: bytes) -> TaskCommandMsg:
    """Decode an execute_task command payload."""
    data = _loads(raw)
    task_type = str(data.get("task_type", ""))
    if not task_type:
        raise ContractError("execute_task requires task_type")
    try:
        return TaskCommandMsg(
            command_id=str(data.get("command_id") or ""),
            task_type=task_type,
            parameters=dict(data.get("parameters") or {}),
            speed_scale=float(data.get("speed_scale", 1.0)),
            group=data.get("group"),
        )
    except (ValueError, TypeError) as exc:
        raise ContractError(f"invalid execute_task payload: {exc}") from exc


# --- uplink: local messages -> MQTT bytes -----------------------------------


def encode_state(state: RobotStateMsg) -> bytes:
    """Encode robot state for ``rcs/{device_id}/state``."""
    payload = state.to_dict()
    if _HAVE_PYDANTIC_CONTRACTS:
        # Round-trip through the shared model so a schema violation is caught
        # here, on our side, rather than silently reaching RCS.
        return StatePayload.model_validate(payload).model_dump_json().encode()
    return _dumps(payload)


def encode_telemetry(telemetry: RobotTelemetryMsg) -> bytes:
    """Encode telemetry for ``robot/{device_id}/telemetry``."""
    payload = telemetry.to_dict()
    if _HAVE_PYDANTIC_CONTRACTS:
        return TelemetryPayload.model_validate(payload).model_dump_json().encode()
    return _dumps(payload)


def encode_alert(alert: AlertMsg) -> bytes:
    """Encode an alert for ``rcs/{device_id}/alert``."""
    payload = alert.to_dict()
    if _HAVE_PYDANTIC_CONTRACTS:
        return AlertPayload.model_validate(payload).model_dump_json().encode()
    return _dumps(payload)


def decode_alert(raw: bytes) -> AlertMsg:
    """Decode an alert -- used when the robot subscribes to RCS fault events."""
    try:
        return AlertMsg.from_dict(_loads(raw))
    except (KeyError, TypeError, ValueError) as exc:
        raise ContractError(f"invalid alert payload: {exc}") from exc


# --- helpers ----------------------------------------------------------------


def _loads(raw: bytes) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractError(f"payload is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"payload must be a JSON object, got {type(data).__name__}")
    return data


def _dumps(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode()
