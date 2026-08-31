"""Console dashboard summary (``/api/sys/dashboard``).

A handful of cheap counts so the console landing page has something to show
without inventing a metrics subsystem.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.services.sys.sys_deps import get_current_user, get_db
from rcs.db.sys_models import (
    SysAuditLog,
    SysDictionary,
    SysMenu,
    SysRole,
    SysUser,
)
from rcs.db.models import Device, Order
from rcs.db.unified_map import UnifiedMap
from rcs.services.sys.sys_schemas import Envelope

router = APIRouter(prefix="/dashboard", tags=["sys-dashboard"])


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Envelope[dict]:
    """Counts for the dashboard cards plus the caller's recent activity."""
    users = (
        await db.execute(select(func.count()).select_from(SysUser).where(SysUser.is_deleted.is_(False)))
    ).scalar_one()
    roles = (
        await db.execute(select(func.count()).select_from(SysRole).where(SysRole.is_deleted.is_(False)))
    ).scalar_one()
    menus = (
        await db.execute(select(func.count()).select_from(SysMenu).where(SysMenu.is_deleted.is_(False)))
    ).scalar_one()
    dicts = (
        await db.execute(
            select(func.count()).select_from(SysDictionary).where(SysDictionary.is_deleted.is_(False))
        )
    ).scalar_one()
    online = (
        await db.execute(
            select(func.count())
            .select_from(SysUser)
            .where(SysUser.is_deleted.is_(False), SysUser.status == "active")
        )
    ).scalar_one()
    devices = (await db.execute(select(func.count()).select_from(Device))).scalar_one()
    orders = (await db.execute(select(func.count()).select_from(Order))).scalar_one()
    # UnifiedMap holds both real records and templates in one table. Templates
    # are filtered via ``is_template.is_(False)`` so the counters do not silently
    # inflate by the template count; the warehouse counter additionally filters
    # ``kind == 'warehouse'``.
    maps = (
        await db.execute(
            select(func.count())
            .select_from(UnifiedMap)
            .where(UnifiedMap.is_template.is_(False))
        )
    ).scalar_one()
    warehouses = (
        await db.execute(
            select(func.count())
            .select_from(UnifiedMap)
            .where(UnifiedMap.is_template.is_(False), UnifiedMap.kind == "warehouse")
        )
    ).scalar_one()

    recent = (
        (
            await db.execute(
                select(SysAuditLog)
                .where(SysAuditLog.user_id == current_user.user_id)
                .order_by(SysAuditLog.created_at.desc(), SysAuditLog.log_id.desc())
                .limit(8)
            )
        )
        .scalars()
        .all()
    )

    return Envelope(
        data={
            "userCount": int(users),
            "roleCount": int(roles),
            "menuCount": int(menus),
            "dictCount": int(dicts),
            "activeUserCount": int(online),
            "deviceCount": int(devices),
            "orderCount": int(orders),
            "mapCount": int(maps),
            "warehouseCount": int(warehouses),
            "recentOperations": [
                {
                    "logId": log.log_id,
                    "operationType": log.operation_type,
                    "operationModule": log.operation_module,
                    "operationDesc": log.operation_desc,
                    "responseStatus": log.response_status,
                    "createdAt": log.created_at.isoformat() if log.created_at else None,
                }
                for log in recent
            ],
        }
    )
