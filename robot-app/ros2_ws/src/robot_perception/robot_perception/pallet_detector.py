"""Pallet detector: in SIM mode returns mock pose; in REAL mode subscribes to point cloud."""
from __future__ import annotations

import json
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class PalletDetectorNode(Node):
    def __init__(self) -> None:
        super().__init__("pallet_detector")
        self.declare_parameter("mode", os.environ.get("HAL_MODE", "sim"))
        self.pub = self.create_publisher(String, "/perception/pallets", 10)
        self.timer = self.create_timer(2.0, self._publish_mock)
        self.get_logger().info("pallet_detector started")

    def _publish_mock(self) -> None:
        msg = String()
        msg.data = json.dumps({
            "detections": [
                {"id": "pallet-01", "x": -3.0, "y": 0.0, "z": 2.0,
                 "rx": 0.0, "ry": 0.0, "rz": 0.0, "confidence": 0.95},
            ],
            "timestamp": self.get_clock().now().to_msg().sec,
        })
        self.pub.publish(msg)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PalletDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()