"""End-to-end tests for the FastAPI surface.

We bypass the lifespan startup to avoid binding uvicorn sockets and the SQLite
background tick. Tests that depend on Runtime state use the singleton directly.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import alerts as alerts_module
from backend.services import runtime as runtime_module


@pytest.fixture
def client():
    import asyncio as _asyncio

    from backend.algorithm.simulator.device import DeviceStatus
    from backend.services import alerts as alerts_module
    from backend.services import runtime as runtime_module

    # Reset state to a known baseline so the lifespan body does not crash
    # on stale scheduler entries from prior tests.
    rt = runtime_module.runtime
    rt.tasks.clear()
    rt.logs.clear()
    rt.reverted_tasks.clear()
    rt.scheduler.tasks.clear()
    rt.scheduler.completed.clear()
    for dev in rt.devices.devices.values():
        dev.battery = 100.0
        dev.status = DeviceStatus.IDLE
        dev.route = []
        dev.current_task = None
        dev.progress = 0.0
    alerts_module.engine.alerts.clear()
    alerts_module.engine.history.clear()
    alerts_module.engine._first_seen.clear()
    alerts_module.engine._subscribers.clear()

    with patch("backend.main.alert_engine") as engine_stub:
        engine_stub.snapshot.return_value = []
        engine_stub.evaluate.return_value = None
        engine_stub.subscribe.return_value = _asyncio.Queue()
        with TestClient(app) as c:
            yield c


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Robot Logic System" in r.json()["message"]


def test_devices_lists_seed(client):
    r = client.get("/api/devices")
    assert r.status_code == 200
    data = r.json()
    assert any(d["device_id"] == "robot-01" for d in data)


def test_create_task_happy_path(client):
    payload = {
        "type": "agv_transport",
        "description": "pytest",
        "priority": 3,
        "device_id": "agv-01",
    }
    r = client.post("/api/tasks", json=payload)
    assert r.status_code == 200
    assert r.json()["task_id"].startswith("task-")


def test_create_task_rejects_unknown_device(client):
    payload = {
        "type": "agv_transport",
        "description": "bad",
        "priority": 3,
        "device_id": "nope-99",
    }
    r = client.post("/api/tasks", json=payload)
    assert r.status_code == 400


def test_logs_returns_array(client):
    r = client.get("/api/logs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_metrics_prometheus_text(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    # The endpoint always emits the API hit counter, regardless of whether
    # the background tick loop has run.
    assert "# TYPE" in body
    assert "robot_logic_api_hits" in body


def test_alerts_returns_shape(client):
    r = client.get("/api/alerts")
    assert r.status_code == 200
    body = r.json()
    assert "firing" in body
    assert set(body["count_by_severity"].keys()) == {"info", "warning", "critical"}


def test_rollback_unknown_task_404(client):
    r = client.post("/api/tasks/missing-id/rollback")
    assert r.status_code == 404


def test_bulk_rollback_validates_devices(client):
    r = client.post("/api/devices/rollback", json={"device_ids": ["nope"], "limit_per_device": 1})
    assert r.status_code == 400


def test_bulk_rollback_success(client):
    # Seed a task that runs through completion so rollback has work to do.
    body = client.post("/api/tasks", json={"type": "agv_transport", "device_id": "agv-01", "description": "seed"}).json()
    task_id = body["task_id"]
    # Force task to completion directly via runtime to keep test deterministic.
    from backend.services import runtime as rt_module
    rt_module.runtime.tasks[task_id]["status"] = "completed"
    rt_module.runtime.tasks[task_id]["snapshot"] = {
        "position": [0.0, 0.0, 0.0],
        "battery": 100.0,
        "status": "idle",
        "route": [],
    }
    r = client.post("/api/devices/rollback", json={"device_ids": ["agv-01"], "limit_per_device": 1})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["rolled_back"][0]["device_id"] == "agv-01"


def test_stats_endpoint_returns_breakdown(client):
    r = client.get("/api/stats")
    assert r.status_code == 200
    body = r.json()
    assert "by_status" in body
    assert "by_type" in body
    assert "per_device_battery" in body
    assert isinstance(body["per_device_battery"], dict)
    assert "uptime_seconds" in body


def test_control_round_trip(client):
    r = client.post("/api/control", json={"action": "start"})
    assert r.status_code == 200
    body = r.json()
    assert "device_count" in body


def test_list_sites_seeded(client):
    r = client.get("/api/sites")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    assert any(s["kind"] == "dock" for s in body)
    assert any(s["kind"] == "warehouse" for s in body)


def test_create_and_delete_site(client):
    payload = {
        "id": "dock-Z", "kind": "dock", "name": "Dock Z",
        "x": 8.0, "z": 8.0, "color": "#ff00ff",
    }
    r = client.post("/api/sites", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "dock-Z"
    assert body["color"] == "#ff00ff"

    r2 = client.delete("/api/sites/dock-Z")
    assert r2.status_code == 200
    r3 = client.delete("/api/sites/dock-Z")
    assert r3.status_code == 404


def test_create_duplicate_site_conflict(client):
    payload = {"id": "rack-1", "kind": "warehouse", "name": "R1"}
    r = client.post("/api/sites", json=payload)
    assert r.status_code == 409


def test_patch_site(client):
    r = client.patch("/api/sites/dock-A", json={"status": "blocked", "x": 9.5})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "blocked"
    assert body["position"][0] == 9.5


def test_register_and_delete_custom_device(client):
    payload = {
        "device_id": "agv-99",
        "device_type": "agv",
        "name": "AGV 99",
        "x": 1.0, "z": -1.0,
    }
    r = client.post("/api/devices/register", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["device_id"] == "agv-99"
    assert body["device_type"] == "agv"

    r2 = client.delete("/api/devices/agv-99")
    assert r2.status_code == 200


def test_register_duplicate_conflict(client):
    payload = {"device_id": "agv-01", "device_type": "agv", "name": "dup"}
    r = client.post("/api/devices/register", json=payload)
    assert r.status_code == 409


def test_patch_device(client):
    r = client.patch("/api/devices/agv-01", json={"battery": 42.5, "name": "AGV One"})
    assert r.status_code == 200
    body = r.json()
    assert body["battery"] == 42.5
    assert body["name"] == "AGV One"
