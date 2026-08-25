"""Unified command + event log service."""
from __future__ import annotations
from typing import Optional

from sqlalchemy import select

from rcs.db import models, session as db_session


async def issue_command(device_id: str, cmd_type: str, payload: dict,
                        issued_by: Optional[str] = None,
                        result: str = "ok") -> dict:
    async for s in db_session.session():
        c = models.CommandLog(device_id=device_id, cmd_type=cmd_type,
                              payload_json=payload or {}, issued_by=issued_by,
                              result=result)
        s.add(c)
        await s.commit()
        await s.refresh(c)
        return _cmd_to_dict(c)
    raise RuntimeError("db session closed")


async def list_commands(device_id: Optional[str] = None, limit: int = 100) -> list[dict]:
    async for s in db_session.session():
        stmt = (select(models.CommandLog)
                .order_by(models.CommandLog.created_at.desc()).limit(limit))
        if device_id:
            stmt = stmt.where(models.CommandLog.device_id == device_id)
        rows = (await s.execute(stmt)).scalars().all()
        return [_cmd_to_dict(c) for c in rows]
    return []


async def log_event(level: str, source: str, message: str,
                    meta: Optional[dict] = None) -> dict:
    async for s in db_session.session():
        e = models.EventLog(level=level, source=source, message=message,
                            meta_json=meta or {})
        s.add(e)
        await s.commit()
        await s.refresh(e)
        return _ev_to_dict(e)
    raise RuntimeError("db session closed")


async def list_events(level: Optional[str] = None, limit: int = 100) -> list[dict]:
    async for s in db_session.session():
        stmt = (select(models.EventLog)
                .order_by(models.EventLog.created_at.desc()).limit(limit))
        if level:
            stmt = stmt.where(models.EventLog.level == level)
        rows = (await s.execute(stmt)).scalars().all()
        return [_ev_to_dict(e) for e in rows]
    return []


def _cmd_to_dict(c: models.CommandLog) -> dict:
    return {"cmd_id": c.cmd_id, "device_id": c.device_id,
            "cmd_type": c.cmd_type, "payload": c.payload_json,
            "issued_by": c.issued_by, "result": c.result,
            "created_at": c.created_at.isoformat() if c.created_at else None}


def _ev_to_dict(e: models.EventLog) -> dict:
    return {"event_id": e.event_id, "level": e.level, "source": e.source,
            "message": e.message, "meta": e.meta_json,
            "created_at": e.created_at.isoformat() if e.created_at else None}