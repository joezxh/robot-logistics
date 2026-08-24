"""RCS — Robot Control System (embedded control runtime).

This package is now embedded directly inside ``rcs_backend`` (single process):
the backend's :mod:`rcs.main` imports :func:`lifespan` and
:func:`router` to mount the control endpoints and drive the control loop.
"""
from __future__ import annotations
from contextlib import asynccontextmanager

from .registry import registry
from .loop import ControlLoop
from .service import rcs_router, bind_loop
from .control import ControlMode, CartesianCommand, ee_pose_in_world
from .state.pose import Pose6D, world_from_base_pose, robot_from_world_pose


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
    """Return the FastAPI router for the control endpoints."""
    _ensure_loaded()
    return rcs_router


__all__ = [
    "lifespan", "router",
    "ControlMode", "CartesianCommand", "ee_pose_in_world",
    "Pose6D", "world_from_base_pose", "robot_from_world_pose",
]
