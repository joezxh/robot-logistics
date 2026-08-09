"""Base (AGV) executor — Nav2 NavigateToPose action client wrapper."""
from __future__ import annotations

import math
from enum import Enum, auto
from typing import Any


class BaseState(Enum):
    IDLE = auto()
    FOLLOWING = auto()
    STOPPED = auto()


class BaseExecutor:
    """Nav2 NavigateToPose action client for the diff-drive base.

    In production (ROS 2 environment), ``setup()`` creates a real action
    client.  In test/mock mode (no ROS 2), the executor gracefully degrades
    so that unit tests can exercise the state machine without a live Nav2
    stack.
    """

    def __init__(self, node: Any = None) -> None:
        self._node = node
        self._nav_client: Any = None
        self._state = BaseState.IDLE
        self._current_goal: Any = None

    @property
    def state(self) -> BaseState:
        return self._state

    def setup(self) -> None:
        """Initialize Nav2 action client.  Call from node ``__init__``."""
        try:
            from nav2_msgs.action import NavigateToPose
            from rclpy.action import ActionClient
            self._nav_client = ActionClient(
                self._node, NavigateToPose, "navigate_to_pose"
            )
        except ImportError:
            # Running in test/mock mode without ROS 2
            self._nav_client = None

    def follow_waypoint(self, x: float, y: float, yaw: float) -> None:
        """Send NavigateToPose goal to Nav2."""
        goal = self._build_goal(x, y, yaw)
        if goal is not None and self._nav_client:
            self._nav_client.send_goal_async(goal)
        self._state = BaseState.FOLLOWING

    def _build_goal(self, x: float, y: float, yaw: float) -> Any:
        """Build a PoseStamped goal.  Returns None without ROS 2."""
        try:
            from geometry_msgs.msg import PoseStamped
            goal = PoseStamped()
            goal.header.frame_id = "map"
            if self._node:
                goal.header.stamp = self._node.get_clock().now().to_msg()
            goal.pose.position.x = float(x)
            goal.pose.position.y = float(y)
            goal.pose.orientation.z = math.sin(yaw / 2)
            goal.pose.orientation.w = math.cos(yaw / 2)
            return goal
        except ImportError:
            return None

    def cancel(self) -> None:
        """Cancel current navigation goal."""
        if self._current_goal and self._nav_client:
            self._current_goal.cancel_goal_async()
        self._state = BaseState.STOPPED

    def stop(self) -> None:
        self.cancel()

    def on_feedback(self, feedback: Any) -> None:
        """Nav2 feedback callback."""
        pass

    def on_result(self, result: Any) -> None:
        """Nav2 result callback — advance coordinator phase."""
        self._state = BaseState.IDLE
        self._current_goal = None

    def complete_follow(self) -> None:
        self._state = BaseState.IDLE
