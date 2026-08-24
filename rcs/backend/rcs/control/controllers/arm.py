"""6-DOF arm controller: PD control in joint space + IK on move_l.

支持从 ArmSpec 动态加载 DH 参数，不再硬编码。
"""
from __future__ import annotations
import math
import numpy as np

from ..state.profile import DeviceProfile, Morphology
from ..state.joint import JointState
from ..state.command import Command, CommandType
from ..state.error import TrackingError
from ..state.controller_state import ControllerState, ControllerMode
from .base import Controller
from ._common import CommandQueue, clip_to_limits, abs_max
from ..planning import fk, ik
from ..planning.trajectory import plan_trapezoidal, Trajectory
from ..planning.interpolator import Interpolator
from ..devices import get_arm_spec, ARM_6DOF_STANDARD


# 向后兼容：保留 ARM_DH 作为默认值（与 ARM_6DOF_STANDARD 一致）
ARM_DH = [
    (0.0,  0.10,  math.pi / 2, 0.0),
    (0.3,  0.0,   0.0,         0.0),
    (0.2,  0.0,   math.pi / 2, 0.0),
    (0.0,  0.10, -math.pi / 2, 0.0),
    (0.0,  0.05,  math.pi / 2, 0.0),
    (0.0,  0.04,  0.0,         0.0),
]


class ArmController(Controller):
    morphology = Morphology.ARM

    def __init__(self, profile: DeviceProfile, dh_params: list | None = None) -> None:
        super().__init__(profile)

        # 优先使用传入的 DH 参数，否则尝试从 ArmSpec 加载
        self._dh_params = dh_params or self._load_dh_from_profile(profile)

        # Note: spec calls for kp=80, kd=8 in absolute torque units (Nm/(rad,rad/s))
        # but that requires a torque-mode HAL; with our position-only SimHAL the
        # controller's own `self._q` (not HAL feedback) is fed back through PD,
        # so for in-process convergence we use normalised per-tick gains.
        self._kp = 0.3
        self._kd = 0.5
        self._q: list[float] = list(profile.home_joints)
        self._qdot: list[float] = [0.0] * profile.num_joints
        self._last_target: list[float] = list(profile.home_joints)
        self._interp: Interpolator | None = None
        self._queue: CommandQueue = CommandQueue(maxsize=1024)

    def _load_dh_from_profile(self, profile: DeviceProfile) -> list:
        """从设备配置加载 DH 参数

        优先级：
        1. profile.extra['dh_params'] 自定义参数
        2. profile.extra['arm_spec'] 从 ArmSpec 库获取
        3. ARM_DH 默认值
        """
        extra = getattr(profile, "extra", None) or {}

        # 1. 尝试从 ArmSpec 获取
        arm_spec_name = extra.get("arm_spec")
        if arm_spec_name:
            try:
                spec = get_arm_spec(arm_spec_name)
                return spec.to_dh_list()
            except KeyError:
                pass

        # 2. 尝试使用内联 DH 参数
        inline_dh = extra.get("dh_params")
        if inline_dh:
            return inline_dh

        # 3. 回退到默认 ARM_DH
        return ARM_DH

    def on_command(self, cmd: Command) -> None:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            return
        # Idempotency: CommandQueue rejects a duplicate command_id silently.
        if not self._queue.push(cmd):
            return
        if cmd.type == CommandType.STOP:
            target = list(self._q)
        elif cmd.type == CommandType.HOME:
            target = list(self.profile.home_joints)
        elif cmd.type == CommandType.MOVE_J and cmd.target_joints is not None:
            target = clip_to_limits(cmd.target_joints, self.profile.limits.pos_lower, self.profile.limits.pos_upper)
        elif cmd.type == CommandType.MOVE_L and cmd.target_pose is not None:
            T = np.eye(4)
            T[:3, 3] = cmd.target_pose.position
            # 使用实例的 DH 参数进行 IK
            try:
                q_sol = list(
                    ik(
                        self._q,
                        self._dh_params,
                        T,
                        self.profile.limits.pos_lower,
                        self.profile.limits.pos_upper,
                    )
                )
            except Exception as exc:
                self.state.last_error = f"ik failed: {exc}"
                return
            target = q_sol
        else:
            return
        vmax = self.profile.limits.vel_max
        amax = self.profile.limits.acc_max
        traj = plan_trapezoidal(self._q, target, vmax, amax)
        self._interp = Interpolator(traj, step_s=1.0 / self.profile.control_hz)
        self.state.mode = ControllerMode.RUNNING
        self.state.active_command_id = cmd.command_id

    def update(self, hal_state: JointState) -> JointState:
        if self.state.mode in (ControllerMode.HALTED, ControllerMode.FAULT, ControllerMode.E_STOP):
            # Brake: hold last command at zero velocity target.
            target = list(self._q)
        elif self._interp is not None and not self._interp.done:
            target = self._interp.next()
        else:
            target = list(self._q)
        # PD control.
        pos = list(hal_state.positions)
        out_positions = [
            self._q[i] + self._kp * (target[i] - self._q[i]) - self._kd * self._qdot[i]
            for i in range(len(target))
        ]
        out_positions = clip_to_limits(out_positions, self.profile.limits.pos_lower, self.profile.limits.pos_upper)
        self._qdot = [out_positions[i] - self._q[i] for i in range(len(out_positions))]
        self._q = out_positions
        self._last_target = target
        return JointState(
            positions=list(out_positions),
            velocities=list(self._qdot),
            efforts=[0.0] * len(out_positions),
            device_id=self.profile.device_id,
        )

    def tracking_error(self, target: JointState, current: JointState) -> TrackingError:
        max_joint = abs_max([target.positions[i] - current.positions[i] for i in range(len(target.positions))])
        if max_joint > self.profile.limits.rad_th:
            self.halt()
        return TrackingError(max_joint_error=max_joint, position_error_m=0.0)
