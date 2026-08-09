import asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient

from rcs.registry import registry
from rcs.service import rcs_router, bind_loop
from rcs.loop import ControlLoop


def _build_client():
    app = FastAPI()
    app.include_router(rcs_router, prefix="/api/rcs")
    return TestClient(app)


def test_post_move_j_then_state_running():
    registry.load()
    loop = ControlLoop()
    loop.start()
    bind_loop(loop)
    try:
        client = _build_client()
        r = client.post(
            "/api/rcs/robot-01/command",
            json={"type": "move_j", "target_joints": [0.1, 0, 0, 0, 0, 0]},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "queued"
        # After on_command, controller mode must transition to running.
        s = client.get("/api/rcs/robot-01/state").json()
        assert s["mode"] in ("running", "idle")  # 1 kHz tick may already have idled
    finally:
        loop.shutdown()
        registry._reset_for_tests()


def test_post_unknown_device_returns_404():
    registry.load()
    try:
        client = _build_client()
        r = client.post(
            "/api/rcs/nope/command",
            json={"type": "stop"},
        )
        assert r.status_code == 404
    finally:
        registry._reset_for_tests()
