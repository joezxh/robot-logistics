"""Gripper ROS2 driver node (50Hz control loop)."""
from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import WrenchStamped
from std_msgs.msg import String

from .hal_interface import make_hal, CommandMsg


class GripperDriverNode(Node):
    def __init__(self) -> None:
        super().__init__("gripper_driver")
        self.declare_parameter("device_id", "loader-01")
        self.declare_parameter("control_hz", 50)
        device_id = self.get_parameter("device_id").value
        control_hz = int(self.get_parameter("control_hz").value)
        self.hal = make_hal(device_id=device_id, num_joints=14)

        self.cmd_sub = self.create_subscription(String, "/gripper/command", self._on_cmd, 10)
        self.wrench_pub = self.create_publisher(WrenchStamped, "/gripper/wrench", 10)
        period = 1.0 / control_hz
        self.timer = self.create_timer(period, self._tick)

        self.get_logger().info(f"gripper_driver started device={device_id} hz={control_hz}")

    def _on_cmd(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
            cmd = CommandMsg(
                type=payload.get("type", "execute_task"),
                task_type=payload.get("task_type"),
                parameters=payload.get("parameters") or {},
            )
            self.hal.send_command(cmd)
        except Exception as exc:
            self.get_logger().warn(f"invalid cmd payload: {exc}")

    def _tick(self) -> None:
        state = self.hal.read_state()
        ws = WrenchStamped()
        ws.header.stamp = self.get_clock().now().to_msg()
        ws.header.frame_id = self.hal.device_id
        # synthetic force derived from gripper position (joint 12 / 13)
        left_close = state.positions[12] if len(state.positions) > 12 else 0.0
        right_close = state.positions[13] if len(state.positions) > 13 else 0.0
        # 0..1 close position maps to 0..100N
        ws.wrench.force.z = float(left_close + right_close) * 50.0
        self.wrench_pub.publish(ws)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GripperDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()