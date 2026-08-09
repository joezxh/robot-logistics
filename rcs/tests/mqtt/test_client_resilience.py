"""A broker outage must never surface as an exception in RCS."""
from __future__ import annotations

from rcs.mqtt.client import MqttClient
from tests.mqtt.conftest import FakeMqttClient


class _StubPahoInfo:
    def __init__(self, rc: int) -> None:
        self.rc = rc


class _StubPaho:
    """Minimal stand-in for paho's Client, driving MqttClient's callbacks."""

    def __init__(self, publish_rc: int = 0, raise_on_publish: bool = False) -> None:
        self.subscribed: list[tuple[str, int]] = []
        self._publish_rc = publish_rc
        self._raise = raise_on_publish
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None

    def subscribe(self, topic: str, qos: int) -> None:
        self.subscribed.append((topic, qos))

    def publish(self, topic, payload, qos=0, retain=False):
        if self._raise:
            raise OSError("broker gone")
        return _StubPahoInfo(self._publish_rc)


def _client_with(stub: _StubPaho) -> MqttClient:
    c = MqttClient(host="localhost", port=1883, client_id="test")
    c._client = stub
    return c


def test_publish_failure_is_counted_not_raised() -> None:
    c = _client_with(_StubPaho(raise_on_publish=True))

    assert c.publish("rcs/robot-01/state", b"{}") is False
    assert c.publish_failures == 1
    assert c.publish_successes == 0


def test_publish_nonzero_rc_counts_as_failure() -> None:
    c = _client_with(_StubPaho(publish_rc=4))

    assert c.publish("rcs/robot-01/state", b"{}") is False
    assert c.publish_failures == 1


def test_publish_before_start_does_not_raise() -> None:
    c = MqttClient(host="localhost", port=1883, client_id="test")

    assert c.publish("rcs/robot-01/state", b"{}") is False
    assert c.publish_failures == 1


def test_subscriptions_are_replayed_on_reconnect() -> None:
    """clean_session drops server-side subscriptions, so we must re-issue them."""
    stub = _StubPaho()
    c = _client_with(stub)
    c.subscribe("rcs/+/command", 1, lambda t, p: None)
    assert stub.subscribed == []  # not connected yet

    c._on_connect(stub, None, {}, 0)
    assert stub.subscribed == [("rcs/+/command", 1)]

    c._on_disconnect(stub, None, 1)
    assert c.connected is False

    c._on_connect(stub, None, {}, 0)
    assert stub.subscribed == [("rcs/+/command", 1), ("rcs/+/command", 1)]
    assert c.connected is True


def test_refused_connection_leaves_client_disconnected() -> None:
    stub = _StubPaho()
    c = _client_with(stub)
    c.subscribe("rcs/+/command", 1, lambda t, p: None)

    c._on_connect(stub, None, {}, 5)  # 5 = not authorised

    assert c.connected is False
    assert stub.subscribed == []


def test_handler_exception_is_isolated() -> None:
    """A raising handler must not kill the message pump."""

    def boom(topic: str, payload: bytes) -> None:
        raise ValueError("handler bug")

    MqttClient._safe_invoke(boom, "rcs/robot-01/command", b"{}")  # no raise


def test_fake_client_rejects_unmatched_topic() -> None:
    """Guards the test double itself against silently swallowing messages."""
    fake = FakeMqttClient()
    fake.subscribe("rcs/+/command", 1, lambda t, p: None)

    try:
        fake.inject("rcs/robot-01/state", b"{}")
    except AssertionError:
        pass
    else:
        raise AssertionError("expected unmatched topic to be reported")
