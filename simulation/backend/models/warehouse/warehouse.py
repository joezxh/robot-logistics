"""Warehouse domain models."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class UOMCapacity(BaseModel):
    uom: str
    qty: float = 0
    reserved: float = 0
    cap: float = 0


class ItemStock(BaseModel):
    c: str = Field(alias="code")
    n: str = Field(alias="name")
    u: str = Field(alias="uom")
    g: str = Field(alias="group")
    qty: float = 0
    reserved: float = 0
    rate: float = 0
    stock_value: float = 0

    class Config:
        populate_by_name = True


class SlotLevel(BaseModel):
    wh: str
    label: str
    uoms: list[UOMCapacity] = []
    items: list[ItemStock] = []


class Slot(BaseModel):
    wh: str
    label: str
    row: int = 0
    col: int = 0
    row_gap: float = 0
    levels: list[SlotLevel] = []


class WarehouseGroup(BaseModel):
    id: str
    name: str
    parent_id: str
    parent_name: str
    slot_count: int = 0


class WarehouseDetail(BaseModel):
    name: str
    warehouse_name: str
    company: str = ""
    wt_warehouse_type: Literal[
        "Building", "Floor", "Slot", "Bin", "Dock",
        "Zone", "Aisle", "Cell", "Bulk", "Facility"
    ] = "Slot"
    parent_warehouse: str = ""
    is_group: bool = False
    disabled: bool = False
    wt_row: int = 0
    wt_col: int = 0
    wt_row_gap: float = 0
    uom_capacities: list[UOMCapacity] = []


ViewMode = Literal["3d", "2d", "editor"]
Language = Literal["zh", "en"]
Theme = Literal["dark", "light"]
