"""SiteGrid raster model — N×M grid of Cell entries (v2.2 spec §13.3.3)."""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field, conlist


class CellType(str, Enum):
    EMPTY = "empty"
    BLOCKED = "blocked"
    AGV_LANE = "agv_lane"
    AGV_NODE = "agv_node"
    ROBOT_LANE = "robot_lane"
    ROBOT_NODE = "robot_node"
    CHARGER = "charger"
    DOCK = "dock"
    SHELF = "shelf"
    WORK_ZONE = "work_zone"


class Bounds(BaseModel):
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    h: float = Field(default=0, ge=0)


class Cell(BaseModel):
    x: int = Field(ge=0)
    z: int = Field(ge=0)
    type: CellType = CellType.EMPTY
    height: float = Field(default=0.0, ge=0)
    metadata: dict = Field(default_factory=dict)


class SiteGrid(BaseModel):
    site_id: str
    bounds: Bounds
    resolution: float = Field(default=0.5, gt=0)
    cells: list[list[Cell]] = Field(default_factory=list)

    def __init__(self, **data):
        super().__init__(**data)
        if not self.cells:
            # Auto-generate empty grid from bounds + resolution
            self._auto_populate()

    def _auto_populate(self) -> None:
        nx = max(1, int(self.bounds.w / self.resolution))
        nz = max(1, int(self.bounds.d / self.resolution))
        self.cells = [
            [Cell(x=x, z=z) for x in range(nx)]
            for z in range(nz)
        ]

    def cell_at(self, x: int, z: int) -> Cell:
        return self.cells[z][x]

    def set_cell_type(self, x: int, z: int, cell_type: CellType) -> None:
        self.cells[z][x].type = cell_type
