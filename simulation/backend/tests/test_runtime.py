"""Tests for the in-memory Runtime and task scheduler."""
from __future__ import annotations

import pytest

from backend.algorithm.scheduler.task import Task, TaskPriority
from backend.algorithm.scheduler.scheduler import TaskScheduler
from backend.services.runtime import runtime as global_runtime  # noqa: F401
from backend.services import runtime as runtime_module


def test_scheduler_prioritizes_critical() -> None:
    scheduler = TaskScheduler()
    low = Task("t-low", "x", priority=TaskPriority.LOW)
    critical = Task("t-crit", "x", priority=TaskPriority.CRITICAL)
    high = Task("t-high", "x", priority=TaskPriority.HIGH)
    scheduler.add_task(low)
    scheduler.add_task(critical)
    scheduler.add_task(high)
    batch = scheduler.get_next_batch(max_concurrent=3)
    assert [t.task_id for t in batch] == ["t-crit", "t-high", "t-low"]


def test_scheduler_rejects_cycle() -> None:
    scheduler = TaskScheduler()
    a = Task("a", "x")
    b = Task("b", "x")
    a.dependencies = ["b"]
    b.dependencies = ["a"]
    scheduler.add_task(a)
    with pytest.raises(ValueError):
        scheduler.add_task(b)


def test_scheduler_respects_dependencies() -> None:
    scheduler = TaskScheduler()
    a = Task("a", "x")
    b = Task("b", "x")
    b.dependencies = ["a"]
    scheduler.add_task(a)
    scheduler.add_task(b)
    first = scheduler.get_next_batch(max_concurrent=10)
    assert [t.task_id for t in first] == ["a"]
    scheduler.mark_completed("a")
    second = scheduler.get_next_batch(max_concurrent=10)
    assert [t.task_id for t in second] == ["b"]


def test_create_task_assigns_id(fresh_runtime) -> None:
    record = fresh_runtime.create_task(
        "agv_transport", "demo", TaskPriority.NORMAL, "agv-01"
    )
    assert record["task_id"].startswith("task-")
    assert record["status"] == "pending"
    assert record["device_id"] == "agv-01"
    assert fresh_runtime.tasks[record["task_id"]] is record


def test_tick_progresses_running_tasks_until_complete(fresh_runtime) -> None:
    record = fresh_runtime.create_task(
        "agv_transport", "demo", TaskPriority.HIGH, "agv-01"
    )
    fresh_runtime.start()
    # Force starting.
    fresh_runtime._start_task(record["task_id"])
    for _ in range(20):
        fresh_runtime.tick(0.5)
    final = fresh_runtime.tasks[record["task_id"]]
    assert final["status"] == "completed"
    assert final["progress"] == 100


def test_rollback_restores_device_snapshot(fresh_runtime) -> None:
    from backend.algorithm.simulator.device import DeviceStatus

    device = fresh_runtime.devices.get("agv-01")
    snapshot_position = list(device.position)
    snapshot_battery = device.battery

    record = fresh_runtime.create_task(
        "agv_transport", "demo", TaskPriority.HIGH, "agv-01"
    )
    fresh_runtime.start()
    fresh_runtime._start_task(record["task_id"])
    for _ in range(20):
        fresh_runtime.tick(0.5)

    # Even if the route's terminal point happens to coincide with the
    # starting position, running 20 ticks drains the battery.
    assert device.battery < snapshot_battery
    assert device.status != DeviceStatus.IDLE or device.battery < snapshot_battery

    fresh_runtime.rollback_task(record["task_id"])

    assert device.position == snapshot_position
    assert device.battery == pytest.approx(snapshot_battery, abs=0.01)
    assert device.status == DeviceStatus.IDLE
    assert fresh_runtime.tasks[record["task_id"]]["status"] == "reverted"


def test_rollback_rejects_pending_task(fresh_runtime) -> None:
    record = fresh_runtime.create_task(
        "agv_transport", "demo", TaskPriority.NORMAL, "agv-01"
    )
    with pytest.raises(RuntimeError):
        fresh_runtime.rollback_task(record["task_id"])


def test_log_emits_publishes_to_subscribers(fresh_runtime) -> None:
    import asyncio
    asyncio.run(_collect_log())


async def _collect_log() -> None:
    from backend.services import runtime as runtime_module

    rt = runtime_module.runtime
    queue = rt.subscribe()
    rt.log("trace-x", None, "test", "hello")
    entry = await queue.get()
    assert entry["message"] == "hello"
    assert entry["level"] == "INFO"
    rt.unsubscribe(queue)


def test_rollback_devices_filters_per_device(fresh_runtime) -> None:
    a = fresh_runtime.create_task("agv_transport", "a", TaskPriority.NORMAL, "agv-01")
    b = fresh_runtime.create_task("agv_transport", "b", TaskPriority.NORMAL, "agv-01")
    c = fresh_runtime.create_task("agv_transport", "c", TaskPriority.NORMAL, "agv-02")
    fresh_runtime.start()
    for t in (a, b, c):
        fresh_runtime._start_task(t["task_id"])
        for _ in range(20):
            fresh_runtime.tick(0.5)

    assert fresh_runtime.tasks[a["task_id"]]["status"] == "completed"
    assert fresh_runtime.tasks[c["task_id"]]["status"] == "completed"

    result = fresh_runtime.rollback_devices(["agv-01"], limit_per_device=5)
    assert result["total"] == 2
    assert fresh_runtime.tasks[a["task_id"]]["status"] == "reverted"
    assert fresh_runtime.tasks[b["task_id"]]["status"] == "reverted"
    # agv-02 untouched
    assert fresh_runtime.tasks[c["task_id"]]["status"] == "completed"


def test_rollback_devices_respects_per_device_limit(fresh_runtime) -> None:
    a = fresh_runtime.create_task("agv_transport", "a", TaskPriority.NORMAL, "agv-01")
    b = fresh_runtime.create_task("agv_transport", "b", TaskPriority.NORMAL, "agv-01")
    fresh_runtime.start()
    for t in (a, b):
        fresh_runtime._start_task(t["task_id"])
        for _ in range(20):
            fresh_runtime.tick(0.5)

    result = fresh_runtime.rollback_devices(["agv-01"], limit_per_device=1)
    assert result["total"] == 1
    # Exactly one is reverted; the other stays completed.
    statuses = sorted([
        fresh_runtime.tasks[a["task_id"]]["status"],
        fresh_runtime.tasks[b["task_id"]]["status"],
    ])
    assert statuses == ["completed", "reverted"]
