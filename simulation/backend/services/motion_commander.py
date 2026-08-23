"""Bridge from simulation tasks to motion commands.

Converts high-level task types (dock_loading, agv_transport, warehouse_storage)
into MoveCommand payloads published via MQTT.

Coordinate transform
-------------------
使用 robot_contracts.site_tcp 模块统一管理站点 TCP 姿态，
替代硬编码的 _SITE_TCP_POSES。

世界坐标系变换链：
    世界 = 基座姿态 @ TCP姿态_in_基座
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from backend.algorithm.simulator.site_manager import SiteManager
from backend.services.mqtt_bridge import SimulationMqttBridge
from robot_contracts import Pose, RobotType, get_site_profile

logger = logging.getLogger(__name__)

# 默认关节配置 (radians) - 保留兼容
_TRANSPORT_JOINTS: list[float] = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]


class MotionCommander:
    """Converts task records into motion commands published via MQTT.

    使用 SiteTCPPose 统一管理坐标系，与 RCS Pose 转换系统集成。
    支持世界坐标系变换：
        世界 = 基座姿态 @ TCP姿态_in_基座
    """

    def __init__(
        self,
        mqtt_bridge: SimulationMqttBridge,
        site_manager: SiteManager,
        site_profiles: dict[str, Any] | None = None,
    ) -> None:
        self._bridge = mqtt_bridge
        self._sites = site_manager
        # site_profiles: site_id -> SiteTCPPose
        self._site_profiles: dict[str, Any] = site_profiles or {}

    def _get_tcp_pose(self, site_id: str) -> Any:
        """获取站点的 TCP 姿态（优先实例配置，否则全局配置）"""
        if site_id in self._site_profiles:
            return self._site_profiles[site_id].tcp_pose_in_base
        return get_site_profile(site_id).tcp_pose_in_base

    def _pose_to_dict(self, pose: Pose, use_quaternion: bool = True) -> dict:
        """将 Pose 转换为命令字典

        Args:
            pose: RCS Pose 对象
            use_quaternion: True=xyzw四元数格式, False=RPY格式(兼容旧接口)
        """
        if use_quaternion:
            return {
                "position": pose.translation.tolist(),
                "quaternion_xyzw": pose.quaternion.tolist(),  # RCS xyzw 标准
            }
        else:
            # 回退到 RPY 格式（兼容旧接口）
            import math
            rpy = pose.to_rpy()
            return {
                "x": pose.translation[0],
                "y": pose.translation[1],
                "z": pose.translation[2],
                "rx": math.degrees(rpy[0]),
                "ry": math.degrees(rpy[1]),
                "rz": math.degrees(rpy[2]),
            }

    def _build_command(
        self,
        task_type: str,
        device_id: str,
        base_pose: Pose | None = None,
    ) -> dict[str, Any] | None:
        """构建运动命令

        Args:
            task_type: 任务类型
            device_id: 设备 ID
            base_pose: 机器人基座在世界坐标系中的姿态（用于坐标变换）
        """
        command_id = f"cmd-{uuid.uuid4().hex[:8]}"

        if task_type == "dock_loading":
            tcp_pose = self._get_tcp_pose("dock_loading")
            # 如果提供了基座姿态，转换为世界系
            if base_pose is not None:
                world_pose = base_pose @ tcp_pose
                return {
                    "command_id": command_id,
                    "type": "move_l",
                    "target_pose": self._pose_to_dict(world_pose, use_quaternion=True),
                    "speed_scale": 0.5,
                }
            return {
                "command_id": command_id,
                "type": "move_l",
                "target_pose": self._pose_to_dict(tcp_pose, use_quaternion=False),
                "speed_scale": 0.5,
            }

        elif task_type == "agv_transport":
            return {
                "command_id": command_id,
                "type": "move_j",
                "target_joints": list(_TRANSPORT_JOINTS),
                "target_pose": None,
                "speed_scale": 0.8,
            }

        elif task_type == "warehouse_storage":
            tcp_pose = self._get_tcp_pose("warehouse_storage")
            if base_pose is not None:
                world_pose = base_pose @ tcp_pose
                return {
                    "command_id": command_id,
                    "type": "move_l",
                    "target_pose": self._pose_to_dict(world_pose, use_quaternion=True),
                    "speed_scale": 0.5,
                }
            return {
                "command_id": command_id,
                "type": "move_l",
                "target_pose": self._pose_to_dict(tcp_pose, use_quaternion=False),
                "speed_scale": 0.5,
            }

        else:
            logger.warning("unknown task type %r — no motion command generated", task_type)
            return None

    def on_task_started(self, task_record: dict[str, Any]) -> dict[str, Any] | None:
        """处理任务开始事件"""
        task_type = task_record["type"]
        device_id = task_record["device_id"]

        # 提取基座姿态（如果有）
        base_pose = None
        if "base_pose" in task_record:
            base_pose = Pose.from_dict(task_record["base_pose"])

        command = self._build_command(task_type, device_id, base_pose)
        if command is None:
            return None

        topic = f"rcs/{device_id}/command"
        self._bridge.publish_command(topic, command)
        logger.info("published %s command for %s: %s", task_type, device_id, command["type"])
        return command

    def on_task_command(self, task_type: str, device_id: str, parameters: dict) -> dict[str, Any] | None:
        """Build an execute_task command for the TaskCoordinator pipeline."""
        command_id = f"cmd-{uuid.uuid4().hex[:8]}"
        command = {
            "command_id": command_id,
            "type": "execute_task",
            "task_type": task_type,
            "parameters": parameters,
            "speed_scale": 1.0,
        }
        topic = f"rcs/{device_id}/command"
        self._bridge.publish_command(topic, command)
        logger.info("published execute_task %s for %s", task_type, device_id)
        return command
