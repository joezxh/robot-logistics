"""Franka FR3/Panda 真实硬件 HAL

使用 libfranka 控制真实 Franka 机器人。
"""
from __future__ import annotations

from typing import Any

import numpy as np

from .base import HardwareHAL, HALState, HALTimeout


class FrankaHAL(HardwareHAL):
    """Franka FR3/Panda 硬件驱动

    使用 libfranka 控制真实 Franka 机器人。
    """

    def __init__(
        self,
        host: str,
        port: int = 50051,
        gripper_host: str | None = None,
    ):
        super().__init__(host, port)
        self._robot = None
        self._gripper = None
        self._gripper_host = gripper_host or host

    def connect(self) -> None:
        try:
            import libfranka
        except ImportError:
            raise ImportError(
                "libfranka required for Franka hardware; "
                "install via: pip install libfranka"
            )

        self._robot = libfranka.Robot(self._host)
        self._robot.automatic_error_recovery = True

        try:
            import libfranka.gripper
            self._gripper = libfranka.gripper.Gripper(self._gripper_host)
        except Exception:
            self._gripper = None

        self._connected = True

    def disconnect(self) -> None:
        if self._robot:
            self._robot = None
        self._connected = False

    def read_state(self, timeout_ms: int = 1000) -> HALState:
        if not self._connected or self._robot is None:
            raise HALTimeout("Not connected")

        try:
            state = self._robot.read_once()
        except Exception as e:
            raise HALTimeout(f"Read timeout: {e}")

        return HALState(
            joint_positions=np.array(state.q),
            joint_velocities=np.array(state.dq),
            joint_efforts=np.array(state.tau_J),
            cartesian_pose=self._ee_pose_from_T(state.O_T_EE),
            wrench=np.array(state.O_F_ext_hat_K),
            timestamp=state.time.to_sec(),
            gripper_position=0.0,  # 需要单独查询
        )

    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        if not self._connected or self._robot is None:
            raise RuntimeError("Not connected")

        if joint_positions is not None:
            import libfranka
            q = joint_positions.tolist()
            self._robot.control(
                libfranka.motion_generators.JointPositionMotionGenerator(q),
            )

        if gripper_position is not None and self._gripper is not None:
            width = max(0.0, min(0.08, gripper_position * 0.08))
            self._gripper.move(width, 0.1)

    def estop(self) -> None:
        if self._robot:
            self._robot.stop()

    def recover(self) -> None:
        if self._robot:
            self._robot.automatic_error_recovery = True

    def base_pose(self) -> dict:
        """Franka 基座姿态（通常固定在地面坐标系）"""
        return {
            "translation": [0.0, 0.0, 0.0],
            "quaternion": [0.0, 0.0, 0.0, 1.0],  # xyzw
        }

    @staticmethod
    def _ee_pose_from_T(T: list) -> np.ndarray:
        """从 4x4 齐次变换矩阵提取 xyzw 四元数 + 平移"""
        m = np.array(T).reshape(4, 4)
        t = m[:3, 3]

        # 从旋转矩阵提取四元数
        trace = m[0, 0] + m[1, 1] + m[2, 2]
        if trace > 0:
            s = 0.5 / (trace + 1.0) ** 0.5
            w = 0.25 / s
            x = (m[2, 1] - m[1, 2]) * s
            y = (m[0, 2] - m[2, 0]) * s
            z = (m[1, 0] - m[0, 1]) * s
        else:
            x = (m[0, 0] - m[1, 1] - m[2, 2] + 1.0) ** 0.5 / 2
            y = (m[1, 0] + m[0, 1]) / (4 * x)
            z = (m[2, 0] + m[0, 2]) / (4 * x)
            w = (m[2, 1] - m[1, 2]) / (4 * x)

        return np.concatenate([t, np.array([x, y, z, w])])


__all__ = ["FrankaHAL"]
