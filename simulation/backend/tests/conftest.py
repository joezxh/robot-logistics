"""Shared pytest fixtures.

The tests import the FastAPI app via httpx, but we deliberately do NOT start
uvicorn. Settings override the database to a temp file (so test runs leave no
state behind) and disable auth + rate limiting by default so individual tests
opt-in via dedicated env fixtures.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
# The monorepo root (two levels above `simulation/`) must also be importable so
# the embedded RCS package (`rcs/rcs`) can be imported when RCS_EMBEDDED is on.
MONOREPO_ROOT = Path(__file__).resolve().parents[3]
if str(MONOREPO_ROOT) not in sys.path:
    sys.path.insert(0, str(MONOREPO_ROOT))
# The shared contract package lives at `shared/python` (one level above the
# simulation repo). Make it importable so the RCS-aligned layer can use it.
SHARED_PY = MONOREPO_ROOT / "shared" / "python"
if str(SHARED_PY) not in sys.path:
    sys.path.insert(0, str(SHARED_PY))


@pytest.fixture(scope="session", autouse=True)
def _test_environment() -> None:
    """Configure isolated environment variables for the entire test session."""
    tmp = Path(tempfile.mkdtemp(prefix="robot-logic-test-"))
    db_path = tmp / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
    os.environ["API_AUTH_ENABLED"] = "0"
    os.environ["API_API_KEYS"] = ""
    tmp.mkdir(parents=True, exist_ok=True)
    yield
    # Best-effort cleanup
    try:
        db_path.unlink(missing_ok=True)
    except Exception:  # pragma: no cover - cleanup only
        pass


@pytest.fixture
def fresh_runtime():
    """Reset the Runtime singleton state between unit tests."""
    from backend.algorithm.simulator.device import DeviceStatus
    from backend.services import runtime as runtime_module
    from backend.services import alerts as alerts_module

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
    rt._subscribers.clear()
    return rt


@pytest.fixture
def client():
    """An httpx TestClient wrapping the FastAPI app.

    Note: we do NOT exercise startup/shutdown lifespan hooks because they bind
    sockets and database connections across the whole suite. Tests that need
    the lifespan-managed runtime should use the fresh_runtime fixture directly.
    """
    from fastapi.testclient import TestClient
    from backend.main import app
    with patch("backend.main.runtime") as rt:
        # Use the same singleton but bypass lifespan by raising it.
        rt.start = lambda: {"running": True}
        rt.stop = lambda: {"running": False}
        with TestClient(app) as c:
            yield c


@pytest.fixture(autouse=True)
def _reset_singletons():
    """Reset the singletons touched by the suite.

    The autouse fixture keeps each test isolated regardless of which fixture(s)
    a particular test pulls in.
    """
    from backend.services import alerts as alerts_module
    from backend.services import runtime as runtime_module
    from backend.algorithm.simulator.device import DeviceStatus

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
    rt._subscribers.clear()
    yield
