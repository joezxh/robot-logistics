"""Dual-arm loading robot controller: 6+6 dual PD with gripper joints.

Task types dispatched via ``Command.task_type`` (when ``Command.type ==
CommandType.EXECUTE_TASK``):
    - ``open_grip``        parameters: {"gripper": "left"|"right"|"both"}
    - ``close_grip``       parameters: {"gripper": "left"|"right"|"both", "force_n": float}
    - ``hug_grasp``        parameters: {"object_width_m": float, "approach_speed": float}
    - ``dual_arm_sync``    parameters: {"left_target": float, "right_target": float}
"""
from __future__ import annotations

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import abs_max
from ..devices import DualArmLoaderSpec


class DualArmLoaderController(Controller):
    morphology = Morphology.ARM

    VALID_TASK_TYPES = {"open_grip", "close_grip", "hug_grasp", "dual_arm_sync"}

    def __init__(self, profile: DeviceProfile, spec: DualArmLoaderSpec) -> None:
        super().__init__(profile)
        self.spec = spec
        self._q: list[float] = list(profile.home_joints)
        self._qdot: list[float] = [0.0] * 14
        self._kp: list[float] = [spec.kp] * 14
        self._kd: list[float] = [spec.kd] * 14
        self._limits = spec.joint_limits()
        self._target: list[float] = list(self._q)

    def on_command(self, cmd: Command) -> None:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            return
        if cmd.type != CommandType.EXECUTE_TASK:
            return
        task_type = getattr(cmd, "task_type", None)
        params = getattr(cmd, "parameters", None) or {}
        if task_type not in self.VALID_TASK_TYPES:
            self.state.last_error = f"unknown loader task_type: {task_type!r}"
            return
        target = list(self._target)  # preserve previous target across sequential commands
        if task_type == "open_grip":
            gripper = params.get("gripper", "both")
            if gripper in ("both", "left"):
                target[12] = 0.0
            if gripper in ("both", "right"):
                target[13] = 0.0
        elif task_type == "close_grip":
            gripper = params.get("gripper", "both")
            if gripper in ("both", "left"):
                target[12] = 1.0
            if gripper in ("both", "right"):
                target[13] = 1.0
        elif task_type == "hug_grasp":
            target[0] = 0.1
            target[6] = -0.1
        elif task_type == "dual_arm_sync":
            target[0] = float(params.get("left_target", 0.0))
            target[6] = float(params.get("right_target", 0.0))
        target = [
            max(self._limits[0][i], min(self._limits[1][i], target[i]))
            for i in range(len(target))
        ]
        self._target = target
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        target = getattr(self, "_target", self._q)
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            target = list(self._q)
        out = [0.0] * 14
        for i in range(len(self._q)):
            err = target[i] - self._q[i]
            out[i] = self._q[i] + self._kp[i] * err - self._kd[i] * self._qdot[i]
            out[i] = max(self._limits[0][i], min(self._limits[1][i], out[i]))
        self._qdot = [out[i] - self._q[i] for i in range(len(self._q))]
        self._q = out
        return JointState(
            positions=list(out),
            velocities=list(self._qdot),
            efforts=[0.0] * len(self._q),
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max(
            [target.positions[i] - current.positions[i] for i in range(len(target.positions))]
        )
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
