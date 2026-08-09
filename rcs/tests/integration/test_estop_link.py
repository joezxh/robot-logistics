from fastapi import FastAPI
from fastapi.testclient import TestClient

from rcs.registry import registry
from rcs.service import rcs_router, bind_loop
from rcs.loop import ControlLoop


def _build_client():
    app = FastAPI()
    app.include_router(rcs_router, prefix="/api/rcs")
    return TestClient(app)


def test_estop_endpoint_sets_mode():
    registry.load()
    try:
        client = _build_client()
        r = client.post("/api/rcs/robot-01/estop")
        assert r.status_code == 200
        s = client.get("/api/rcs/robot-01/state").json()
        assert s["mode"] == "e_stop"
        r = client.post("/api/rcs/robot-01/clear_estop")
        assert r.status_code == 200
        s = client.get("/api/rcs/robot-01/state").json()
        assert s["mode"] == "idle"
    finally:
        registry._reset_for_tests()
