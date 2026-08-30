"""Scheduler configuration persistence (weights/strategy), single active."""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from rcs.db import models, session as db_session


async def create(name: str, strategy: str = "util-weighted",
                 weights: Optional[dict] = None) -> dict:
    async for s in db_session.session():
        c = models.SchedulerConfig(name=name, strategy=strategy,
                                   weights_json=weights or {})
        s.add(c)
        await s.commit()
        await s.refresh(c)
        return _to_dict(c)
    raise RuntimeError("db session closed")


async def get(config_id: str) -> Optional[dict]:
    async for s in db_session.session():
        c = await s.get(models.SchedulerConfig, config_id)
        return _to_dict(c) if c else None
    return None


async def list_configs() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.SchedulerConfig))).scalars().all()
        return [_to_dict(c) for c in rows]
    return []


async def update(config_id: str, **fields) -> Optional[dict]:
    async for s in db_session.session():
        c = await s.get(models.SchedulerConfig, config_id)
        if c is None:
            return None
        # API/tests pass "weights"; the ORM column is weights_json.
        if "weights" in fields:
            fields["weights_json"] = fields.pop("weights")
        for k, v in fields.items():
            if hasattr(c, k):
                setattr(c, k, v)
        await s.commit()
        await s.refresh(c)
        return _to_dict(c)
    return None


async def activate(config_id: str) -> bool:
    async for s in db_session.session():
        rows = (await s.execute(select(models.SchedulerConfig))).scalars().all()
        if not any(c.config_id == config_id for c in rows):
            return False
        for c in rows:
            c.active = (c.config_id == config_id)
        await s.commit()
        return True
    return False


async def get_active() -> Optional[dict]:
    async for s in db_session.session():
        rows = (await s.execute(
            select(models.SchedulerConfig).where(models.SchedulerConfig.active == True)  # noqa: E712
        )).scalars().all()
        return _to_dict(rows[0]) if rows else None
    return None


def _to_dict(c: models.SchedulerConfig) -> dict:
    return {"config_id": c.config_id, "name": c.name, "strategy": c.strategy,
            "weights": c.weights_json, "active": c.active,
            "created_at": c.created_at.isoformat() if c.created_at else None}