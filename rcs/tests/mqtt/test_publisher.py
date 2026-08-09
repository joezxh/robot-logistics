"""State downsampling and EventBus alert forwarding."""
from __future__ import annotations

import asyncio
import json

import pytest

from rcs.loop import ControlLoop
from rcs.mqtt.publisher import AlertPublisher, StatePublisher
from rcs.state.controller_state import ControllerMode, ControllerState
from rcs.state.error import TrackingError
from rcs.state.joint import JointState
from robot_contracts import QOS_ALERT, QOS_STATE, RETAIN_ALERT, RETAIN_STATE


def _emit(loop: ControlLoop, device_id: str = "robot-01") -> None:
    """Push one frame through StateStream, bypassing its own 10 Hz limiter so the
    test exercises the publisher's downsampling in isolation."""
    loop.stream.force_publish(
        device_id,
        JointState(positions=[0.0] * 6, velocities=[0.0] * 6, efforts=[0.0] * 6),
        TrackingError(max_joint_error=0.0, position_error_m=0.0),
        ControllerState(mode=ControllerMode.IDLE),
    )


async def _drain() -> None:
    """Let the publisher task consume whatever is queued."""
    for _ in range(5):
        await asyncio.sleep(0)


async def test_state_is_published_on_the_right_topic(fake_client) -> None:
    loop = ControlLoop()
    pub = StatePublisher(fake_client, loop, publish_hz=1000.0)
    await pub.start()

    _emit(loop)
    await _drain()

    assert fake_client.topics() == ["rcs/robot-01/state"]
    topic, payload, qos, retain = fake_client.published[0]
    assert qos == QOS_STATE
    assert retain is RETAIN_STATE
    assert json.loads(payload)["device_id"] == "robot-01"

    await pub.stop()


async def test_state_payload_is_forwarded_unmodified(fake_client) -> None:
    """StateStream already emits JSON; re-encoding would waste the hot path."""
    loop = ControlLoop()
    pub = StatePublisher(fake_client, loop, publish_hz=1000.0)
    await pub.start()

    _emit(loop)
    await _drain()

    body = json.loads(fake_client.published[0][1])
    assert body["joint"]["positions"] == [0.0] * 6
    assert body["ctrl"]["mode"] == ControllerMode.IDLE.value
    assert "iso_ts" in body

    await pub.stop()


async def test_downsampling_drops_frames_above_the_rate(fake_client) -> None:
    loop = ControlLoop()
    # 1 Hz: only the first of a rapid burst should go out.
    pub = StatePublisher(fake_client, loop, publish_hz=1.0)
    await pub.start()

    for _ in range(10):
        _emit(loop)
    await _drain()

    assert len(fake_client.published) == 1
    assert pub.dropped == 9

    await pub.stop()


async def test_downsampling_is_per_device(fake_client) -> None:
    """One chatty device must not starve another."""
    loop = ControlLoop()
    pub = StatePublisher(fake_client, loop, publish_hz=1.0)
    await pub.start()

    _emit(loop, "robot-01")
    _emit(loop, "agv-01")
    await _drain()

    assert sorted(fake_client.topics()) == ["rcs/agv-01/state", "rcs/robot-01/state"]

    await pub.stop()


async def test_publish_hz_zero_disables_state(fake_client) -> None:
    loop = ControlLoop()
    pub = StatePublisher(fake_client, loop, publish_hz=0.0)
    await pub.start()

    _emit(loop)
    await _drain()

    assert fake_client.published == []

    await pub.stop()


async def test_stop_unsubscribes_from_the_stream(fake_client) -> None:
    """A leaked queue would grow unbounded behind the 1 kHz loop."""
    loop = ControlLoop()
    pub = StatePublisher(fake_client, loop, publish_hz=1000.0)
    await pub.start()
    assert len(loop.stream._subscribers) == 1

    await pub.stop()

    assert len(loop.stream._subscribers) == 0


async def test_state_topic_prefix(fake_client) -> None:
    loop = ControlLoop()
    pub = StatePublisher(fake_client, loop, publish_hz=1000.0, topic_prefix="site-a")
    await pub.start()

    _emit(loop)
    await _drain()

    assert fake_client.topics() == ["site-a/rcs/robot-01/state"]

    await pub.stop()


@pytest.mark.parametrize(
    "event", ["hal_read_timeout", "hal_write_failure", "controller_halted"]
)
async def test_each_event_bus_alert_is_forwarded(fake_client, event: str) -> None:
    loop = ControlLoop()
    pub = AlertPublisher(fake_client, loop)
    await pub.start()

    loop.bus.publish(event, {"device_id": "robot-01", "error": "boom"})

    assert len(fake_client.published) == 1
    topic, payload, qos, retain = fake_client.published[0]
    assert topic == "rcs/robot-01/alert"
    assert qos == QOS_ALERT
    assert retain is RETAIN_ALERT
    body = json.loads(payload)
    assert body["event"] == event
    assert body["device_id"] == "robot-01"
    assert body["error"] == "boom"
    assert body["iso_ts"].endswith("Z")

    await pub.stop()


async def test_alert_without_device_id_is_ignored(fake_client) -> None:
    loop = ControlLoop()
    pub = AlertPublisher(fake_client, loop)
    await pub.start()

    loop.bus.publish("controller_halted", {})

    assert fake_client.published == []

    await pub.stop()


async def test_alert_stop_unsubscribes(fake_client) -> None:
    loop = ControlLoop()
    pub = AlertPublisher(fake_client, loop)
    await pub.start()
    await pub.stop()

    loop.bus.publish("controller_halted", {"device_id": "robot-01"})

    assert fake_client.published == []
