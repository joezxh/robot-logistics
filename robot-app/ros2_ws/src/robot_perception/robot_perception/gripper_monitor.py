"""Gripper monitor: watches force and triggers /collision/stop if exceeded."""
from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import WrenchStamped


class GripperMonitorNode(Node):
    def __init__(self) -> None:
        super().__init__("gripper_monitor")
        self.declare_parameter("max_force_n", 200.0)
        self.max_force = float(self.get_parameter("max_force_n").value)
        self.sub = self.create_subscription(WrenchStamped, "/gripper/wrench", self._on_wrench, 10)
        self.pub = self.create_publisher(Bool, "/collision/stop", 10)
        self.get_logger().info(f"gripper_monitor started max_force={self.max_force}N")

    def _on_wrench(self, msg: WrenchStamped) -> None:
        force = msg.wrench.force.z
        if abs(force) > self.max_force:
            self.get_logger().warn(f"force limit exceeded: {force:.1f}N")
            stop = Bool()
            stop.data = True
            self.pub.publish(stop)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = GripperMonitorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()