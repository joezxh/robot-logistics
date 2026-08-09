"""ROS 2 node wrapping TaskCoordinator for dual-arm loading tasks.

Subscribes to ~/task_command (String JSON), dispatches to executors,
publishes state on ~/robot_state.

Adapts the TaskCoordinator's generic execute(phase, params) dispatch
to the existing executor APIs (BaseExecutor, ArmExecutor, HugController).
"""
from __future__ import annotations

import json
from typing import Any

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from robot_decision.task_coordinator import TaskCoordinator
from robot_decision.safety_monitor import SafetyMonitor
from robot_decision.base_executor import BaseExecutor
from robot_decision.arm_executor import ArmExecutor
from robot_decision.hug_controller import HugController


class _BaseAdapter:
    """Adapts BaseExecutor to the coordinator's execute(phase, params) interface."""

    def __init__(self, executor: BaseExecutor) -> None:
        self._executor = executor

    def execute(self, phase: str, params: dict[str, Any]) -> None:
        pose = params.get("target_pose", {})
        x = float(pose.get("x", 0.0))
        y = float(pose.get("y", 0.0))
        yaw = float(pose.get("yaw", 0.0))
        self._executor.follow_waypoint(x, y, yaw)

    def stop(self) -> None:
        self._executor.stop()


class _ArmAdapter:
    """Adapts ArmExecutor to the coordinator's execute(phase, params) interface."""

    def __init__(self, executor: ArmExecutor) -> None:
        self._executor = executor

    def execute(self, phase: str, params: dict[str, Any]) -> None:
        joints = params.get("target_joints", [])
        if joints:
            self._executor.plan_and_execute(joints)

    def stop(self) -> None:
        self._executor.cancel()


class _HugAdapter:
    """Adapts HugController to the coordinator's execute(phase, params) interface."""

    def __init__(self, controller: HugController) -> None:
        self._controller = controller

    def execute(self, phase: str, params: dict[str, Any]) -> None:
        hug_params = params.get("hug_params", {})
        if phase == "approaching":
            target_pose = params.get("target_pose", {})
            self._controller.approach(target_pose)
        elif phase == "hugging":
            self._controller.close(
                pressure_target=float(hug_params.get("pressure_target", 50.0)),
                approach_speed=float(hug_params.get("approach_speed", 0.2)),
                close_speed=float(hug_params.get("close_speed", 0.05)),
            )
        elif phase == "placing":
            self._controller.release()

    def stop(self) -> None:
        self._controller.abort()


class TaskCoordinatorNode(Node):
    def __init__(self) -> None:
        super().__init__("task_coordinator_node")

        self.declare_parameter("safety_zone_radius", 1.5)
        self.declare_parameter("min_obstacle_distance", 0.3)

        self._coordinator = TaskCoordinator(
            on_phase_change=self._on_phase_change,
        )
        self._safety = SafetyMonitor()

        # Create executors and adapters
        base = BaseExecutor()
        left_arm = ArmExecutor(arm_id="left")
        right_arm = ArmExecutor(arm_id="right")
        hug = HugController()

        self._base_adapter = _BaseAdapter(base)
        self._arm_adapter = _ArmAdapter(left_arm)
        self._hug_adapter = _HugAdapter(hug)

        self._coordinator.set_executor("base", self._base_adapter)
        self._coordinator.set_executor("arm", self._arm_adapter)
        self._coordinator.set_executor("hug", self._hug_adapter)

        # Keep references for state reporting
        self._base = base
        self._hug = hug

        self._task_cmd_sub = self.create_subscription(
            String, "~/task_command", self._on_task_command, 10
        )
        self._state_pub = self.create_publisher(String, "~/robot_state", 10)

        self._timer = self.create_timer(0.1, self._tick)
        self.get_logger().info("TaskCoordinatorNode ready")

    def _on_task_command(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
            self._coordinator.on_task_command(
                task_type=data["task_type"],
                parameters=data.get("parameters", {}),
            )
        except Exception:
            self.get_logger().exception("failed to process task command")

    def _on_phase_change(self, phase: str) -> None:
        self._publish_state()

    def _tick(self) -> None:
        self._coordinator.check_timeouts()
        self._publish_state()

    def _publish_state(self) -> None:
        from robot_decision.hug_controller import HugPhase
        state = {
            "ctrl": {
                "mode": "task",
                "phase": self._coordinator.get_phase(),
            },
            "hug": {
                "state": self._hug.phase.name.lower(),
            },
            "base": {
                "velocity": self._base.get_cmd_vel(),
            },
        }
        msg = String()
        msg.data = json.dumps(state)
        self._state_pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = TaskCoordinatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
