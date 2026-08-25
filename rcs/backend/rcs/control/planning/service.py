"""Trajectory planning profile library (persisted, reusable)."""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from rcs.db import models, session as db_session


async def create(name: str, algo: str, axes: int, vel_max: list,
                 acc_max: list, created_by: Optional[str] = None) -> dict:
    async for s in db_session.session():
        p = models.PlanningProfile(name=name, algo=algo, axes=axes,
                                   vel_max_json=vel_max or [],
                                   acc_max_json=acc_max or [],
                                   created_by=created_by)
        s.add(p)
        await s.commit()
        await s.refresh(p)
        return _to_dict(p)
    raise RuntimeError("db session closed")


async def get(profile_id: str) -> Optional[dict]:
    async for s in db_session.session():
        p = await s.get(models.PlanningProfile, profile_id)
        return _to_dict(p) if p else None
    return None


async def list_profiles() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.PlanningProfile))).scalars().all()
        return [_to_dict(p) for p in rows]
    return []


async def delete(profile_id: str) -> bool:
    async for s in db_session.session():
        p = await s.get(models.PlanningProfile, profile_id)
        if p is None:
            return False
        await s.delete(p)
        await s.commit()
        return True
    return False


def _to_dict(p: models.PlanningProfile) -> dict:
    return {"profile_id": p.profile_id, "name": p.name, "algo": p.algo,
            "axes": p.axes, "vel_max": p.vel_max_json,
            "acc_max": p.acc_max_json, "created_by": p.created_by,
            "created_at": p.created_at.isoformat() if p.created_at else None}