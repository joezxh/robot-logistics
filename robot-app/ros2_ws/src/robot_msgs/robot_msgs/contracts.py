"""Typed message contracts mirroring ``shared/contracts/*.schema.json``.

Every field name, type and default here is deliberately identical to the shared
JSON Schemas and to ``robot_contracts.payloads``. The gateway converts between
these dataclasses and the wire payloads, so any divergence would surface
immediately as a conversion error rather than as silent data loss.

Kept dependency-free on purpose (no rclpy, no pydantic): these types are
imported by unit tests that run without a ROS 2 environment.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Timestamp in the format used across the wire contract (UTC, ISO 8601)."""
    return datetime.now(timezone.utc).isoformat()

# Command types accepted by RCS. Mirrors ``CommandType`` in the shared contract
# and ``rcs.state.command.CommandType``.
COMMAND_TYPES: tuple[str, ...] = (
    "move_j",
    "move_l",
    "stop",
    "home",
    "estop",
    "recover",
    "execute_task",
)

# Task types for execute_task command.
TASK_TYPES: tuple[str, ...] = (
    "goto",
    "dock",
    "pick_box",
    "place_box",
    "transport",
    "hug_close",
    "hug_release",
    "home_all",
)

# Hug states.
HUG_STATES: tuple[str, ...] = ("closed", "holding", "open")

# Alert kinds published by the RCS ``EventBus``.
ALERT_KINDS: tuple[str, ...] = (
    "hal_read_timeout",
    "hal_write_failure",
    "controller_halted",
)


