from fastapi import FastAPI
from fastapi.testclient import TestClient

from rcs.registry import registry
from rcs.service import rcs_router, bind_loop
from rcs.loop import ControlLoop


def test_queue_overflow_503():
    registry.load()
    try:
        app = FastAPI()
        app.include_router(rcs_router, prefix="/api/rcs")
        client = TestClient(app)
        # ArmController uses a CommandQueue(maxsize=1024). Fill it to capacity
        # with unique command_ids; the 1025th POST must return 503.
        for i in range(1024):
            r = client.post(
                "/api/rcs/robot-01/command",
                json={"type": "stop", "command_id": f"warmup-{i}"},
            )
            assert r.status_code == 200, f"unexpected {r.status_code} on warmup {i}"
        r = client.post(
            "/api/rcs/robot-01/command",
            json={"type": "stop", "command_id": "overflow-1"},
        )
        assert r.status_code == 503
        assert r.headers.get("Retry-After") == "1"
    finally:
        registry._reset_for_tests()
