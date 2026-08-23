"""站点 TCP 姿态配置 — 统一坐标系管理

统一管理仓库站点到臂基座的坐标变换，避免硬编码。
与 RCS Pose 转换系统完全集成。

世界坐标系变换链：
    世界 = 基座姿态 @ TCP姿态_in_基座
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .kinematics import Pose, RobotType


@dataclass
class SiteTCPPose:
    """站点 TCP 姿态配置

    统一管理仓库站点到臂基座的坐标变换，避免硬编码。
    使用 RCS xyzw 四元数约定。
    """

    site_id: str
    tcp_pose_in_base: Pose
    robot_type: RobotType
    description: str = ""

    @classmethod
    def from_rpy(
        cls,
        site_id: str,
        translation: Sequence[float],
        rpy_deg: Sequence[float],
        robot_type: RobotType = RobotType.ARM,
        description: str = "",
    ) -> "SiteTCPPose":
        """从 RPY (度) 创建站点配置（兼容旧数据）"""
        r, p, y = [math.radians(d) for d in rpy_deg]
        tcp_pose = Pose.from_rpy([r, p, y], translation)
        return cls(
            site_id=site_id,
            tcp_pose_in_base=tcp_pose,
            robot_type=robot_type,
            description=description,
        )

    @classmethod
    def from_xyzw(
        cls,
        site_id: str,
        translation: Sequence[float],
        quaternion_xyzw: Sequence[float],
        robot_type: RobotType = RobotType.ARM,
        description: str = "",
    ) -> "SiteTCPPose":
        """从 xyzw 四元数创建站点配置（RCS 标准格式）"""
        tcp_pose = Pose(translation=translation, quaternion=quaternion_xyzw)
        return cls(
            site_id=site_id,
            tcp_pose_in_base=tcp_pose,
            robot_type=robot_type,
            description=description,
        )

    def get_world_pose(self, base_pose: Pose) -> Pose:
        """将 TCP 姿态转换到世界坐标系"""
        from .kinematics import to_pose_in_world_coordinates
        return to_pose_in_world_coordinates(base_pose, self.tcp_pose_in_base)

    def to_dict(self) -> dict:
        """序列化为字典（用于配置持久化）"""
        return {
            "site_id": self.site_id,
            "translation": self.tcp_pose_in_base.translation.tolist(),
            "quaternion_xyzw": self.tcp_pose_in_base.quaternion.tolist(),
            "robot_type": self.robot_type.value,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SiteTCPPose":
        """从字典反序列化"""
        return cls(
            site_id=d["site_id"],
            tcp_pose_in_base=Pose(
                translation=d["translation"],
                quaternion=d["quaternion_xyzw"],
            ),
            robot_type=RobotType(d["robot_type"]),
            description=d.get("description", ""),
        )


# 预定义站点配置（兼容旧 _SITE_TCP_POSES）
DEFAULT_SITE_PROFILES: dict[str, SiteTCPPose] = {
    "dock_loading": SiteTCPPose.from_rpy(
        site_id="dock_loading",
        translation=[0.50, 0.00, 0.30],
        rpy_deg=[0.0, 90.0, 0.0],  # ry=90° = y向上
        description="码头装载站点 TCP",
    ),
    "warehouse_storage": SiteTCPPose.from_rpy(
        site_id="warehouse_storage",
        translation=[0.40, -0.30, 0.50],
        rpy_deg=[0.0, 90.0, 0.0],
        description="仓库存储站点 TCP",
    ),
}


def get_site_profile(site_id: str) -> SiteTCPPose:
    """获取站点配置"""
    if site_id not in DEFAULT_SITE_PROFILES:
        raise KeyError(
            f"Unknown site_id: {site_id!r}; available: {list(DEFAULT_SITE_PROFILES)}"
        )
    return DEFAULT_SITE_PROFILES[site_id]


def register_site_profile(profile: SiteTCPPose) -> None:
    """注册自定义站点配置"""
    DEFAULT_SITE_PROFILES[profile.site_id] = profile


__all__ = [
    "SiteTCPPose",
    "DEFAULT_SITE_PROFILES",
    "get_site_profile",
    "register_site_profile",
]
