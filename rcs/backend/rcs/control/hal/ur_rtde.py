"""UR5e/UR10 真实硬件 HAL

使用 ur_rtde 控制真实 UR 机器人。
"""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from .base import HardwareHAL, HALState, HALTimeout


class URRTDEHAL(HardwareHAL):
    """UR5e/UR10 硬件驱动 (ur_rtde)

    使用 UR 的 RTDE 协议读取状态和发送命令。
    """

    def __init__(
        self,
        host: str,
        port: int = 30004,
        gripper_type: str = "robotiq",
    ):
        super().__init__(host, port)
        self._rtde = None
        self._gripper_type = gripper_type
        self._input_register = None

    def connect(self) -> None:
        try:
            import rtde.rtde as rtde
        except ImportError:
            raise ImportError(
                "ur-rtde required for UR hardware; "
                "install via: pip install ur-rtde"
            )

        self._rtde = rtde.RTDE(self._host, self._port)
        self._rtde.connect()

        # 配置要读取的变量
        self._rtde.get_controller_version()
        self._rtde.send_start()

        self._connected = True

    def disconnect(self) -> None:
        if self._rtde:
            self._rtde.send_pause()
            self._rtde.disconnect()
            self._rtde = None
        self._connected = False

    def read_state(self, timeout_ms: int = 1000) -> HALState:
        if not self._connected or self._rtde is None:
            raise HALTimeout("Not connected")

        try:
            state = self._rtde.receive(timeout_ms / 1000)
        except Exception as e:
            raise HALTimeout(f"Receive timeout: {e}")

        return HALState(
            joint_positions=np.array(state.actual_q),
            joint_velocities=np.array(state.actual_qd),
            joint_efforts=np.array(state.actual_TCP_force[:6]),
            cartesian_pose=self._get_cartesian_pose(state),
            wrench=np.concatenate([state.actual_TCP_force, [0, 0, 0]]),
            timestamp=time.time(),
            gripper_position=0.0,
        )

    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        if not self._connected or self._rtde is None:
            raise RuntimeError("Not connected")

        if joint_positions is not None:
            import rtde.csv_writer as csv_writer
            setp = joint_positions.tolist()
            self._rtde.send(
                ["speed_slider_mask", "speed_slider_ratio"],
                [[0, 0.5]],
            )

    def estop(self) -> None:
        if self._rtde:
            self._rtde.send_stop()

    def recover(self) -> None:
        pass  # UR 通常自动恢复

    def base_pose(self) -> dict:
        """UR 基座姿态（通常固定在地面坐标系）"""
        return {
            "translation": [0.0, 0.0, 0.0],
            "quaternion": [0.0, 0.0, 0.0, 1.0],  # xyzw
        }

    def _get_cartesian_pose(self, state) -> np.ndarray:
        """从 RTDE 状态提取笛卡尔姿态"""
        t = np.array(state.actual_TCP_pose[:3])
        rpy = state.actual_TCP_pose[3:6]
        q = self._rpy_to_quaternion(rpy)
        return np.concatenate([t, q])

    @staticmethod
    def _rpy_to_quaternion(rpy: list) -> np.ndarray:
        """RPY (rad) -> xyzw 四元数"""
        import math
        r, p, y = rpy
        cy, sy = math.cos(y / 2), math.sin(y / 2)
        cp, sp = math.cos(p / 2), math.sin(p / 2)
        cr, sr = math.cos(r / 2), math.sin(r / 2)
        qw = cr * cp * cy + sr * sp * sy
        qx = sr * cp * cy - cr * sp * sy
        qy = cr * sp * cy + sr * cp * sy
        qz = cr * cp * sy - sr * sp * cy
        return np.array([qx, qy, qz, qw])


__all__ = ["URRTDEHAL"]
