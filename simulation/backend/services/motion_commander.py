"""Bridge from simulation tasks to motion commands.

Converts high-level task types (dock_loading, agv_transport, warehouse_storage)
into MoveCommand payloads published via MQTT.

Coordinate transform
--------------------
SiteManager stores warehouse-scale coordinates (e.g. x=-6.0, z=7.0) which are
far outside the arm's ~0.8m reach.  We predefine fixed TCP poses in the arm
base frame for each task type.  Real values come from calibration or CAD.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any

from backend.algorithm.simulator.site_manager import SiteManager
from backend.services.mqtt_bridge import SimulationMqttBridge

logger = logging.getLogger(__name__)

# Predefined arm-base TCP poses (metres, in arm base frame).
_SITE_TCP_POSES: dict[str, dict[str, float]] = {
    "dock_loading": {"x": 0.50, "y": 0.00, "z": 0.30, "rx": 0.0, "ry": 1.57, "rz": 0.0},
    "warehouse_storage": {"x": 0.40, "y": -0.30, "z": 0.50, "rx": 0.0, "ry": 1.57, "rz": 0.0},
}

# Default joint configuration for agv_transport (radians).
_TRANSPORT_JOINTS: list[float] = [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]


class MotionCommander:
    """Converts task records into motion commands published via MQTT."""

    def __init__(self, mqtt_bridge: SimulationMqttBridge, site_manager: SiteManager) -> None:
        self._bridge = mqtt_bridge
        self._sites = site_manager

    def on_task_started(self, task_record: dict[str, Any]) -> dict[str, Any] | None:
        task_type = task_record["type"]
        device_id = task_record["device_id"]
        command = self._build_command(task_type, device_id)
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

    def _build_command(self, task_type: str, device_id: str) -> dict[str, Any] | None:
        command_id = f"cmd-{uuid.uuid4().hex[:8]}"
        if task_type == "dock_loading":
            return {
                "command_id": command_id,
                "type": "move_l",
                "target_pose": _SITE_TCP_POSES["dock_loading"],
                "target_joints": [],
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
            return {
                "command_id": command_id,
                "type": "move_l",
                "target_pose": _SITE_TCP_POSES["warehouse_storage"],
                "target_joints": [],
                "speed_scale": 0.5,
            }
        else:
            logger.warning("unknown task type %r — no motion command generated", task_type)
            return None
