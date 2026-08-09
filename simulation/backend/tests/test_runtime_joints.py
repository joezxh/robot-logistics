"""Tests for Runtime joint cache and task state machine enhancements."""
import pytest

from backend.services.runtime import Runtime


class TestRuntimeJointCache:
    def test_update_and_get_joint_state(self):
        rt = Runtime()
        data = {
            "device_id": "robot-01",
            "joint_names": ["j1", "j2", "j3", "j4", "j5", "j6"],
            "positions": [0.0, -1.57, 1.57, -1.57, -1.57, 0.0],
            "velocities": [0.0] * 6,
            "timestamp_ns": 1234567890,
        }
        rt.update_joint_state("robot-01", data)
        result = rt.get_joint_state("robot-01")
        assert result is not None
        assert result["positions"] == [0.0, -1.57, 1.57, -1.57, -1.57, 0.0]

    def test_get_joint_state_unknown_device(self):
        rt = Runtime()
        assert rt.get_joint_state("nonexistent") is None


class TestRuntimeTaskStateMachine:
    def test_task_starts_as_pending(self):
        rt = Runtime()
        for task in rt.tasks.values():
            assert task["status"] == "pending"

    def test_advance_task_to_command_sent(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        rt.advance_task(task_id, "command_sent")
        assert rt.tasks[task_id]["status"] == "command_sent"

    def test_advance_task_to_running(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        rt.advance_task(task_id, "command_sent")
        rt.advance_task(task_id, "running")
        assert rt.tasks[task_id]["status"] == "running"

    def test_fail_task_from_any_state(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        rt.fail_task(task_id, "planning failed")
        assert rt.tasks[task_id]["status"] == "failed"

    def test_complete_task_requires_running(self):
        rt = Runtime()
        task_id = list(rt.tasks.keys())[0]
        # pending → completed should fail
        with pytest.raises(RuntimeError):
            rt.complete_task(task_id)
