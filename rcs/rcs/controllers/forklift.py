"""Forklift controller: 3 independent PID joints (travel/lift/extend).

Task types dispatched via ``Command.task_type`` (when ``Command.type ==
CommandType.EXECUTE_TASK``):
    - ``extend_fork``   parameters: {"extension_m": float}
    - ``lift_fork``     parameters: {"height_m": float}
    - ``move_to``       parameters: {"x": float}  (travel only)
    - ``drop_pallet``   parameters: {"stage": "lower"|"open"|"retract"}
    - ``pick_pallet``   parameters: {"stage": "approach"|"insert"|"lift"}
"""
from __future__ import annotations

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import abs_max
from ..devices import ForkliftSpec


class ForkliftController(Controller):
    morphology = Morphology.ARM

    VALID_TASK_TYPES = {"extend_fork", "lift_fork", "move_to", "drop_pallet", "pick_pallet"}

    def __init__(self, profile: DeviceProfile, spec: ForkliftSpec) -> None:
        super().__init__(profile)
        self.spec = spec
        self._q: list[float] = list(profile.home_joints)
        self._qdot: list[float] = [0.0] * 3
        self._kp = [spec.kp_travel, spec.kp_lift, spec.kp_extend]
        self._kd = [spec.kd_travel, spec.kd_lift, spec.kd_extend]
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
            self.state.last_error = f"unknown forklift task_type: {task_type!r}"
            return
        target = list(self._target)  # preserve previous target across sequential commands
        if task_type == "extend_fork":
            target[2] = float(params.get("extension_m", 0.0))
        elif task_type == "lift_fork":
            target[1] = float(params.get("height_m", 0.0))
        elif task_type == "move_to":
            target[0] = float(params.get("x", 0.0))
        elif task_type == "drop_pallet":
            stage = params.get("stage", "lower")
            if stage == "lower":
                target[1] = 0.05
            elif stage == "open":
                target[2] = 0.0
            elif stage == "retract":
                target[0] = 0.0
        elif task_type == "pick_pallet":
            stage = params.get("stage", "approach")
            if stage == "approach":
                target[0] = float(params.get("approach_m", 1.5))
            elif stage == "insert":
                target[2] = 0.4
            elif stage == "lift":
                target[1] = float(params.get("lift_m", 0.3))
        target = [max(self._limits[0][i], min(self._limits[1][i], target[i])) for i in range(3)]
        self._target = target
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        target = getattr(self, "_target", self._q)
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            target = list(self._q)
        out = [0.0] * 3
        for i in range(3):
            err = target[i] - self._q[i]
            out[i] = self._q[i] + self._kp[i] * err - self._kd[i] * self._qdot[i]
            out[i] = max(self._limits[0][i], min(self._limits[1][i], out[i]))
        self._qdot = [out[i] - self._q[i] for i in range(3)]
        self._q = out
        return JointState(
            positions=list(out),
            velocities=list(self._qdot),
            efforts=[0.0] * 3,
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max([target.positions[i] - current.positions[i] for i in range(len(target.positions))])
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
