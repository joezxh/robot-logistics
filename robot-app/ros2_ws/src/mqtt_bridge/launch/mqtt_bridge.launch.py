"""Launch MQTT bridge node."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package="mqtt_bridge",
            executable="mqtt_bridge_node",
            name="mqtt_bridge_node",
            parameters=[{"broker_host": "mosquitto", "broker_port": 1883}],
            output="screen",
        ),
    ])