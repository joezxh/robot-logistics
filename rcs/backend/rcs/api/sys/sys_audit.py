"""Audit log endpoints (``/api/sys/audit-logs``).

The log is written by :class:`~rcs.sysadmin.audit.AuditRoute` for every
``/api/sys/**`` request; this router only provides the read side plus a
maintenance purge.
"""
from __future__ import annotations
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.services.sys.sys_deps import get_current_admin, get_db, require_permissions
from rcs.db.sys_models import SysAuditLog
from rcs.services.sys.sys_schemas import AuditLogRow, Envelope
from rcs.services.sys.sys_service import list_audit_logs

router = APIRouter(prefix="/audit-logs", tags=["sys-audit"])


def _parse_dt(value: str | None) -> dt.datetime | None:
    """Parse an ISO-8601 query parameter; ``None`` when absent or malformed."""
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"时间格式无效: {value}（应为 ISO-8601，如 2026-08-30T00:00:00）",
        ) from exc


@router.get("", response_model=Envelope[list[AuditLogRow]])
async def get_audit_logs(
    user_id: int | None = Query(None),
    username: str | None = Query(None),
    operation_type: str | None = Query(None, description="create/update/delete/query/login/logout"),
    operation_module: str | None = Query(None),
    keyword: str | None = Query(None, description="描述/URL/IP 模糊匹配"),
    start_at: str | None = Query(None, description="起始时间 ISO-8601"),
    end_at: str | None = Query(None, description="结束时间 ISO-8601"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[list[AuditLogRow]]:
    """Filtered, newest-first audit page."""
    rows, total = await list_audit_logs(
        db,
        user_id=user_id,
        username=username,
        operation_type=operation_type,
        operation_module=operation_module,
        keyword=keyword,
        start_at=_parse_dt(start_at),
        end_at=_parse_dt(end_at),
        skip=skip,
        limit=limit,
    )
    return Envelope(data=rows, total=total)


@router.get("/stats")
async def get_audit_stats(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[dict]:
    """Aggregate counts grouped by operation type (dashboard widget)."""
    rows = (
        await db.execute(
            select(SysAuditLog.operation_type, func.count())
            .group_by(SysAuditLog.operation_type)
            .order_by(func.count().desc())
        )
    ).all()
    total = (
        await db.execute(select(func.count()).select_from(SysAuditLog))
    ).scalar_one()
    return Envelope(data={"total": int(total), "byType": {r[0]: int(r[1]) for r in rows}})


@router.delete(
    "",
    dependencies=[Depends(require_permissions("sys:audit:delete"))],
)
async def purge_audit_logs(
    before: str | None = Query(None, description="删除该时间点之前的日志（缺省=清空）"),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_current_admin),
) -> Envelope[dict]:
    """Delete audit rows older than ``before``, or all of them when omitted."""
    cutoff = _parse_dt(before)
    stmt = delete(SysAuditLog)
    if cutoff is not None:
        stmt = stmt.where(SysAuditLog.created_at < cutoff)
    result = await db.execute(stmt)
    await db.commit()
    return Envelope(message="清理成功", data={"deleted": int(result.rowcount or 0)})
