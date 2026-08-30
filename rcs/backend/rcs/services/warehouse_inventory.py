"""Warehouse inventory domain service (WMS layer).

The 3-D geometry is already owned by the topology domain (FloorShell / SiteMap,
imported via :mod:`rcs.services.warehouse_converter`). This module owns the
*inventory* layer that sits on top of that geometry:

* storage slots (rack cells) and the SKU lines they hold,
* the AGV fleet + their planned grids,
* the logistics tasks flowing through the docks.

It knows how to **seed** a deterministic demo dataset derived from the imported
shell (so the warehouse view has something to render without a live WMS feed)
and how to **serialise** ORM rows back to the JSON contracts the frontend
``warehouse`` view already consumes (``Slot``, ``LogisticsTask``, ``AGVGrid``).
"""
from __future__ import annotations

import math
import random
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from rcs.db import models

SITE_ID = "warehouse-theatre-3d"

# Rack-style zone prototype types that hold storage slots.
_RACK_ZONE_TYPES = {
    "flow_rack", "high_rack", "bulk", "drive_in", "push_back", "pallet",
    "shelf", "bin", "asrs",
}
_UOMS = ["EA", "BOX", "PLT", "KG"]


# ── seeding ─────────────────────────────────────────────────────────────────

def _seed_slots_for_zone(zone: dict[str, Any]) -> list[dict[str, Any]]:
    """Build a grid of storage slots for a rack-type zone blueprint entry."""
    zx, zz, zw, zd = zone["x"], zone["z"], zone["w"], zone["d"]
    cols = max(2, int(round(zw / 4.0)))
    rows = max(2, int(round(zd / 3.0)))
    slots: list[dict[str, Any]] = []
    for r in range(rows):
        for c in range(cols):
            label = f"{zone['ref']}-{r+1:02d}-{c+1:02d}"
            levels = [
                {
                    "wh": SITE_ID,
                    "label": f"L{lv}",
                    "uoms": [
                        {"uom": uom, "qty": 0, "reserved": 0, "cap": cap}
                        for uom, cap in (("EA", 240), ("BOX", 24), ("PLT", 6))
                    ],
                    "items": [],
                }
                for lv in (1, 2, 3)
            ]
            slots.append(
                {
                    "group_id": zone["ref"],
                    "label": label,
                    "row": r,
                    "col": c,
                    "row_gap": 3.0,
                    "occ": 0.0,
                    "levels": levels,
                }
            )
    return slots


