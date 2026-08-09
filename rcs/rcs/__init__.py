"""RCS — Robot Control System.

Standalone subproject controlling loading/unloading robots and related logistics
robot facilities. Runs either embedded in the simulation backend (via
:func:`router` / :func:`lifespan`) or as an independent FastAPI service (via
``rcs.app:create_app``).
"""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager

from .registry import registry
from .loop import ControlLoop
from .service import rcs_router, bind_loop


_loop: ControlLoop | None = None


def _ensure_loaded() -> ControlLoop:
    global _loop
    registry.load()
    if _loop is None:
        _loop = ControlLoop()
        bind_loop(_loop)
    return _loop


@asynccontextmanager
async def lifespan():
    loop = _ensure_loaded()
    try:
        loop.start()
        yield
    finally:
        loop.shutdown()


def router():
    """Return the FastAPI router for the RCS-1 endpoints."""
    _ensure_loaded()
    return rcs_router


def create_app():
    """Build the standalone RCS FastAPI app.

    Imported lazily so that embedded users (who only need the router) never pay
    for the standalone app's middleware imports.
    """
    from .app import create_app as _create_app

    return _create_app()


# `rcs` is the public façade used by the simulation backend:
# `from rcs import rcs`. It exposes the same `lifespan()` and `router()`
# callables plus the bound ControlLoop for tests that want to inspect health.
class _RCSFacade:
    lifespan = staticmethod(lifespan)
    router = staticmethod(router)
    create_app = staticmethod(create_app)
    loop = property(lambda self: _ensure_loaded())


rcs = _RCSFacade()


__all__ = ["lifespan", "router", "create_app", "rcs"]
