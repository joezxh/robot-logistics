"""Device registry persistence + seeding (PostgreSQL).

Algorithm file ``rcs.control.registry`` keeps its in-memory defaults; this
service mirrors those defaults into the DB on first boot and provides
CRUD APIs used by REST + seed workflows.
"""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from rcs.db import models, session as db_session


async def register(
    device_id: str, morphology: str, num_joints: int, control_hz: int,
    limits: dict, home_joints: list, spec: dict, status: str = "registered",
) -> dict:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        if dev is None:
            dev = models.Device(device_id=device_id)
        dev.morphology = morphology
        dev.num_joints = num_joints
        dev.control_hz = control_hz
        dev.limits_json = limits or {}
        dev.home_joints_json = home_joints or []
        dev.spec_json = spec or {}
        dev.status = status
        s.add(dev)
        await s.commit()
        await s.refresh(dev)
        return _to_dict(dev)
    raise RuntimeError("db session closed unexpectedly")


async def get(device_id: str) -> Optional[dict]:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        return _to_dict(dev) if dev else None
    return None


async def list_devices() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.Device))).scalars().all()
        return [_to_dict(d) for d in rows]
    return []


async def update(device_id: str, **fields) -> Optional[dict]:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        if dev is None:
            return None
        for k, v in fields.items():
            if hasattr(dev, k):
                setattr(dev, k, v)
        await s.commit()
        await s.refresh(dev)
        return _to_dict(dev)
    return None


async def delete(device_id: str) -> bool:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        if dev is None:
            return False
        await s.delete(dev)
        await s.commit()
        return True
    return False


def _to_dict(d: models.Device) -> dict:
    return {
        "device_id": d.device_id,
        "morphology": d.morphology,
        "robot_type": d.robot_type,
        "num_joints": d.num_joints,
        "control_hz": d.control_hz,
        "mode": d.mode,
        "limits": d.limits_json or {},
        "home_joints": d.home_joints_json or [],
        "spec": d.spec_json or {},
        "status": d.status,
        "locked": d.locked,
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


async def seed_defaults_if_empty() -> None:
    """Seed devices from ``rcs.control.registry._DEFAULT_PROFILES`` when empty."""
    async for s in db_session.session():
        if (await s.execute(select(models.Device))).scalars().first() is not None:
            return
    # lazy import to avoid cycle
    try:
        from rcs.control.registry import _DEFAULT_PROFILES  # type: ignore
    except Exception:
        return
    for p in _DEFAULT_PROFILES:
        await register(
            device_id=p.device_id,
            morphology=getattr(p.morphology, "value", str(p.morphology)),
            num_joints=p.num_joints,
            control_hz=p.control_hz,
            limits={
                "pos_lower": list(p.limits.pos_lower),
                "pos_upper": list(p.limits.pos_upper),
                "vel_max": list(p.limits.vel_max),
                "acc_max": list(p.limits.acc_max),
            },
            home_joints=list(p.home_joints),
            spec={},
        )