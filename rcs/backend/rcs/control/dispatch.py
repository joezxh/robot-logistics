"""Single command-dispatch path shared by the REST router and the MQTT adapter.

Both entry points funnel through :func:`dispatch_command` so a command arriving
over MQTT cannot behave differently from the same command arriving over REST.
The function is transport-agnostic: it raises :class:`DispatchError` with a
machine-readable ``code``, and each transport maps that to its own error
representation (HTTP status / MQTT log).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

from .registry import registry
from .state.command import Command, CommandType
from .state.pose import Pose6D

# Match the controller's per-device queue capacity. Mirrors
# `ArmController._queue.maxsize` (kept identical to avoid silent backpressure
# drift between the transports and the controller's actual queue).
COMMAND_QUEUE_MAXSIZE = 1024


class DispatchError(Exception):
    """Command could not be dispatched.

    ``code`` is one of: ``unknown_device``, ``device_locked``, ``queue_full``.
    """

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass
class DispatchResult:
    status: str  # "queued" | "estop" | "recover"
    device_id: str
    command_id: str | None = None


def dispatch_command(
    device_id: str,
    *,
    type: str,
    command_id: str | None = None,
    target_pose: Pose6D | None = None,
    target_joints: list[float] | None = None,
    speed_scale: float = 1.0,
    constraints: dict | None = None,
) -> DispatchResult:
    """Validate, then hand the command to the device controller.

    Safety commands (``estop`` / ``recover``) bypass the queue by design so they
    take effect even when the queue is saturated.
    """
    try:
        ctrl = registry.get_controller(device_id)
    except KeyError:
        raise DispatchError("unknown_device", f"unknown device_id: {device_id}") from None

    if registry.get_profile(device_id).locked:
        raise DispatchError("device_locked", "device is locked")

    if type == "estop":
        ctrl.estop()
        return DispatchResult(status="estop", device_id=device_id)
    if type == "recover":
        ctrl.recover()
        return DispatchResult(status="recover", device_id=device_id)

    cmd = Command(
        command_id=command_id or uuid.uuid4().hex,
        type=CommandType(type),
        target_pose=target_pose,
        target_joints=target_joints,
        speed_scale=speed_scale,
        constraints=constraints,
    )

    if hasattr(ctrl, "_queue") and len(ctrl._queue) >= COMMAND_QUEUE_MAXSIZE:
        raise DispatchError("queue_full", "command queue full")

    ctrl.on_command(cmd)
    return DispatchResult(status="queued", device_id=device_id, command_id=cmd.command_id)