@dataclass(slots=True)
class Pose6DMsg:
    """Cartesian pose: metres for translation, radians for rotation."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rx: float = 0.0
    ry: float = 0.0
    rz: float = 0.0

    def to_dict(self) -> dict[str, float]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "rx": self.rx,
            "ry": self.ry,
            "rz": self.rz,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Pose6DMsg":
        return cls(
            x=float(data.get("x", 0.0)),
            y=float(data.get("y", 0.0)),
            z=float(data.get("z", 0.0)),
            rx=float(data.get("rx", 0.0)),
            ry=float(data.get("ry", 0.0)),
            rz=float(data.get("rz", 0.0)),
        )


@dataclass(slots=True)
class CommandMsg:
    """A motion command travelling downlink from RCS to the robot."""

    type: str
    command_id: str = ""
    target_pose: Pose6DMsg | None = None
    target_joints: list[float] | None = None
    speed_scale: float = 1.0
    constraints: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.type not in COMMAND_TYPES:
            raise ValueError(
                f"unknown command type {self.type!r}; expected one of {COMMAND_TYPES}"
            )
        if not 0.0 <= self.speed_scale <= 10.0:
            raise ValueError(f"speed_scale out of range: {self.speed_scale}")

    @property
    def is_emergency(self) -> bool:
        """E-stop bypasses the queue and must never be delayed or buffered."""
        return self.type == "estop"


@dataclass(slots=True)
class JointStateMsg:
    """Joint feedback. Matches ``rcs.state.joint.JointState``."""

    positions: list[float] = field(default_factory=list)
    velocities: list[float] = field(default_factory=list)
    efforts: list[float] = field(default_factory=list)
    timestamp_ns: int = 0
    device_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "positions": list(self.positions),
            "velocities": list(self.velocities),
            "efforts": list(self.efforts),
            "timestamp_ns": self.timestamp_ns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JointStateMsg":
        return cls(
            device_id=str(data.get("device_id", "")),
            positions=[float(v) for v in data.get("positions", [])],
            velocities=[float(v) for v in data.get("velocities", [])],
            efforts=[float(v) for v in data.get("efforts", [])],
            timestamp_ns=int(data.get("timestamp_ns", 0)),
        )


@dataclass(slots=True)
class TrackingErrorMsg:
    """Tracking error. Matches ``rcs.state.error.TrackingError``."""

    max_joint_error: float = 0.0
    position_error_m: float = 0.0
    timestamp_ns: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_joint_error": self.max_joint_error,
            "position_error_m": self.position_error_m,
            "timestamp_ns": self.timestamp_ns,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrackingErrorMsg":
        return cls(
            max_joint_error=float(data.get("max_joint_error", 0.0)),
            position_error_m=float(data.get("position_error_m", 0.0)),
            timestamp_ns=int(data.get("timestamp_ns", 0)),
        )


@dataclass(slots=True)
class ControllerStateMsg:
    """Controller mode snapshot. Matches ``rcs.state.controller_state``."""

    mode: str = "idle"
    active_command_id: str | None = None
    last_error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "active_command_id": self.active_command_id,
            "last_error": self.last_error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ControllerStateMsg":
        return cls(
            mode=str(data.get("mode", "idle")),
            active_command_id=data.get("active_command_id"),
            last_error=data.get("last_error"),
        )


@dataclass(slots=True)
class HugParamsMsg:
    """Parameters for hug grasp control."""

    pressure_target: float = 50.0
    approach_speed: float = 0.2
    close_speed: float = 0.05

    def to_dict(self) -> dict[str, float]:
        return {
            "pressure_target": self.pressure_target,
            "approach_speed": self.approach_speed,
            "close_speed": self.close_speed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HugParamsMsg":
        return cls(
            pressure_target=float(data.get("pressure_target", 50.0)),
            approach_speed=float(data.get("approach_speed", 0.2)),
            close_speed=float(data.get("close_speed", 0.05)),
        )


@dataclass(slots=True)
class TaskCommandMsg:
    """Task-level command for execute_task."""

    command_id: str = ""
    task_type: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    speed_scale: float = 1.0
    group: str | None = None

    def __post_init__(self) -> None:
        if self.task_type and self.task_type not in TASK_TYPES:
            raise ValueError(
                f"unknown task_type {self.task_type!r}; expected one of {TASK_TYPES}"
            )
        if not 0.0 <= self.speed_scale <= 10.0:
            raise ValueError(f"speed_scale out of range: {self.speed_scale}")


@dataclass(slots=True)
class BaseStateMsg:
    """AGV base state."""

    velocity: list[float] = field(default_factory=lambda: [0.0, 0.0])
    odom: dict[str, float] = field(default_factory=lambda: {"x": 0.0, "y": 0.0, "yaw": 0.0})
    battery_soc: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "velocity": list(self.velocity),
            "odom": dict(self.odom),
            "battery_soc": self.battery_soc,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseStateMsg":
        return cls(
            velocity=[float(v) for v in data.get("velocity", [0.0, 0.0])],
            odom={k: float(v) for k, v in (data.get("odom") or {"x": 0, "y": 0, "yaw": 0}).items()},
            battery_soc=float(data.get("battery_soc", 1.0)),
        )


@dataclass(slots=True)
class HugStateMsg:
    """Hug grasp state."""

    pressure_l: float = 0.0
    pressure_r: float = 0.0
    state: str = "open"

    def __post_init__(self) -> None:
        if self.state not in HUG_STATES:
            raise ValueError(f"unknown hug state {self.state!r}; expected one of {HUG_STATES}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "pressure_l": self.pressure_l,
            "pressure_r": self.pressure_r,
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "HugStateMsg":
        return cls(
            pressure_l=float(data.get("pressure_l", 0.0)),
            pressure_r=float(data.get("pressure_r", 0.0)),
            state=str(data.get("state", "open")),
        )


@dataclass(slots=True)
class RobotStateMsg:
    """Full robot state travelling uplink. Mirrors ``state.schema.json``.

    ``iso_ts`` is required by the wire contract; it defaults to "now" so callers
    constructing a frame by hand cannot accidentally emit an invalid payload.
    """

    device_id: str
    joint: JointStateMsg = field(default_factory=JointStateMsg)
    err: TrackingErrorMsg = field(default_factory=TrackingErrorMsg)
    ctrl: ControllerStateMsg = field(default_factory=ControllerStateMsg)
    base: BaseStateMsg | None = None
    hug: HugStateMsg | None = None
    iso_ts: str = ""
    degraded: bool = False

    def __post_init__(self) -> None:
        if not self.iso_ts:
            self.iso_ts = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "device_id": self.device_id,
            "joint": self.joint.to_dict(),
            "err": self.err.to_dict(),
            "ctrl": self.ctrl.to_dict(),
            "iso_ts": self.iso_ts,
            "degraded": self.degraded,
        }
        if self.base is not None:
            result["base"] = self.base.to_dict()
        if self.hug is not None:
            result["hug"] = self.hug.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RobotStateMsg":
        return cls(
            device_id=str(data["device_id"]),
            joint=JointStateMsg.from_dict(data.get("joint") or {}),
            err=TrackingErrorMsg.from_dict(data.get("err") or {}),
            ctrl=ControllerStateMsg.from_dict(data.get("ctrl") or {}),
            base=BaseStateMsg.from_dict(data["base"]) if data.get("base") else None,
            hug=HugStateMsg.from_dict(data["hug"]) if data.get("hug") else None,
            iso_ts=str(data.get("iso_ts", "")),
            degraded=bool(data.get("degraded", False)),
        )


@dataclass(slots=True)
class RobotTelemetryMsg:
    """Robot-originated health telemetry. Mirrors ``telemetry.schema.json``.

    Distinct from :class:`RobotStateMsg`: state is control feedback owned by
    RCS, telemetry is what only the robot itself can observe (battery, temps,
    connectivity). The contract splits it into numeric ``metrics`` and string
    ``status`` so consumers can chart the former without guessing at types.
    """

    device_id: str
    iso_ts: str = ""
    metrics: dict[str, float] = field(default_factory=dict)
    status: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.iso_ts:
            self.iso_ts = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "iso_ts": self.iso_ts,
            "metrics": dict(self.metrics),
            "status": dict(self.status),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RobotTelemetryMsg":
        return cls(
            device_id=str(data["device_id"]),
            iso_ts=str(data.get("iso_ts", "")),
            metrics={k: float(v) for k, v in (data.get("metrics") or {}).items()},
            status={k: str(v) for k, v in (data.get("status") or {}).items()},
        )


@dataclass(slots=True)
class AlertMsg:
    """Fault event forwarded from the RCS ``EventBus``."""

    device_id: str
    event: str
    error: str | None = None
    iso_ts: str = ""

    def __post_init__(self) -> None:
        if self.event not in ALERT_KINDS:
            raise ValueError(
                f"unknown alert event {self.event!r}; expected one of {ALERT_KINDS}"
            )
        if not self.iso_ts:
            self.iso_ts = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        return {
            "device_id": self.device_id,
            "event": self.event,
            "error": self.error,
            "iso_ts": self.iso_ts,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AlertMsg":
        return cls(
            device_id=str(data["device_id"]),
            event=str(data.get("event", "")),
            error=data.get("error"),
            iso_ts=str(data.get("iso_ts", "")),
        )


@dataclass(slots=True)
class MoveCommandGoal:
    """Goal half of the move action the gateway offers to local ROS 2 nodes.

    The gateway is the only producer today (it converts incoming
    :class:`CommandMsg` into these), but exposing it as an explicit contract
    lets ``robot_decision`` issue local motions through the same path.
    """

    command_id: str
    type: str
    target_joints: list[float] = field(default_factory=list)
    target_pose: Pose6DMsg | None = None
    speed_scale: float = 1.0


@dataclass(slots=True)
class MoveCommandResult:
    """Result half of the move action."""

    command_id: str
    success: bool
    message: str = ""
