"""Tests for BaseExecutor with Nav2 action client interface."""
import math
import pytest
from unittest.mock import MagicMock
from robot_decision.base_executor import BaseExecutor, BaseState


class TestBaseExecutorNav2:
    def setup_method(self):
        self.node = MagicMock()
        self.node.get_clock.return_value.now.return_value.to_msg.return_value = MagicMock()
        self.executor = BaseExecutor(self.node)

    def test_initial_state_idle(self):
        assert self.executor.state == BaseState.IDLE

    def test_setup_creates_action_client(self):
        self.executor.setup()
        # In test mode (no ROS 2), nav_client is None
        assert self.executor._nav_client is None

    def test_follow_waypoint_sets_state(self):
        self.executor.follow_waypoint(1.0, 2.0, 0.5)
        assert self.executor.state == BaseState.FOLLOWING

    def test_stop_transitions_to_stopped(self):
        self.executor.follow_waypoint(1.0, 2.0, 0.5)
        self.executor.stop()
        assert self.executor.state == BaseState.STOPPED

    def test_on_result_resets_state(self):
        self.executor._state = BaseState.FOLLOWING
        self.executor.on_result(MagicMock())
        assert self.executor.state == BaseState.IDLE

    def test_on_feedback_does_not_crash(self):
        self.executor.on_feedback(MagicMock())

    def test_cancel_when_no_goal(self):
        """Cancel with no active goal should not crash."""
        self.executor._current_goal = None
        self.executor.cancel()
        assert self.executor.state == BaseState.STOPPED

    def test_complete_follow_resets_to_idle(self):
        self.executor._state = BaseState.FOLLOWING
        self.executor.complete_follow()
        assert self.executor.state == BaseState.IDLE

    def test_quaternion_from_yaw(self):
        """Verify yaw → quaternion conversion via mock nav_client."""
        import sys
        from unittest.mock import patch, MagicMock as MM
        # Create mock geometry_msgs module
        mock_pose = MM()
        mock_msg_mod = MM()
        mock_msg_mod.PoseStamped.return_value = mock_pose
        with patch.dict(sys.modules, {"geometry_msgs": mock_msg_mod, "geometry_msgs.msg": mock_msg_mod}):
            mock_client = MagicMock()
            self.executor._nav_client = mock_client
            self.executor.follow_waypoint(0.0, 0.0, math.pi / 2)
            mock_client.send_goal_async.assert_called_once()
            goal = mock_client.send_goal_async.call_args[0][0]
            assert abs(goal.pose.orientation.z - math.sin(math.pi / 4)) < 0.01
            assert abs(goal.pose.orientation.w - math.cos(math.pi / 4)) < 0.01

    def test_build_goal_returns_none_without_ros2(self):
        """_build_goal should return None when geometry_msgs is unavailable."""
        result = self.executor._build_goal(1.0, 2.0, 0.0)
        # In test env without ROS 2, returns None
        assert result is None
