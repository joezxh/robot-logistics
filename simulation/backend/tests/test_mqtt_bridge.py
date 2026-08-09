"""Unit tests for SimulationMqttBridge — no broker required."""
import json
from unittest.mock import MagicMock

import pytest

from backend.services.mqtt_bridge import SimulationMqttBridge


class TestSimulationMqttBridge:
    """Tests that the bridge publishes commands and dispatches state callbacks."""

    def _make_bridge(self, enabled: bool = True) -> SimulationMqttBridge:
        bridge = SimulationMqttBridge(
            host="127.0.0.1",
            port=1883,
            enabled=enabled,
        )
        # Replace the real paho client with a mock
        bridge._client = MagicMock()
        bridge._client.publish = MagicMock(return_value=MagicMock(rc=0))
        bridge._connected = True
        return bridge

    def test_disabled_bridge_does_not_publish(self):
        bridge = SimulationMqttBridge(host="127.0.0.1", port=1883, enabled=False)
        bridge.start()
        result = bridge.publish_command("rcs/robot-01/command", {"type": "move_l"})
        assert result is False

    def test_publish_command_sends_json(self):
        bridge = self._make_bridge()
        payload = {"command_id": "cmd-1", "type": "move_l", "target_joints": []}
        ok = bridge.publish_command("rcs/robot-01/command", payload)
        assert ok is True
        bridge._client.publish.assert_called_once()
        args = bridge._client.publish.call_args
        assert args[0][0] == "rcs/robot-01/command"
        sent = json.loads(args[0][1])
        assert sent["command_id"] == "cmd-1"

    def test_state_callback_dispatched(self):
        bridge = self._make_bridge()
        received = []
        bridge.subscribe_state("rcs/robot-01/state", lambda msg: received.append(msg))
        # Simulate an incoming message
        fake_msg = MagicMock()
        fake_msg.topic = "rcs/robot-01/state"
        fake_msg.payload = json.dumps(
            {"device_id": "robot-01", "joint": {"positions": [0.0] * 6}}
        ).encode()
        bridge._on_message(None, None, fake_msg)
        assert len(received) == 1
        assert received[0]["device_id"] == "robot-01"

    def test_stop_disconnects(self):
        bridge = self._make_bridge()
        bridge.stop()
        bridge._client.loop_stop.assert_called_once()
        bridge._client.disconnect.assert_called_once()

    def test_wildcard_topic_matching(self):
        bridge = self._make_bridge()
        received = []
        bridge.subscribe_state("rcs/+/state", lambda msg: received.append(msg))
        fake_msg = MagicMock()
        fake_msg.topic = "rcs/loader-01/state"
        fake_msg.payload = json.dumps({"device_id": "loader-01"}).encode()
        bridge._on_message(None, None, fake_msg)
        assert len(received) == 1
        assert received[0]["device_id"] == "loader-01"

    def test_hash_wildcard_matches_subtopics(self):
        bridge = self._make_bridge()
        received = []
        bridge.subscribe_state("rcs/#", lambda msg: received.append(msg))
        fake_msg = MagicMock()
        fake_msg.topic = "rcs/robot-01/state"
        fake_msg.payload = json.dumps({"device_id": "robot-01"}).encode()
        bridge._on_message(None, None, fake_msg)
        assert len(received) == 1

    def test_non_matching_wildcard_is_ignored(self):
        bridge = self._make_bridge()
        received = []
        bridge.subscribe_state("rcs/+/state", lambda msg: received.append(msg))
        fake_msg = MagicMock()
        fake_msg.topic = "rcs/robot-01/telemetry"
        fake_msg.payload = json.dumps({"device_id": "robot-01"}).encode()
        bridge._on_message(None, None, fake_msg)
        assert len(received) == 0
