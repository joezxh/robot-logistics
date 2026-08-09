"""Differential-drive AGV controller: 2 joints (left/right wheel velocity)."""
from __future__ import annotations
import math

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import CommandQueue, clip_to_limits, abs_max
from ..planning.trajectory import plan_trapezoidal, Trajectory
from ..planning.interpolator import Interpolator


class AgvController(Controller):
    morphology = Morphology.AGV

    def __init__(self, profile: DeviceProfile) -> None:
        super().__init__(profile)
        self._p = 1.5
        self._q: list[float] = [0.0] * 2  # linear, angular velocity
        self._interp: Interpolator | None = None
        self._queue: CommandQueue = CommandQueue(maxsize=1024)

    def on_command(self, cmd: Command) -> None:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            return
        if cmd.type == CommandType.STOP:
            target = [0.0, 0.0]
        elif cmd.type == CommandType.MOVE_J and cmd.target_joints is not None:
            target = clip_to_limits(cmd.target_joints, [-2.0, -2.0], [2.0, 2.0])
        else:
            return
        vmax = self.profile.limits.vel_max or [1.0, 1.0]
        amax = self.profile.limits.acc_max or [2.0, 2.0]
        traj = plan_trapezoidal(self._q, target, vmax, amax)
        self._interp = Interpolator(traj, step_s=1.0 / self.profile.control_hz)
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            target = [0.0, 0.0]
        elif self._interp is not None and not self._interp.done:
            target = self._interp.next()
        else:
            target = list(self._q)
        out = [self._q[i] + self._p * (target[i] - self._q[i]) for i in range(len(target))]
        self._q = out
        return JointState(
            positions=list(out),
            velocities=[0.0, 0.0],
            efforts=[0.0, 0.0],
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max([target.positions[i] - current.positions[i] for i in range(len(target.positions))])
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
