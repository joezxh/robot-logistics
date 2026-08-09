"""Pydantic payload models for the RCS <-> robot-app MQTT bus.

These are the single source of truth for wire format. They mirror the JSON
Schemas in ``shared/contracts/*.schema.json`` and are deliberately aligned
field-for-field with the RCS REST models (``rcs.service.CommandRequest`` and
``rcs.state.state_stream.StateFrame``) so that a command arriving over MQTT
behaves identically to the same command arriving over REST.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CommandTypeEnum(str, Enum):
    """Mirrors ``rcs.state.command.CommandType``."""

    MOVE_J = "move_j"
    MOVE_L = "move_l"
    STOP = "stop"
    HOME = "home"
    ESTOP = "estop"
    RECOVER = "recover"
    EXECUTE_TASK = "execute_task"


class Pose6DPayload(BaseModel):
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float


class CommandPayload(BaseModel):
    """Downlink command. Field-identical to the REST ``CommandRequest``."""

    command_id: str | None = None
    type: CommandTypeEnum
    target_pose: Pose6DPayload | None = None
    target_joints: list[float] | None = None
    speed_scale: float = Field(default=1.0, ge=0.0, le=10.0)
    constraints: dict[str, Any] | None = None
    task_type: str | None = None
    parameters: dict[str, Any] | None = None
    group: str | None = None


class JointStatePayload(BaseModel):
    device_id: str = ""
    positions: list[float] = Field(default_factory=list)
    velocities: list[float] = Field(default_factory=list)
    efforts: list[float] = Field(default_factory=list)
    timestamp_ns: int = 0


class TrackingErrorPayload(BaseModel):
    max_joint_error: float = 0.0
    position_error_m: float = 0.0
    timestamp_ns: int = 0


class ControllerStatePayload(BaseModel):
    mode: str
    phase: str | None = None
    active_command_id: str | None = None
    last_error: str | None = None


class BaseStatePayload(BaseModel):
    """AGV base state."""

    velocity: list[float] = Field(default_factory=lambda: [0.0, 0.0])
    odom: dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0, "yaw": 0.0})
    battery_soc: float = 1.0


class HugStatePayload(BaseModel):
    """Hug grasp state."""

    pressure_l: float = 0.0
    pressure_r: float = 0.0
    state: str = "open"


class StatePayload(BaseModel):
    """Uplink state frame. Mirrors ``StateStream``'s emitted JSON."""

    device_id: str
    joint: JointStatePayload | None = None
    err: TrackingErrorPayload | None = None
    ctrl: ControllerStatePayload | None = None
    base: BaseStatePayload | None = None
    hug: HugStatePayload | None = None
    iso_ts: str
    # Set when the frame exceeded the 64 KB cap and was reduced.
    degraded: bool = False

    model_config = {"extra": "allow"}


class AlertEventEnum(str, Enum):
    """The three events published on ``rcs.events.EventBus``."""

    HAL_READ_TIMEOUT = "hal_read_timeout"
    HAL_WRITE_FAILURE = "hal_write_failure"
    CONTROLLER_HALTED = "controller_halted"


class AlertPayload(BaseModel):
    event: AlertEventEnum
    device_id: str
    error: str | None = None
    iso_ts: str


class TelemetryPayload(BaseModel):
    """Uplink telemetry from the robot-side application to RCS."""

    device_id: str
    iso_ts: str
    # Free-form measurements (battery, temperature, payload weight, ...).
    metrics: dict[str, float] = Field(default_factory=dict)
    # Free-form status strings (firmware version, current task, ...).
    status: dict[str, str] = Field(default_factory=dict)


class HugParamsPayload(BaseModel):
    """Parameters for hug grasp control."""

    pressure_target: float = 50.0
    approach_speed: float = 0.2
    close_speed: float = 0.05


class TaskCommandPayload(BaseModel):
    """Task-level command for execute_task."""

    command_id: str | None = None
    task_type: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    speed_scale: float = Field(default=1.0, ge=0.0, le=10.0)
    group: str | None = None


__all__ = [
    "CommandTypeEnum",
    "Pose6DPayload",
    "CommandPayload",
    "JointStatePayload",
    "TrackingErrorPayload",
    "ControllerStatePayload",
    "StatePayload",
    "AlertEventEnum",
    "AlertPayload",
    "TelemetryPayload",
    "HugParamsPayload",
    "TaskCommandPayload",
    "BaseStatePayload",
    "HugStatePayload",
]
