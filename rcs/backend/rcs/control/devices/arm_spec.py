"""机械臂设备规格 — 参数化 DH/TCP/限位

与 robot-control-stack 的 RobotMetaConfig 对齐，支持从标准库或自定义配置创建设备规格。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass
class DHParams:
    """Denavit-Hartenberg 参数

    参数顺序: (a, d, alpha, theta_offset)
    与 rcs/planning/fk.py 的约定一致。
    """

    a: float
    d: float
    alpha: float
    theta_offset: float = 0.0

    def to_tuple(self) -> tuple[float, float, float, float]:
        return (self.a, self.d, self.alpha, self.theta_offset)


@dataclass
class JointLimits:
    """关节限位"""

    lower: np.ndarray
    upper: np.ndarray
    vel_max: np.ndarray
    acc_max: np.ndarray
    torque_max: np.ndarray | None = None
    rad_th: float = 0.05  # 关节空间追踪误差阈值
    pos_th: float = 0.01  # 位置空间追踪误差阈值


@dataclass
class ArmSpec:
    """机械臂设备规格

    统一管理 DH 参数、TCP 偏移、关节限位等运动学参数。
    与 DeviceProfile 的 limits 字段配合使用。
    """

    name: str
    dof: int
    dh_params: list[DHParams]
    tcp_offset: np.ndarray  # TCP 在最后关节末端的偏移 [x, y, z]
    joint_limits: JointLimits
    home_joints: np.ndarray
    control_hz: float = 100.0
    description: str = ""

    def to_dh_list(self) -> list[tuple[float, float, float, float]]:
        """转换为 (a, d, alpha, theta_offset) 列表

        用于 rcs/planning/fk.py 的 fk() 函数。
        """
        return [dh.to_tuple() for dh in self.dh_params]

    def to_dict(self) -> dict:
        """序列化为字典（用于配置持久化）"""
        return {
            "name": self.name,
            "dof": self.dof,
            "dh_params": [
                {"a": dh.a, "d": dh.d, "alpha": dh.alpha, "theta_offset": dh.theta_offset}
                for dh in self.dh_params
            ],
            "tcp_offset": self.tcp_offset.tolist(),
            "joint_limits": {
                "lower": self.joint_limits.lower.tolist(),
                "upper": self.joint_limits.upper.tolist(),
                "vel_max": self.joint_limits.vel_max.tolist(),
                "acc_max": self.joint_limits.acc_max.tolist(),
            },
            "home_joints": self.home_joints.tolist(),
            "control_hz": self.control_hz,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ArmSpec":
        """从字典反序列化"""
        return cls(
            name=d["name"],
            dof=d["dof"],
            dh_params=[DHParams(**p) for p in d["dh_params"]],
            tcp_offset=np.array(d["tcp_offset"]),
            joint_limits=JointLimits(
                lower=np.array(d["joint_limits"]["lower"]),
                upper=np.array(d["joint_limits"]["upper"]),
                vel_max=np.array(d["joint_limits"]["vel_max"]),
                acc_max=np.array(d["joint_limits"]["acc_max"]),
            ),
            home_joints=np.array(d["home_joints"]),
            control_hz=d.get("control_hz", 100.0),
            description=d.get("description", ""),
        )


# ---- 标准设备规格库 ----

# 6-DOF 通用机械臂（与 test_fk.py / test_ik.py 一致）
ARM_6DOF_STANDARD = ArmSpec(
    name="ARM_6DOF",
    dof=6,
    dh_params=[
        DHParams(a=0.0, d=0.10, alpha=math.pi / 2, theta_offset=0.0),
        DHParams(a=0.3, d=0.00, alpha=0.0, theta_offset=0.0),
        DHParams(a=0.2, d=0.00, alpha=math.pi / 2, theta_offset=0.0),
        DHParams(a=0.0, d=0.10, alpha=-math.pi / 2, theta_offset=0.0),
        DHParams(a=0.0, d=0.05, alpha=math.pi / 2, theta_offset=0.0),
        DHParams(a=0.0, d=0.04, alpha=0.0, theta_offset=0.0),
    ],
    tcp_offset=np.array([0.0, 0.0, 0.0]),
    joint_limits=JointLimits(
        lower=np.array([-3.14, -3.14, -3.14, -3.14, -3.14, -3.14]),
        upper=np.array([3.14, 3.14, 3.14, 3.14, 3.14, 3.14]),
        vel_max=np.array([2.0, 2.0, 2.0, 2.0, 2.0, 2.0]),
        acc_max=np.array([5.0, 5.0, 5.0, 5.0, 5.0, 5.0]),
    ),
    home_joints=np.array([0.0, -0.785, 0.785, 0.0, 0.785, 0.0]),
    description="6-DOF 通用机械臂（与 RCS 测试用例一致）",
)

# 7-DOF 机械臂（Franka FR3/Panda 类）
ARM_7DOF_FR3 = ArmSpec(
    name="ARM_7DOF_FR3",
    dof=7,
    dh_params=[
        DHParams(a=0.0, d=0.333, alpha=0.0, theta_offset=0.0),
        DHParams(a=0.0, d=0.316, alpha=-math.pi / 2, theta_offset=0.0),
        DHParams(a=0.0, d=0.384, alpha=math.pi / 2, theta_offset=0.0),
        DHParams(a=0.0825, d=0.0, alpha=math.pi / 2, theta_offset=0.0),
        DHParams(a=-0.0825, d=0.321, alpha=-math.pi / 2, theta_offset=0.0),
        DHParams(a=0.0, d=0.0, alpha=math.pi / 2, theta_offset=0.0),
        DHParams(a=0.088, d=0.107, alpha=math.pi / 2, theta_offset=0.0),
    ],
    tcp_offset=np.array([0.0, 0.0, 0.0]),
    joint_limits=JointLimits(
        lower=np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973]),
        upper=np.array([2.8973, 1.7628, 2.8973, 0.0698, 2.8973, 3.7525, 2.8973]),
        vel_max=np.array([2.175, 2.175, 2.175, 2.175, 2.61, 2.61, 2.61]),
        acc_max=np.array([15.0, 7.5, 10.0, 12.5, 15.0, 20.0, 20.0]),
    ),
    home_joints=np.array([0.0, -0.9599, 0.0, -2.0944, 0.0, 1.0472, 0.7854]),
    description="7-DOF Franka FR3/Panda 类机械臂",
)

# 标准规格注册表
ARM_SPEC_REGISTRY: dict[str, ArmSpec] = {
    "ARM_6DOF": ARM_6DOF_STANDARD,
    "ARM_7DOF_FR3": ARM_7DOF_FR3,
}


def get_arm_spec(name: str) -> ArmSpec:
    """获取标准机械臂规格

    Args:
        name: 规格名称，如 "ARM_6DOF", "ARM_7DOF_FR3"

    Returns:
        ArmSpec 实例

    Raises:
        KeyError: 规格名称不存在
    """
    if name not in ARM_SPEC_REGISTRY:
        raise KeyError(f"Unknown arm spec: {name!r}; available: {list(ARM_SPEC_REGISTRY)}")
    return ARM_SPEC_REGISTRY[name]


def register_arm_spec(spec: ArmSpec) -> None:
    """注册自定义机械臂规格"""
    ARM_SPEC_REGISTRY[spec.name] = spec


__all__ = [
    "DHParams",
    "JointLimits",
    "ArmSpec",
    "ARM_6DOF_STANDARD",
    "ARM_7DOF_FR3",
    "ARM_SPEC_REGISTRY",
    "get_arm_spec",
    "register_arm_spec",
]
