"""Tests for BaseExecutor."""
import pytest
from robot_decision.base_executor import BaseExecutor, BaseState


def test_initial_state_is_idle():
    executor = BaseExecutor()
    assert executor.state == BaseState.IDLE


def test_follow_waypoint_transitions_to_following():
    executor = BaseExecutor()
    executor.follow_waypoint(x=1.0, y=2.0, yaw=0.0)
    assert executor.state == BaseState.FOLLOWING


def test_stop_transitions_to_stopped():
    executor = BaseExecutor()
    executor.follow_waypoint(x=1.0, y=2.0, yaw=0.0)
    executor.stop()
    assert executor.state == BaseState.STOPPED


def test_get_cmd_vel_returns_zero_when_stopped():
    executor = BaseExecutor()
    executor.stop()
    vx, wz = executor.get_cmd_vel()
    assert vx == 0.0 and wz == 0.0
