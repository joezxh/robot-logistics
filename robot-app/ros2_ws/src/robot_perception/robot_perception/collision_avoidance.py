"""Collision avoidance: aggregates /collision/stop signals and broadcasts to all nodes."""
from __future__ import annotations

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool


class CollisionAvoidanceNode(Node):
    def __init__(self) -> None:
        super().__init__("collision_avoidance")
        self.sub = self.create_subscription(Bool, "/collision/stop", self._on_stop, 10)
        self.pub = self.create_publisher(Bool, "/collision/estop", 10, latch=True)
        self._estopped = False
        self.get_logger().info("collision_avoidance started")

    def _on_stop(self, msg: Bool) -> None:
        if msg.data and not self._estopped:
            self._estopped = True
            self.get_logger().error("EMERGENCY STOP triggered")
            stop = Bool()
            stop.data = True
            self.pub.publish(stop)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = CollisionAvoidanceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()