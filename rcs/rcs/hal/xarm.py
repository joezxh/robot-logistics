"""XArm7 真实硬件 HAL

使用 xarm 库控制真实 XArm 机器人。
"""
from __future__ import annotations

from typing import Any

import numpy as np

from .base import HardwareHAL, HALState, HALTimeout


class XArmHAL(HardwareHAL):
    """XArm7 硬件驱动

    使用 xarm SDK 控制真实 XArm 机器人。
    """

    def __init__(
        self,
        host: str = "192.168.1.200",
        port: int = 5004,
        dof: int = 7,
    ):
        super().__init__(host, port)
        self._dof = dof
        self._arm = None

    def connect(self) -> None:
        try:
            from xarm.wrapper import XArmAPI
        except ImportError:
            raise ImportError(
                "xarm-sdk required for XArm hardware; "
                "install via: pip install xarm-sdk"
            )

        self._arm = XArmAPI(self._host)
        self._connected = True

    def disconnect(self) -> None:
        if self._arm:
            self._arm.disconnect()
            self._arm = None
        self._connected = False

    def read_state(self, timeout_ms: int = 1000) -> HALState:
        if not self._connected or self._arm is None:
            raise HALTimeout("Not connected")

        state = self._arm.state
        if state != 0:  # 0 = normal
            raise HALTimeout(f"Robot in error state: {state}")

        # 读取关节位置
        joint_positions = np.array(self._armAngles if hasattr(self, '_armAngles') else [0] * self._dof)
        joint_velocities = np.array([0.0] * self._dof)
        joint_efforts = np.array([0.0] * self._dof)

        # 读取末端位置
        tcp_pose = self._arm.position
        cartesian_pose = np.array([
            tcp_pose[0], tcp_pose[1], tcp_pose[2],
            0, 0, 0, 1  # 简化：使用默认四元数
        ])

        wrench = np.zeros(6)

        return HALState(
            joint_positions=joint_positions,
            joint_velocities=joint_velocities,
            joint_efforts=joint_efforts,
            cartesian_pose=cartesian_pose,
            wrench=wrench,
            timestamp=0.0,
            gripper_position=0.0,
        )

    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        if not self._connected or self._arm is None:
            raise RuntimeError("Not connected")

        if joint_positions is not None:
            positions = joint_positions.tolist()
            self._arm.set_servo_angle(angle=positions, wait=True)

        if gripper_position is not None:
            # XArm 夹爪控制
            self._arm.set_gripper_position(gripper_position * 100, wait=True)

    def estop(self) -> None:
        if self._arm:
            self._arm.emergency_stop()

    def recover(self) -> None:
        if self._arm:
            self._arm.motion_enable(True)

    def base_pose(self) -> dict:
        """XArm 基座姿态"""
        return {
            "translation": [0.0, 0.0, 0.0],
            "quaternion": [0.0, 0.0, 0.0, 1.0],  # xyzw
        }


__all__ = ["XArmHAL"]
