"""Bidirectional ROS2 ↔ MQTT bridge.

Reads topic mapping from topic_mapping.yaml and registers subscribers/publishers
accordingly. Uses paho-mqtt for the MQTT side.
"""
from __future__ import annotations

import os
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

import paho.mqtt.client as mqtt
import yaml


class MqttBridgeNode(Node):
    def __init__(self) -> None:
        super().__init__("mqtt_bridge_node")
        self.declare_parameter("broker_host", "localhost")
        self.declare_parameter("broker_port", 1883)
        self.declare_parameter("mapping_file", str(
            Path(__file__).parent / "topic_mapping.yaml"
        ))
        broker_host = self.get_parameter("broker_host").value
        broker_port = int(self.get_parameter("broker_port").value)
        mapping_file = self.get_parameter("mapping_file").value

        with open(mapping_file, "r", encoding="utf-8") as fh:
            self._mapping = yaml.safe_load(fh)

        # ROS2 publishers and subscribers
        self._ros_pubs: dict[str, object] = {}
        self._ros_subs: dict[str, object] = {}

        for mqtt_topic, ros_topic in self._mapping.get("mqtt_to_ros", {}).items():
            pub = self.create_publisher(String, ros_topic, 10)
            self._ros_pubs[mqtt_topic] = pub
            self.get_logger().info(f"mqtt->ros  {mqtt_topic} -> {ros_topic}")

        for ros_topic, mqtt_topic in self._mapping.get("ros_to_mqtt", {}).items():
            sub = self.create_subscription(String, ros_topic, self._make_ros_cb(mqtt_topic), 10)
            self._ros_subs[ros_topic] = sub
            self.get_logger().info(f"ros->mqtt  {ros_topic} -> {mqtt_topic}")

        # MQTT client
        self._mqtt = mqtt.Client(client_id="mqtt_bridge_node")
        self._mqtt.on_message = self._on_mqtt_message
        self._mqtt.connect(broker_host, broker_port, keepalive=30)
        for topic in self._mapping.get("mqtt_to_ros", {}).keys():
            self._mqtt.subscribe(topic)
        self._mqtt.loop_start()
        self.get_logger().info(f"mqtt_bridge connected to {broker_host}:{broker_port}")

    def _on_mqtt_message(self, client, userdata, msg) -> None:
        pub = self._ros_pubs.get(msg.topic)
        if pub is None:
            return
        ros_msg = String()
        ros_msg.data = msg.payload.decode("utf-8")
        pub.publish(ros_msg)

    def _make_ros_cb(self, mqtt_topic: str):
        def cb(ros_msg: String) -> None:
            self._mqtt.publish(mqtt_topic, ros_msg.data.encode("utf-8"))
        return cb


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MqttBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()