"""ROS 2 node hosting the MQTT bridge to RCS.

Thin wrapper: all routing and contract rules live in
:mod:`robot_gateway.bridge` and :mod:`robot_gateway.mqtt_link`, which are ROS-free
and unit-tested. This module only supplies parameters, timers and the ROS-side
sinks.

Parameters
----------
device_id : str
    Device this robot answers for. Commands for other devices are ignored.
broker_host / broker_port : str / int
    Mosquitto endpoint.
topic_prefix : str
    Optional deployment-wide MQTT prefix (multi-tenant brokers).
telemetry_hz : float
    Telemetry publish rate. Keep this low -- telemetry is health data, not
    control feedback.

Run with::

    ros2 run robot_gateway mqtt_bridge_node --ros-args -p device_id:=robot-01
"""
from __future__ import annotations

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from robot_msgs import CommandMsg, MoveCommandGoal, Pose6DMsg, RobotStateMsg, RobotTelemetryMsg, TaskCommandMsg

from .bridge import MqttBridge
from .mqtt_link import MqttLink


class MqttBridgeNode(Node):
    """Bridges the MQTT command/telemetry bus onto the local ROS 2 graph."""

    def __init__(self) -> None:
        super().__init__("mqtt_bridge_node")

        self.declare_parameter("device_id", "robot-01")
        self.declare_parameter("broker_host", "127.0.0.1")
        self.declare_parameter("broker_port", 1883)
        self.declare_parameter("broker_username", "")
        self.declare_parameter("broker_password", "")
        self.declare_parameter("topic_prefix", "")
        self.declare_parameter("telemetry_hz", 1.0)

        device_id = self.get_parameter("device_id").value
        topic_prefix = self.get_parameter("topic_prefix").value
        telemetry_hz = float(self.get_parameter("telemetry_hz").value)

        self._device_id = device_id

        self._link = MqttLink(
            host=self.get_parameter("broker_host").value,
            port=int(self.get_parameter("broker_port").value),
            client_id=f"robot-gateway-{device_id}",
            username=self.get_parameter("broker_username").value,
            password=self.get_parameter("broker_password").value,
        )
        self._bridge = MqttBridge(
            self._link,
            device_id=device_id,
            motion_sink=self._on_motion_command,
            estop_sink=self._on_estop_command,
            task_sink=self._on_task_command,
            topic_prefix=topic_prefix,
        )

        self._link.start()
        self._bridge.start()

        if telemetry_hz > 0:
            self._telemetry_timer = self.create_timer(
                1.0 / telemetry_hz, self._publish_telemetry
            )

        # ROS 2 topics for Decision communication
        self._motion_cmd_pub = self.create_publisher(String, "~/motion_command", 10)
        self._robot_state_sub = self.create_subscription(
            String, "~/robot_state", self._on_robot_state, 10
        )
        self._alert_sub = self.create_subscription(
            String, "~/alert", self._on_alert, 10
        )
        self._task_cmd_pub = self.create_publisher(String, "~/task_command", 10)

        self.get_logger().info(
            f"MQTT bridge started for device={device_id} "
            f"broker={self._link._host}:{self._link._port} "
            f"telemetry={telemetry_hz}Hz"
        )

    # --- command sinks ------------------------------------------------------

    def _on_motion_command(self, command: CommandMsg) -> None:
        """Forward a motion command to robot_decision via ~/motion_command."""
        goal = MoveCommandGoal(
            command_id=command.command_id,
            type=command.type,
            target_joints=command.target_joints or [],
            target_pose=command.target_pose,
            speed_scale=command.speed_scale,
        )
        # Serialize to JSON for std_msgs/msg/String transport
        payload = {
            "command_id": goal.command_id,
            "type": goal.type,
            "target_joints": goal.target_joints,
            "target_pose": goal.target_pose.to_dict() if goal.target_pose else None,
            "speed_scale": goal.speed_scale,
        }
        msg = String()
        msg.data = json.dumps(payload)
        self._motion_cmd_pub.publish(msg)
        self.get_logger().info(
            f"forwarded {command.type} (id={command.command_id}) to ~/motion_command"
        )

    def _on_estop_command(self, command: CommandMsg) -> None:
        """Emergency stop: must never be queued behind a motion command."""
        self.get_logger().warn(f"E-STOP received (id={command.command_id})")

    def _on_task_command(self, msg: TaskCommandMsg) -> None:
        """Forward a task command to robot_decision via ~/task_command."""
        payload = {
            "command_id": msg.command_id,
            "task_type": msg.task_type,
            "parameters": msg.parameters,
            "speed_scale": msg.speed_scale,
            "group": msg.group,
        }
        ros_msg = String()
        ros_msg.data = json.dumps(payload)
        self._task_cmd_pub.publish(ros_msg)
        self.get_logger().info(
            f"forwarded task_command {msg.task_type} (id={msg.command_id}) to ~/task_command"
        )

    def _on_robot_state(self, msg: String) -> None:
        """Forward robot state from Decision to MQTT."""
        try:
            data = json.loads(msg.data)
            state = RobotStateMsg.from_dict(data)
            self._bridge.publish_state(state)
        except Exception:
            self.get_logger().exception("failed to forward robot state to MQTT")

    def _on_alert(self, msg: String) -> None:
        """Forward alert from Decision to MQTT."""
        try:
            data = json.loads(msg.data)
            payload = json.dumps(data).encode()
            self._link.publish(
                f"rcs/{self._device_id}/alert", payload, qos=1
            )
            self.get_logger().warn(f"alert forwarded: {data.get('error', '')}")
        except Exception:
            self.get_logger().exception("failed to forward alert to MQTT")

    # --- telemetry ----------------------------------------------------------

    def _publish_telemetry(self) -> None:
        telemetry = RobotTelemetryMsg(
            device_id=self._device_id,
            metrics={
                "mqtt_buffered": float(self._link.buffered),
                "mqtt_publish_failures": float(self._link.publish_failures),
                **{k: float(v) for k, v in self._bridge.stats().items()},
            },
            status={
                "mqtt_connected": "true" if self._link.connected else "false",
                "online": "true",
            },
        )
        self._bridge.publish_telemetry(telemetry)

    # --- shutdown -----------------------------------------------------------

    def destroy_node(self) -> bool:
        self._link.stop()
        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MqttBridgeNode()
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
