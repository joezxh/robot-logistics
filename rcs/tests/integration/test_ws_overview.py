import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from rcs.registry import registry
from rcs.service import rcs_router, bind_loop
from rcs.loop import ControlLoop


def _build_app():
    app = FastAPI()
    app.include_router(rcs_router, prefix="/api/rcs")
    return app


def test_ws_overview_streams_frames():
    registry.load()
    loop = ControlLoop()
    loop.start()
    bind_loop(loop)
    try:
        # Subscribe to the StateStream directly and push a synthetic frame.
        from rcs.state.joint import JointState
        from rcs.state.error import TrackingError
        from rcs.state.controller_state import ControllerState

        q = loop.stream.subscribe()
        loop.stream.force_publish(
            "robot-01",
            JointState(positions=[0.0]*6, velocities=[0.0]*6, efforts=[0.0]*6, device_id="robot-01"),
            TrackingError(max_joint_error=0.0, position_error_m=0.0),
            ControllerState(),
        )
        data = q.get_nowait()
        assert b"robot-01" in data
        loop.stream.unsubscribe(q)
    finally:
        loop.shutdown()
        registry._reset_for_tests()
