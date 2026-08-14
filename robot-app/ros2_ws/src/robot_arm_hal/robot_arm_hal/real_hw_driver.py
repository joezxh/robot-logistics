"""Real hardware HAL — paho-mqtt bridge to PLC/EtherCAT gateway.

Requires env vars:
    HAL_MODE=real
    MQTT_BROKER_HOST=<host>
    MQTT_BROKER_PORT=<port>  (default 1883)
    PLC_TOPIC_CMD=<topic>    (default rcs/<device_id>/command)
    PLC_TOPIC_STATUS=<topic> (default rcs/<device_id>/status)
"""
from __future__ import annotations

import json
import os
import threading
from typing import Optional

import paho.mqtt.client as mqtt

from .hal_interface import HALInterface, JointStateMsg, CommandMsg


class RealHardwareDriver(HALInterface):
    def __init__(self, device_id: str, num_joints: int) -> None:
        self.device_id = device_id
        self.num_joints = num_joints
        self._lock = threading.Lock()
        self._positions: list[float] = [0.0] * num_joints
        self._velocities: list[float] = [0.0] * num_joints
        self._estopped = False

        broker_host = os.environ.get("MQTT_BROKER_HOST", "localhost")
        broker_port = int(os.environ.get("MQTT_BROKER_PORT", "1883"))
        status_topic = os.environ.get("PLC_TOPIC_STATUS", f"rcs/{device_id}/status")

        self._client = mqtt.Client(client_id=f"hal-{device_id}")
        self._client.on_message = self._on_status
        self._client.connect(broker_host, broker_port, keepalive=30)
        self._client.subscribe(status_topic)
        self._client.loop_start()

    def _on_status(self, client, userdata, msg) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            positions = payload.get("joint_positions", [])
            velocities = payload.get("joint_velocities", [])
            with self._lock:
                if len(positions) == self.num_joints:
                    self._positions = list(positions)
                if len(velocities) == self.num_joints:
                    self._velocities = list(velocities)
        except Exception:
            pass

    def read_state(self) -> JointStateMsg:
        with self._lock:
            return JointStateMsg(
                positions=list(self._positions),
                velocities=list(self._velocities),
                efforts=[0.0] * self.num_joints,
                device_id=self.device_id,
            )

    def send_command(self, cmd: CommandMsg) -> bool:
        with self._lock:
            if self._estopped:
                return False
        topic = os.environ.get("PLC_TOPIC_CMD", f"rcs/{self.device_id}/command")
        payload = json.dumps({
            "type": cmd.type,
            "task_type": cmd.task_type,
            "parameters": cmd.parameters or {},
        })
        self._client.publish(topic, payload)
        return True

    def estop(self) -> None:
        with self._lock:
            self._estopped = True
        self.send_command(CommandMsg(type="estop"))

    def recover(self) -> None:
        with self._lock:
            self._estopped = False
        self.send_command(CommandMsg(type="recover"))