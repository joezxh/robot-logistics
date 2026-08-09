"""Tests for MotionCommander — task-to-motion-command mapping."""
import math

import pytest

from backend.services.motion_commander import MotionCommander


class FakeBridge:
    def __init__(self):
        self.published = []

    def publish_command(self, topic: str, payload: dict) -> bool:
        self.published.append((topic, payload))
        return True


class TestMotionCommander:
    def _make(self) -> tuple[MotionCommander, FakeBridge]:
        from backend.algorithm.simulator.site_manager import SiteManager

        bridge = FakeBridge()
        sites = SiteManager()
        cmdr = MotionCommander(bridge, sites)
        return cmdr, bridge

    def test_dock_loading_publishes_move_l(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t1", "type": "dock_loading", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is not None
        assert len(bridge.published) == 1
        topic, payload = bridge.published[0]
        assert topic == "rcs/robot-01/command"
        assert payload["type"] == "move_l"
        assert "target_pose" in payload

    def test_agv_transport_publishes_move_j(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t2", "type": "agv_transport", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is not None
        topic, payload = bridge.published[0]
        assert payload["type"] == "move_j"
        assert "target_joints" in payload

    def test_warehouse_storage_publishes_move_l(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t3", "type": "warehouse_storage", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is not None
        _, payload = bridge.published[0]
        assert payload["type"] == "move_l"

    def test_unknown_task_type_returns_none(self):
        cmdr, bridge = self._make()
        task = {"task_id": "t4", "type": "unknown_type", "device_id": "robot-01"}
        result = cmdr.on_task_started(task)
        assert result is None
        assert len(bridge.published) == 0

    def test_tcp_pose_within_arm_reach(self):
        """SiteManager warehouse coords must be converted to arm-reachable poses."""
        cmdr, bridge = self._make()
        task = {"task_id": "t5", "type": "dock_loading", "device_id": "robot-01"}
        cmdr.on_task_started(task)
        _, payload = bridge.published[0]
        pose = payload["target_pose"]
        reach = math.sqrt(pose["x"] ** 2 + pose["y"] ** 2 + pose["z"] ** 2)
        assert reach < 1.5, f"TCP pose out of arm reach: {reach:.2f}m"
