"""Warehouse API router for 3D visualization."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.warehouse import (
    Slot,
    WarehouseGroup,
    WarehouseDetail,
    FloorFull,
    LogisticsTask,
    LogisticsStats,
    AGVGrid,
    ShellBlueprint,
    Zone,
    Facility,
    Dock,
)

router = APIRouter(prefix="/api/warehouse", tags=["warehouse"])

# Demo data directory
DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "warehouse"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_json(name: str, default: Any = None) -> Any:
    """Load JSON data from demo directory."""
    path = DATA_DIR / f"{name}.json"
    if path.exists():
        return json.loads(path.read_text())
    return default


def _save_json(name: str, data: Any) -> None:
    """Save JSON data to demo directory."""
    path = DATA_DIR / f"{name}.json"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


# ─────────────────────────────────────────────────────────────
# Response Models
# ─────────────────────────────────────────────────────────────


class GroupsResponse(BaseModel):
    groups: list[dict]


class SlotsResponse(BaseModel):
    slots: list[dict]


class FloorFullResponse(BaseModel):
    floor_full: FloorFull | None


class LogisticsStatsResponse(BaseModel):
    stats: LogisticsStats


class LogisticsTasksResponse(BaseModel):
    tasks: list[LogisticsTask]


class AGVGridResponse(BaseModel):
    grid: AGVGrid


class ShellSaveRequest(BaseModel):
    group_id: str
    shell: ShellBlueprint


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────


@router.get("/groups", response_model=GroupsResponse)
async def get_groups() -> GroupsResponse:
    """Get all warehouse groups."""
    groups = _load_json("groups", [])
    return GroupsResponse(groups=groups)


@router.get("/groups/{group_id}", response_model=dict)
async def get_group(group_id: str) -> dict:
    """Get a specific warehouse group."""
    groups = _load_json("groups", [])
    for g in groups:
        if g.get("id") == group_id:
            return g
    raise HTTPException(status_code=404, detail=f"Group {group_id} not found")


@router.get("/slots", response_model=SlotsResponse)
async def get_slots(group_id: str | None = None) -> SlotsResponse:
    """Get warehouse slots, optionally filtered by group."""
    slots = _load_json("slots", [])
    if group_id:
        slots = [s for s in slots if s.get("group_id") == group_id]
    return SlotsResponse(slots=slots)


@router.get("/slots/{slot_id}", response_model=dict)
async def get_slot(slot_id: str) -> dict:
    """Get a specific slot with levels."""
    slots = _load_json("slots", [])
    for s in slots:
        if s.get("wh") == slot_id:
            return s
    raise HTTPException(status_code=404, detail=f"Slot {slot_id} not found")


@router.get("/floor", response_model=FloorFullResponse)
async def get_floor_full(group_id: str) -> FloorFullResponse:
    """Get full floor layout including shell, zones, facilities, docks."""
    floor = _load_json(f"floor_{group_id}", None)
    if floor:
        return FloorFullResponse(floor_full=FloorFull(**floor))
    return FloorFullResponse(floor_full=None)


@router.get("/logistics/stats", response_model=LogisticsStatsResponse)
async def get_logistics_stats() -> LogisticsStatsResponse:
    """Get logistics statistics."""
    stats = _load_json("logistics_stats", {
        "total_inbound": 0,
        "total_outbound": 0,
        "avg_processing_time": 0,
        "dock_utilization": 0,
    })
    return LogisticsStatsResponse(stats=LogisticsStats(**stats))


@router.get("/logistics/tasks", response_model=LogisticsTasksResponse)
async def get_logistics_tasks() -> LogisticsTasksResponse:
    """Get logistics tasks."""
    tasks = _load_json("logistics_tasks", [])
    return LogisticsTasksResponse(tasks=[LogisticsTask(**t) for t in tasks])


@router.get("/agv/grid", response_model=AGVGridResponse)
async def get_agv_grid(group_id: str | None = None) -> AGVGridResponse:
    """Get AGV navigation grid."""
    grid = _load_json("agv_grid", {
        "cols": 40,
        "rows": 30,
        "cell_size": 1.0,
        "cells": [{"t": 1, "w": 1} for _ in range(40 * 30)],
    })
    return AGVGridResponse(grid=AGVGrid(**grid))


@router.post("/agv/grid")
async def save_agv_grid(grid: AGVGrid, group_id: str) -> dict:
    """Save AGV navigation grid."""
    _save_json(f"agv_grid_{group_id}", grid.model_dump())
    return {"status": "ok"}


@router.post("/floor/shell")
async def save_floor_shell(req: ShellSaveRequest) -> dict:
    """Save floor plan shell blueprint."""
    _save_json(f"floor_{req.group_id}", {"shell": req.shell.model_dump()})
    return {"status": "ok"}


@router.get("/warehouses", response_model=list[dict])
async def get_warehouses() -> list[dict]:
    """Get all warehouse details (for manage modal)."""
    return _load_json("warehouses", [])


@router.post("/warehouses")
async def create_warehouse(data: WarehouseDetail) -> dict:
    """Create a new warehouse."""
    warehouses = _load_json("warehouses", [])
    warehouses.append(data.model_dump())
    _save_json("warehouses", warehouses)
    return {"name": data.name}


@router.put("/warehouses/{name}")
async def update_warehouse(name: str, data: WarehouseDetail) -> dict:
    """Update a warehouse."""
    warehouses = _load_json("warehouses", [])
    for i, w in enumerate(warehouses):
        if w.get("name") == name:
            warehouses[i] = data.model_dump()
            _save_json("warehouses", warehouses)
            return {"name": name}
    raise HTTPException(status_code=404, detail=f"Warehouse {name} not found")


@router.delete("/warehouses/{name}")
async def delete_warehouse(name: str) -> dict:
    """Delete a warehouse."""
    warehouses = _load_json("warehouses", [])
    warehouses = [w for w in warehouses if w.get("name") != name]
    _save_json("warehouses", warehouses)
    return {"status": "deleted"}


# ─────────────────────────────────────────────────────────────
# Demo Data Generation
# ─────────────────────────────────────────────────────────────


@router.post("/demo/generate")
async def generate_demo_data() -> dict:
    """Generate demo warehouse data."""
    # Generate demo groups
    groups = [
        {"id": "demo-001", "name": "Demo Warehouse A", "parent_id": "", "parent_name": "", "slot_count": 8},
        {"id": "demo-002", "name": "Demo Warehouse B", "parent_id": "", "parent_name": "", "slot_count": 6},
    ]
    _save_json("groups", groups)

    # Generate demo slots
    slots = []
    for gi, g in enumerate(groups):
        for i in range(g["slot_count"]):
            row = i // 4
            col = i % 4
            wh = f"WH-{g['id']}-{i:02d}"
            slot = {
                "wh": wh,
                "label": f"Slot {chr(65 + row)}{i + 1}",
                "row": row,
                "col": col,
                "row_gap": 0.5 if i % 3 == 0 else 0,
                "levels": [
                    {
                        "wh": f"{wh}/LV{j}",
                        "label": f"Level {j}",
                        "uoms": [
                            {"uom": "PCS", "qty": 50 if j == 1 else 0, "reserved": 5, "cap": 100},
                        ],
                        "items": [],
                    }
                    for j in range(1, 5)
                ],
            }
            slots.append(slot)
    _save_json("slots", slots)

    # Generate demo shell
    shell = {
        "bounds": {"w": 40, "d": 30},
        "walls": [
            {"x0": -20, "z0": -15, "x1": 20, "z1": -15, "h": 3},
            {"x0": -20, "z0": 15, "x1": 20, "z1": 15, "h": 3},
            {"x0": -20, "z0": -15, "x1": -20, "z1": 15, "h": 3},
            {"x0": 20, "z0": -15, "x1": 20, "z1": 15, "h": 3},
        ],
        "docks": [
            {"ref": "DOCK-1", "x": -15, "z": 15, "w": 4, "d": 3, "direction": "inbound"},
            {"ref": "DOCK-2", "x": 0, "z": 15, "w": 4, "d": 3, "direction": "inbound"},
            {"ref": "DOCK-3", "x": 15, "z": 15, "w": 4, "d": 3, "direction": "outbound"},
        ],
        "facilities": [
            {"ref": "CHG-1", "kind": "charger", "x": -15, "z": -10, "w": 2, "d": 2},
            {"ref": "QC-1", "kind": "qc", "x": 15, "z": -10, "w": 3, "d": 2},
        ],
        "corridors": [
            {"x0": -20, "z0": 0, "x1": 20, "z1": 0, "main": True},
        ],
    }
    _save_json(f"floor_{groups[0]['id']}", {
        "shell": shell,
        "zones": [
            {"ref": "ZONE-A", "type": "rack", "name": "Rack Zone A", "x": -8, "z": -8, "w": 15, "d": 12},
            {"ref": "ZONE-B", "type": "rack", "name": "Rack Zone B", "x": 8, "z": -8, "w": 10, "d": 12},
        ],
        "facilities": [],
        "docks": [],
    })

    # Generate demo AGV grid
    cells = []
    for _ in range(40 * 30):
        cells.append({"t": 1, "w": 1})
    _save_json("agv_grid", {"cols": 40, "rows": 30, "cell_size": 1.0, "cells": cells})

    return {"status": "generated", "groups": len(groups), "slots": len(slots)}
