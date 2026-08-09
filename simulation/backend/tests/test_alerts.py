"""Tests for AlertEngine rules."""
from __future__ import annotations

from backend.algorithm.scheduler.task import TaskPriority
from backend.services import alerts as alerts_module
from backend.services.alerts import AlertSeverity, engine
from backend.services import runtime as runtime_module


def _run(runtime) -> None:
    engine.evaluate(runtime)


def test_battery_low_triggers_warning_then_critical(fresh_runtime) -> None:
    rt = fresh_runtime
    device = rt.devices.get("agv-01")
    device.battery = 15.0
    _run(rt)
    alerts = engine.snapshot()
    assert any(a["alert_key"].endswith("agv-01") and a["severity"] == "warning" for a in alerts)
    device.battery = 3.0
    _run(rt)
    alerts = engine.snapshot()
    keys = {a["alert_key"]: a for a in alerts}
    assert keys[f"device_battery_low:agv-01"]["severity"] == AlertSeverity.CRITICAL.value


def test_device_fault_alert(fresh_runtime) -> None:
    from backend.algorithm.simulator.device import DeviceStatus

    rt = fresh_runtime
    rt.devices.get("robot-01").status = DeviceStatus.FAULT
    _run(rt)
    alerts = {a["alert_key"]: a for a in engine.snapshot()}
    assert alerts["device_fault:robot-01"]["severity"] == AlertSeverity.CRITICAL.value


def test_queue_backlog_only_when_pending_above_threshold(fresh_runtime) -> None:
    rt = fresh_runtime
    # 4 pending: should NOT trigger.
    for i in range(4):
        rt.create_task("agv_transport", f"q-{i}", TaskPriority.LOW, "agv-01")
    _run(rt)
    assert not any(a["alert_key"] == "queue_backlog:global" for a in engine.snapshot())
    # 5th: should trigger.
    rt.create_task("agv_transport", "q-4", TaskPriority.LOW, "agv-01")
    _run(rt)
    assert any(a["alert_key"] == "queue_backlog:global" for a in engine.snapshot())


def test_resolved_alerts_leave_active_dict(fresh_runtime) -> None:
    rt = fresh_runtime
    rt.devices.get("agv-01").battery = 10
    _run(rt)
    before = len(engine.snapshot())
    assert before == 1
    rt.devices.get("agv-01").battery = 99
    _run(rt)
    # Re-evaluate after battery is healthy — the alert should resolve and drop.
    after = engine.snapshot()
    assert after == []


def test_sse_publish_on_fire_and_resolve(fresh_runtime) -> None:
    import asyncio

    async def scenario():
        queue = engine.subscribe()
        rt = fresh_runtime
        rt.devices.get("agv-01").battery = 5
        _run(rt)
        fired = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert fired["state"] == "firing"
        # Now heal the battery.
        rt.devices.get("agv-01").battery = 100
        _run(rt)
        resolved = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert resolved["state"] == "resolved"
        engine.unsubscribe(queue)

    asyncio.run(scenario())


def test_alert_ack_persists_state(fresh_runtime) -> None:
    rt = fresh_runtime
    rt.devices.get("agv-01").battery = 10
    _run(rt)
    target = engine.snapshot()[0]
    engine.acknowledge(target["id"], by="pytest")
    after = engine.snapshot()
    assert after[0]["state"] == "acknowledged"
    assert after[0]["acknowledged_by"] == "pytest"
