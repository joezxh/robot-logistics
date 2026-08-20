"""AGV navigation grid models."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel


CellType = Literal[0, 1, 2, 3]


class AGVCell(BaseModel):
    t: CellType
    w: float


class AGVNode(BaseModel):
    x: int
    z: int
    g: float = 0
    h: float = 0
    f: float = 0
    parent: AGVNode | None = None


class AGVGrid(BaseModel):
    cols: int
    rows: int
    cell_size: float = 1.0
    cells: list[AGVCell] = []


class AisleGap(BaseModel):
    index: int
    label: str
    z_center: float
    width: float


class AGVPath(BaseModel):
    task_id: str
    points: list[tuple[float, float, float]]
    vehicle_ref: str
    status: Literal["planned", "active", "completed"] = "planned"


class AGVTool(BaseModel):
    type: Literal["block", "walk", "main", "restricted"]
    label: str
    color: str


AGV_WEIGHTS = {0: 999, 1: 1, 2: 1, 3: 5}
