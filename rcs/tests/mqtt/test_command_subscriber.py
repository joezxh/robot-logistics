"""Inbound MQTT commands must behave exactly like the REST equivalent."""
from __future__ import annotations

import json

import pytest

from rcs.dispatch import COMMAND_QUEUE_MAXSIZE
from rcs.mqtt.subscriber import CommandSubscriber
from rcs.registry import registry
from rcs.state.command import CommandType
from rcs.state.controller_state import ControllerMode
from robot_contracts import QOS_COMMAND, command_topic, command_topic_filter


@pytest.fixture
def device_id() -> str:
    """Yield a device whose controller queue is clean.

    ``registry`` is a process-wide singleton, so without this the queue (and its
    ``command_id`` idempotency set) would leak between tests.
    """
    registry.load()
    dev = registry.list_devices()[0].device_id
    _reset_queue(dev)
    yield dev
    _reset_queue(dev)


def _reset_queue(device_id: str) -> None:
    ctrl = registry.get_controller(device_id)
    # Mode must be reset too: on_command() silently drops everything while the
    # controller sits in E_STOP/HALTED/FAULT, and estop() is not undone by
    # recover() (that only clears HALTED).
    ctrl.state.mode = ControllerMode.IDLE
    ctrl.state.active_command_id = None
    ctrl.state.last_error = None
    queue = getattr(ctrl, "_queue", None)
    if queue is None:
        return
    queue._q.clear()
    queue._seen.clear()


def _drain(ctrl) -> list:
    """Pop the whole queue -- CommandQueue is not subscriptable."""
    items = []
    while (item := ctrl._queue.pop()) is not None:
        items.append(item)
    return items


async def test_subscribes_to_command_wildcard(fake_client) -> None:
    sub = CommandSubscriber(fake_client)
    await sub.start()
    assert fake_client.subscriptions == [(command_topic_filter(), QOS_COMMAND)]


async def test_valid_command_reaches_controller(fake_client, device_id) -> None:
    sub = CommandSubscriber(fake_client)
    await sub.start()
    ctrl = registry.get_controller(device_id)
    n_joints = registry.get_profile(device_id).num_joints

    fake_client.inject(
        command_topic(device_id),
        json.dumps({"type": "move_j", "target_joints": [0.1] * n_joints}).encode(),
    )

    assert sub.accepted == 1
    assert sub.rejected == 0
    queued = _drain(ctrl)
    assert len(queued) == 1
    assert queued[0].type is CommandType.MOVE_J


async def test_command_id_is_preserved(fake_client, device_id) -> None:
    sub = CommandSubscriber(fake_client)
    await sub.start()
    ctrl = registry.get_controller(device_id)
    n_joints = registry.get_profile(device_id).num_joints

    fake_client.inject(
        command_topic(device_id),
        json.dumps(
            {"command_id": "cmd-42", "type": "move_j", "target_joints": [0.0] * n_joints}
        ).encode(),
    )

    assert _drain(ctrl)[-1].command_id == "cmd-42"


async def test_missing_command_id_is_generated(fake_client, device_id) -> None:
    sub = CommandSubscriber(fake_client)
    await sub.start()
    ctrl = registry.get_controller(device_id)
    n_joints = registry.get_profile(device_id).num_joints

    fake_client.inject(
        command_topic(device_id),
        json.dumps({"type": "move_j", "target_joints": [0.0] * n_joints}).encode(),
    )

    assert _drain(ctrl)[-1].command_id  # non-empty uuid


async def test_estop_bypasses_the_queue(fake_client, device_id) -> None:
    """Safety commands must take effect even though they never enqueue."""
    sub = CommandSubscriber(fake_client)
    await sub.start()
    ctrl = registry.get_controller(device_id)

    fake_client.inject(command_topic(device_id), json.dumps({"type": "estop"}).encode())

    assert sub.accepted == 1
    assert len(ctrl._queue) == 0
    assert ctrl.state.mode is ControllerMode.E_STOP
    ctrl.clear_estop()


@pytest.mark.parametrize(
    "raw",
    [
        b"not json at all",
        b"{}",  # missing required "type"
        json.dumps({"type": "fly_away"}).encode(),  # not in the enum
        json.dumps({"type": "move_j", "speed_scale": 99}).encode(),  # above the cap
        json.dumps({"type": "move_j", "speed_scale": -1}).encode(),  # below the floor
    ],
)
async def test_malformed_payloads_are_dropped(fake_client, device_id, raw) -> None:
    sub = CommandSubscriber(fake_client)
    await sub.start()
    ctrl = registry.get_controller(device_id)
    before = len(ctrl._queue)

    fake_client.inject(command_topic(device_id), raw)

    assert sub.rejected == 1
    assert sub.accepted == 0
    assert len(ctrl._queue) == before


async def test_unknown_device_is_rejected(fake_client) -> None:
    registry.load()
    sub = CommandSubscriber(fake_client)
    await sub.start()

    fake_client.inject(
        command_topic("does-not-exist"), json.dumps({"type": "stop"}).encode()
    )

    assert sub.rejected == 1
    assert sub.accepted == 0


async def test_queue_full_applies_backpressure(fake_client, device_id) -> None:
    """MQTT must honour the same 1024-deep limit the REST route enforces."""
    sub = CommandSubscriber(fake_client)
    await sub.start()
    ctrl = registry.get_controller(device_id)
    n_joints = registry.get_profile(device_id).num_joints

    def payload(i: int) -> bytes:
        # Distinct command_id per message: the queue de-duplicates by id, so
        # replaying one payload would never actually fill it.
        return json.dumps(
            {
                "command_id": f"cmd-{i}",
                "type": "move_j",
                "target_joints": [0.0] * n_joints,
            }
        ).encode()

    for i in range(COMMAND_QUEUE_MAXSIZE):
        fake_client.inject(command_topic(device_id), payload(i))
    assert len(ctrl._queue) == COMMAND_QUEUE_MAXSIZE
    assert sub.rejected == 0

    fake_client.inject(command_topic(device_id), payload(COMMAND_QUEUE_MAXSIZE))

    assert sub.rejected == 1
    assert len(ctrl._queue) == COMMAND_QUEUE_MAXSIZE  # did not grow


async def test_topic_prefix_is_honoured(fake_client, device_id) -> None:
    sub = CommandSubscriber(fake_client, topic_prefix="site-a")
    await sub.start()
    ctrl = registry.get_controller(device_id)
    n_joints = registry.get_profile(device_id).num_joints

    fake_client.inject(
        command_topic(device_id, "site-a"),
        json.dumps({"type": "move_j", "target_joints": [0.0] * n_joints}).encode(),
    )

    assert sub.accepted == 1
    assert len(ctrl._queue) == 1
