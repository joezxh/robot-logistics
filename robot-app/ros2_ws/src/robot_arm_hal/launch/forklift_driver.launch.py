"""Launch forklift and gripper drivers."""
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    return LaunchDescription([
        Node(
            package="robot_arm_hal",
            executable="forklift_driver",
            name="forklift_driver",
            parameters=[{"device_id": "forklift-01", "control_hz": 50}],
            output="screen",
        ),
        Node(
            package="robot_arm_hal",
            executable="gripper_driver",
            name="gripper_driver",
            parameters=[{"device_id": "loader-01", "control_hz": 50}],
            output="screen",
        ),
    ])