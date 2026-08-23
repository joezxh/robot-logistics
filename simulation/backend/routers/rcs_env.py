"""RCS-aligned simulation API router.

Exposes the robot-logic ``rcs_env`` layer (Gym env, planner, extension registry)
over HTTP so the RCS-facing stack can be driven through the same port as the
legacy logistics API. This mirrors how RCS serves its env/planner.

The router is intentionally thin — it delegates all logic to ``backend.rcs_env``.
"""
from __future__ import annotations

import threading
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from robot_contracts import RobotType

from backend.rcs_env import SimEnv, MjOMPL, Planner
from backend.rcs_env.envs.configs import get_config
from backend.rcs_env.extensions import all_extensions

router = APIRouter(prefix="/api/rcs-env", tags=["rcs-env"])

# Envs are stateful; keep one per session id (simple in-process registry).
_ENVS: dict[str, SimEnv] = {}
_LOCK = threading.Lock()


class EnvCreate(BaseModel):
    config_name: str = Field("LogisticsArm", description="Key from rcs_env.envs.configs")
    session_id: str = "default"


class StepRequest(BaseModel):
    session_id: str = "default"
    action: list[float]


class PlanRequest(BaseModel):
    session_id: str = "default"
    goal: list[float]
    planner: str = "RRTConnect"
    se3: bool = False
    goal_pose: list[float] | None = None


def _get_env(session_id: str) -> SimEnv:
    with _LOCK:
        if session_id not in _ENVS:
            raise HTTPException(status_code=404, detail=f"no env for session {session_id!r}")
        return _ENVS[session_id]


@router.get("/configs")
async def list_configs() -> dict[str, Any]:
    from backend.rcs_env.envs.configs import CONFIGS

    return {name: {"robot_type": c.robot_type.value, "has_camera": c.has_camera,
                   "has_gripper": c.has_gripper} for name, c in CONFIGS.items()}


@router.get("/extensions")
async def list_extensions() -> list[dict]:
    return [
        {"key": e.key, "kind": e.kind, "robot_type": e.robot_type.value if e.robot_type else None,
         "device_type": e.device_type}
        for e in all_extensions()
    ]


@router.post("/create")
async def create_env(req: EnvCreate) -> dict:
    cfg = get_config(req.config_name)
    with _LOCK:
        if req.session_id in _ENVS:
            del _ENVS[req.session_id]
        env = SimEnv(robot_type=cfg.robot_type, mjcf_path=cfg.mjcf_path,
                     logic_device_id=cfg.logic_device_id, planner=cfg.planner)
        env.reset()
        _ENVS[req.session_id] = env
    return {"session_id": req.session_id, "dof": env.engine.dof,
            "robot_type": cfg.robot_type.value}


@router.post("/step")
async def step_env(req: StepRequest) -> dict:
    env = _get_env(req.session_id)
    obs, reward, terminated, truncated, info = env.step(np.array(req.action, dtype=float))
    ee = info["ee_pose"]
    return {"obs": obs.tolist(), "reward": reward, "terminated": terminated,
            "truncated": truncated, "ee": ee.to_dict()}


@router.post("/plan")
async def plan_env(req: PlanRequest) -> dict:
    env = _get_env(req.session_id)
    planner = Planner(req.planner)
    if req.se3 and req.goal_pose is not None:
        path = env.ompl.plan_SE3(np.array(req.goal_pose, dtype=float), planner)
    else:
        path = env.ompl.plan(env.engine.qpos(), np.array(req.goal, dtype=float), planner)
    return {"waypoints": [p.tolist() for p in path], "length": len(path)}


@router.delete("/{session_id}")
async def drop_env(session_id: str) -> dict:
    with _LOCK:
        _ENVS.pop(session_id, None)
    return {"dropped": session_id}
