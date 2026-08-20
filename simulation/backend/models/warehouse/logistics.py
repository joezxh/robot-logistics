"""Logistics and task models."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel


TaskType = Literal["inbound", "outbound", "transfer", "replenishment"]
TaskStatus = Literal["pending", "in_progress", "completed", "cancelled"]


class TaskItem(BaseModel):
    item_code: str
    item_name: str
    qty: float
    uom: str = "PCS"


class LogisticsTask(BaseModel):
    ref: str
    type: TaskType
    status: TaskStatus
    priority: int = 3
    source_dock: str | None = None
    target_dock: str | None = None
    items: list[TaskItem] = []
    assigned_vehicle: str | None = None
    eta: float | None = None
    completed_at: float | None = None
    created_at: float


class LogisticsStats(BaseModel):
    total_inbound: int = 0
    total_outbound: int = 0
    avg_processing_time: float = 0
    dock_utilization: float = 0


class DockDetail(BaseModel):
    ref: str
    direction: Literal["inbound", "outbound"]
    name: str
    x: float
    z: float
    slots: list[DockSlot]
    utilization: float = 0


class DockSlot(BaseModel):
    ref: str
    status: Literal["available", "occupied", "scheduled"] = "available"
    task: str | None = None
    vehicle: str | None = None


class FloorFull(BaseModel):
    shell: ShellBlueprint | None = None
    zones: list[Zone] = []
    facilities: list[Facility] = []
    docks: list[Dock] = []


# Forward references for FloorFull
from backend.models.warehouse.zone import (
    ShellBlueprint,
    Zone,
    Facility,
    Dock,
)
