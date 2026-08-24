"""硬件抽象层基类

定义真实硬件 HAL 的标准接口，与 SimHAL 对齐。
支持 Franka/UR 等多种机器人。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class HALState:
    """HAL 状态快照

    统一的状态格式，与 RCS RobotState 对齐。
    """

    joint_positions: np.ndarray
    joint_velocities: np.ndarray
    joint_efforts: np.ndarray
    cartesian_pose: np.ndarray  # [x, y, z, qx, qy, qz, qw] xyzw
    wrench: np.ndarray  # [fx, fy, fz, tx, ty, tz]
    timestamp: float
    gripper_position: float = 0.0

    @property
    def dof(self) -> int:
        return len(self.joint_positions)


class HALError(Exception):
    """HAL 操作失败"""
    pass


class HALTimeout(HALError):
    """HAL 读取超时"""
    pass


class HALConnectionError(HALError):
    """HAL 连接失败"""
    pass


class HardwareHAL(ABC):
    """真实硬件 HAL 抽象基类

    定义与 SimHAL 一致的接口，子类实现具体协议。
    支持 Franka、UR 等多种机器人。
    """

    def __init__(self, host: str, port: int = 50051):
        self._host = host
        self._port = port
        self._connected = False

    @abstractmethod
    def connect(self) -> None:
        """建立连接"""

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""

    @abstractmethod
    def read_state(self, timeout_ms: int = 1000) -> HALState:
        """读取当前状态"""

    @abstractmethod
    def send_command(
        self,
        *,
        joint_positions: np.ndarray | None = None,
        joint_efforts: np.ndarray | None = None,
        gripper_position: float | None = None,
    ) -> None:
        """发送控制命令

        Args:
            joint_positions: 目标关节位置 (DOF,)
            joint_efforts: 目标关节力矩 (DOF,) (可选)
            gripper_position: 夹爪目标位置 (0-1)
        """

    @abstractmethod
    def estop(self) -> None:
        """紧急停止"""

    @abstractmethod
    def recover(self) -> None:
        """从错误状态恢复"""

    def base_pose(self) -> dict:
        """获取基座在世界坐标系中的姿态

        默认返回原点姿态，子类可覆盖以支持移动机器人。
        """
        return {
            "translation": [0.0, 0.0, 0.0],
            "quaternion": [0.0, 0.0, 0.0, 1.0],  # xyzw 单位四元数
        }

    @property
    def is_connected(self) -> bool:
        return self._connected

    def __repr__(self) -> str:
        status = "connected" if self._connected else "disconnected"
        return f"{self.__class__.__name__}({self._host}:{self._port}, {status})"


def create_hal(robot_type: str, host: str, **kwargs) -> HardwareHAL:
    """HAL 工厂函数

    Args:
        robot_type: 机器人类型，如 "franka", "ur5e", "xarm7"
        host: 机器人 IP 地址
        **kwargs: 额外参数（如 port, gripper_host）

    Returns:
        HardwareHAL 实例
    """
    from robot_contracts import RobotType

    # 标准化机器人类型
    rt = robot_type.lower()
    if rt in ("franka", "fr3", "panda"):
        from .franka import FrankaHAL
        return FrankaHAL(host=host, **kwargs)
    elif rt in ("ur5e", "ur10", "ur", "ur5"):
        from .ur_rtde import URRTDEHAL
        return URRTDEHAL(host=host, **kwargs)
    elif rt in ("xarm7", "xarm"):
        from .xarm import XArmHAL
        return XArmHAL(host=host, **kwargs)
    else:
        raise ValueError(
            f"Unknown robot type: {robot_type!r}; "
            f"supported: franka, ur5e, xarm7"
        )


__all__ = [
    "HALState",
    "HALError",
    "HALTimeout",
    "HALConnectionError",
    "HardwareHAL",
    "create_hal",
]
