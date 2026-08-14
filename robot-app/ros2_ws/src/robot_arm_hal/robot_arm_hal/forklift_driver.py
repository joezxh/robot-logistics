"""Forklift ROS2 driver node (50Hz control loop)."""
from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String

from .hal_interface import make_hal, CommandMsg


class ForkliftDriverNode(Node):
    def __init__(self) -> None:
        super().__init__("forklift_driver")
        self.declare_parameter("device_id", "forklift-01")
        self.declare_parameter("control_hz", 50)
        device_id = self.get_parameter("device_id").value
        control_hz = int(self.get_parameter("control_hz").value)
        self.hal = make_hal(device_id=device_id, num_joints=3)

        self.cmd_sub = self.create_subscription(String, "/forklift/command", self._on_cmd, 10)
        self.js_pub = self.create_publisher(JointState, "/forklift/joint_states", 10)
        period = 1.0 / control_hz
        self.timer = self.create_timer(period, self._tick)

        self.get_logger().info(f"forklift_driver started device={device_id} hz={control_hz}")

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
        js = JointState()
        js.name = ["travel", "lift", "extend"]
        js.position = state.positions
        js.velocity = state.velocities
        js.effort = state.efforts
        js.header.stamp = self.get_clock().now().to_msg()
        js.header.frame_id = self.hal.device_id
        self.js_pub.publish(js)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ForkliftDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()