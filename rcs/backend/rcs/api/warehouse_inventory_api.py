"""REST endpoints for the warehouse inventory domain (WMS layer).

These endpoints own the *inventory* layer that sits on top of the 3-D geometry
already imported into the topology domain:

* ``/api/rcs/warehouse/inventory/slots``      — storage slots (rack cells)
* ``/api/rcs/warehouse/inventory/items``       — SKU lines held in slots
* ``/api/rcs/warehouse/inventory/agv``         — AGV fleet
* ``/api/rcs/warehouse/inventory/tasks``        — logistics tasks
* ``/api/rcs/warehouse/inventory/stats``        — aggregate dashboard stats
* ``/api/rcs/warehouse/inventory/groups``       — slot groups (zone prototype)
* ``POST /api/rcs/warehouse/inventory/seed``    — (re)generate demo dataset

The frontend ``warehouse`` view consumes these to flip its data-source badge to
``RCS`` (green), completing the layered fusion of geometry (topology domain) and
inventory (this domain).
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from rcs.db import models, session as db_session
from rcs.services import warehouse_inventory as inv
from rcs.services.warehouse_converter import BLUEPRINT

router = APIRouter(prefix="/warehouse/inventory", tags=["warehouse-inventory"])


@router.get("/groups")
async def get_groups() -> dict:
    async for s in db_session.session():
        groups = await inv.build_groups(s)
        return {"groups": groups}
    raise HTTPException(503, "db unavailable")


@router.get("/slots")
async def get_slots(group_id: str | None = Query(default=None)) -> dict:
    async for s in db_session.session():
        q = select(models.WmsSlot).where(models.WmsSlot.site_id == inv.SITE_ID)
        if group_id:
            q = q.where(models.WmsSlot.group_id == group_id)
        q = q.order_by(models.WmsSlot.row, models.WmsSlot.col)
        rows = (await s.execute(q)).scalars().all()
        return {"slots": [inv.slot_to_contract(sl) for sl in rows]}
    raise HTTPException(503, "db unavailable")


@router.get("/items")
async def get_items(slot_id: int | None = Query(default=None)) -> dict:
    async for s in db_session.session():
        q = select(models.WmsInventoryItem).where(
            models.WmsInventoryItem.site_id == inv.SITE_ID
        )
        if slot_id is not None:
            q = q.where(models.WmsInventoryItem.slot_id == slot_id)
        rows = (await s.execute(q)).scalars().all()
        return {
            "items": [
                {
                    "slot_id": it.slot_id,
                    "level_label": it.level_label,
                    "item_code": it.item_code,
                    "item_name": it.item_name,
                    "uom": it.uom,
                    "group": it.group,
                    "qty": it.qty,
                    "reserved": it.reserved,
                    "rate": it.rate,
                    "stock_value": it.stock_value,
                }
                for it in rows
            ]
        }
    raise HTTPException(503, "db unavailable")


@router.get("/agv")
async def get_agvs() -> dict:
    async for s in db_session.session():
        rows = (
            await s.execute(
                select(models.WmsAgv).where(models.WmsAgv.site_id == inv.SITE_ID)
            )
        ).scalars().all()
        return {"agvs": [inv.agv_to_contract(a) for a in rows]}
    raise HTTPException(503, "db unavailable")


@router.get("/tasks")
async def get_tasks(
    status: str | None = Query(default=None),
    type_: str | None = Query(default=None, alias="type"),
) -> dict:
    async for s in db_session.session():
        q = select(models.WmsLogisticsTask).where(
            models.WmsLogisticsTask.site_id == inv.SITE_ID
        )
        if status:
            q = q.where(models.WmsLogisticsTask.status == status)
        if type_:
            q = q.where(models.WmsLogisticsTask.type == type_)
        q = q.order_by(models.WmsLogisticsTask.priority, models.WmsLogisticsTask.created_at)
        rows = (await s.execute(q)).scalars().all()
        return {"tasks": [inv.task_to_contract(t) for t in rows]}
    raise HTTPException(503, "db unavailable")


@router.get("/stats")
async def get_stats() -> dict:
    async for s in db_session.session():
        stats = await inv.inventory_stats(s)
        return {"stats": stats}
    raise HTTPException(503, "db unavailable")


@router.post("/seed")
async def seed() -> dict:
    """(Re)generate the demo inventory dataset derived from the imported shell."""
    async for s in db_session.session():
        result = await inv.seed_inventory(s, BLUEPRINT)
        return {"ok": True, **result}
    raise HTTPException(503, "db unavailable")