def _fill_demo_inventory(slot_rows: list[models.WmsSlot]) -> list[models.WmsInventoryItem]:
    """Populate a fraction of slot levels with demo SKU lines."""
    items: list[models.WmsInventoryItem] = []
    rng = random.Random(42)
    skus = [
        ("SKU-A100", "Wireless Mouse", "EA", "peripherals"),
        ("SKU-B200", "USB-C Hub", "BOX", "peripherals"),
        ("SKU-C300", "Cat6 Cable 1m", "EA", "cabling"),
        ("SKU-D400", "27\" Monitor", "PLT", "displays"),
        ("SKU-E500", "Mechanical KB", "BOX", "peripherals"),
        ("SKU-F600", "SSD 1TB", "EA", "storage"),
    ]
    for slot in slot_rows:
        if rng.random() < 0.55:  # ~55% of slots carry stock
            level = rng.choice(slot.levels)
            sku = rng.choice(skus)
            qty = rng.randint(10, int(level["uoms"][0]["cap"]))
            reserved = rng.randint(0, max(0, qty // 3))
            rate = round(rng.uniform(2.0, 40.0), 1)
            items.append(
                models.WmsInventoryItem(
                    site_id=slot.site_id,
                    slot_id=slot.id,
                    level_label=level["label"],
                    item_code=sku[0],
                    item_name=sku[1],
                    uom=sku[2],
                    group=sku[3],
                    qty=float(qty),
                    reserved=float(reserved),
                    rate=rate,
                    stock_value=round(qty * rng.uniform(1.5, 25.0), 2),
                )
            )
            slot.occ = round(min(1.0, qty / level["uoms"][0]["cap"]), 3)
    return items


def _seed_agvs() -> list[models.WmsAgv]:
    rng = random.Random(7)
    agvs: list[models.WmsAgv] = []
    for i in range(1, 5):
        status = rng.choice(["idle", "idle", "moving", "charging"])
        agvs.append(
            models.WmsAgv(
                site_id=SITE_ID,
                ref=f"AGV-{i:02d}",
                name=f"Forklift {i}",
                x=round(rng.uniform(-70, 70), 2),
                z=round(rng.uniform(-40, 40), 2),
                yaw=round(rng.uniform(-math.pi, math.pi), 3),
                battery=round(rng.uniform(0.25, 1.0), 3),
                status=status,
            )
        )
    return agvs


def _seed_tasks(docks: list[dict[str, Any]]) -> list[models.WmsLogisticsTask]:
    rng = random.Random(99)
    tasks: list[models.WmsLogisticsTask] = []
    inbound = [d["ref"] for d in docks if d.get("flow") == "inbound"] or ["DOCK-1"]
    outbound = [d["ref"] for d in docks if d.get("flow") == "outbound"] or ["DOCK-2"]
    for i in range(1, 13):
        ttype = rng.choice(["inbound", "outbound", "transfer", "replenishment"])
        status = rng.choice(["pending", "pending", "in_progress", "completed"])
        src = rng.choice(inbound) if ttype in ("inbound", "transfer") else None
        tgt = rng.choice(outbound) if ttype in ("outbound", "transfer") else None
        tasks.append(
            models.WmsLogisticsTask(
                site_id=SITE_ID,
                ref=f"LT-{i:04d}",
                type=ttype,
                status=status,
                priority=rng.randint(1, 9),
                source_dock=src,
                target_dock=tgt,
                items=[
                    {
                        "item_code": "SKU-A100",
                        "item_name": "Wireless Mouse",
                        "qty": rng.randint(5, 80),
                        "uom": "EA",
                    }
                ],
                assigned_vehicle=rng.choice(["AGV-01", "AGV-02", "AGV-03", None]),
                eta=rng.randint(60, 3600) if status != "completed" else None,
                completed_at=None if status != "completed" else 1_700_000_000,
                created_at=1_700_000_000 - i * 60,
            )
        )
    return tasks


async def seed_inventory(session: AsyncSession, shell_blueprint: dict[str, Any] | None) -> dict:
    """(Re)generate the demo inventory dataset for ``SITE_ID``.

    Slots are derived from rack-type zones in the imported shell blueprint so the
    inventory grid lines up with the 3-D geometry. Idempotent: clears existing
    rows for the site first.
    """
    zones = (shell_blueprint or {}).get("zones", [])
    docks = (shell_blueprint or {}).get("docks", [])
    rack_zones = [z for z in zones if z.get("type") in _RACK_ZONE_TYPES]

    await session.execute(delete(models.WmsInventoryItem).where(models.WmsInventoryItem.site_id == SITE_ID))
    await session.execute(delete(models.WmsSlot).where(models.WmsSlot.site_id == SITE_ID))
    await session.execute(delete(models.WmsLogisticsTask).where(models.WmsLogisticsTask.site_id == SITE_ID))
    await session.execute(delete(models.WmsAgv).where(models.WmsAgv.site_id == SITE_ID))
    await session.flush()

    slot_rows: list[models.WmsSlot] = []
    for z in rack_zones:
        for sd in _seed_slots_for_zone(z):
            slot_rows.append(
                models.WmsSlot(
                    site_id=SITE_ID,
                    group_id=sd["group_id"],
                    label=sd["label"],
                    row=sd["row"],
                    col=sd["col"],
                    row_gap=sd["row_gap"],
                    occ=sd["occ"],
                    levels=sd["levels"],
                )
            )
    session.add_all(slot_rows)
    await session.flush()  # assign ids so inventory FK resolves

    items = _fill_demo_inventory(slot_rows)
    session.add_all(items)
    session.add_all(_seed_agvs())
    session.add_all(_seed_tasks(docks))
    await session.commit()

    return {
        "site_id": SITE_ID,
        "slots": len(slot_rows),
        "items": len(items),
        "agvs": 4,
        "tasks": 12,
    }


# ── serialisation ─────────────────────────────────────────────────────────────

def slot_to_contract(slot: models.WmsSlot) -> dict[str, Any]:
    return {
        "wh": slot.site_id,
        "label": slot.label,
        "row": slot.row,
        "col": slot.col,
        "row_gap": slot.row_gap,
        "levels": slot.levels,
    }


def task_to_contract(task: models.WmsLogisticsTask) -> dict[str, Any]:
    return {
        "ref": task.ref,
        "type": task.type,
        "status": task.status,
        "priority": task.priority,
        "source_dock": task.source_dock,
        "target_dock": task.target_dock,
        "items": task.items,
        "assigned_vehicle": task.assigned_vehicle,
        "eta": task.eta,
        "completed_at": task.completed_at,
        "created_at": task.created_at,
    }


def agv_to_contract(agv: models.WmsAgv) -> dict[str, Any]:
    return {
        "ref": agv.ref,
        "name": agv.name,
        "x": agv.x,
        "z": agv.z,
        "yaw": agv.yaw,
        "battery": agv.battery,
        "status": agv.status,
        "current_task": agv.current_task,
    }


async def build_groups(session: AsyncSession) -> list[dict[str, Any]]:
    """Aggregate slots into warehouse groups (zone prototype → group)."""
    rows = await session.execute(
        select(
            models.WmsSlot.group_id,
            models.WmsSlot.site_id,
            models.WmsSlot.label,
        ).where(models.WmsSlot.site_id == SITE_ID)
    )
    counts: dict[str, int] = {}
    for group_id, _site, _label in rows.all():
        counts[group_id] = counts.get(group_id, 0) + 1
    return [
        {
            "id": gid,
            "name": gid,
            "parent_id": "",
            "parent_name": "",
            "slot_count": n,
        }
        for gid, n in sorted(counts.items())
    ]


async def inventory_stats(session: AsyncSession) -> dict[str, Any]:
    tasks = await session.execute(
        select(models.WmsLogisticsTask).where(models.WmsLogisticsTask.site_id == SITE_ID)
    )
    inbound = outbound = 0
    for t in tasks.scalars().all():
        if t.type == "inbound":
            inbound += 1
        elif t.type == "outbound":
            outbound += 1
    slots = await session.execute(
        select(models.WmsSlot.occ).where(models.WmsSlot.site_id == SITE_ID)
    )
    occs = [o for (o,) in slots.all()]
    avg_occ = round(sum(occs) / len(occs), 3) if occs else 0.0
    return {
        "total_inbound": inbound,
        "total_outbound": outbound,
        "avg_processing_time": 0,
        "dock_utilization": avg_occ,
    }
