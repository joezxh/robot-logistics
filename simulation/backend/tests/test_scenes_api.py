"""Tests for /api/scenes endpoints via FastAPI TestClient."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.runtime import runtime


@pytest.fixture(autouse=True)
def _reset_runtime_after_test():
    yield
    runtime.reset()
    runtime.current_scene = None


def test_list_scenes_returns_three():
    client = TestClient(app)
    res = client.get("/api/scenes")
    assert res.status_code == 200
    body = res.json()
    assert set(body["available"]) == {"pallet", "box", "bag"}


def test_load_scene_pallet_succeeds():
    client = TestClient(app)
    res = client.post("/api/scenes/load/pallet")
    assert res.status_code == 200
    assert res.json()["scene"] == "pallet"


def test_load_scene_unknown_returns_404():
    client = TestClient(app)
    res = client.post("/api/scenes/load/nope")
    assert res.status_code == 404


def test_current_scene_404_when_none_loaded():
    client = TestClient(app)
    res = client.get("/api/scenes/current")
    assert res.status_code == 404


def test_current_scene_returns_preset_when_loaded():
    client = TestClient(app)
    client.post("/api/scenes/load/box")
    res = client.get("/api/scenes/current")
    assert res.status_code == 200
    assert res.json()["name"] == "box"


def test_scene_kpi_returns_snapshot():
    client = TestClient(app)
    client.post("/api/scenes/load/bag")
    res = client.get("/api/scenes/bag/kpi")
    assert res.status_code == 200
    body = res.json()
    assert body["scene"] == "bag"
    assert "throughput_per_hour" in body


def test_device_create_accepts_pallet_forklift_type():
    client = TestClient(app)
    res = client.post(
        "/api/devices/register",
        json={
            "device_id": "test-fork-01",
            "device_type": "pallet_forklift",
            "name": "test",
            "x": 0.0, "z": 0.0,
        },
    )
    assert res.status_code == 200
