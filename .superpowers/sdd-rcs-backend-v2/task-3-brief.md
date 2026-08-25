## Task 3: Pydantic 模型 — SiteGrid

**Files:**
- Create: `rcs/backend/rcs_backend/models/site_grid.py`
- Create: `rcs/backend/tests/unit/test_site_grid_model.py`

**Interfaces:**
- Produces:
  - `enum CellType(str, Enum)`: empty, blocked, agv_lane, agv_node, robot_lane, robot_node, charger, dock, shelf, work_zone
  - `class Cell(BaseModel)`: x, z, type=CellType.EMPTY, height=0.0, metadata={}
  - `class SiteGrid(BaseModel)`: site_id, bounds{w,d,h?}, resolution=0.5, cells (2D list[list[Cell]])

- [ ] **Step 0: 在 `rcs_backend/models/__init__.py` 追加 SiteGrid re-export**

```python
# Edit rcs/backend/rcs_backend/models/__init__.py
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType

# Append to __all__:
__all__ = [
    "WallSegment", "Zone", "Facility", "Dock", "Corridor", "Marking", "FloorShell", "Floor",
    "SiteGrid", "Cell", "CellType",
]
```

- [ ] **Step 1: 写失败的测试**

```python
"""Pydantic models for site grid (resolution-N raster of CellType)."""
import pytest
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType


def test_cell_type_enum_all_members():
    """All 10 v2.2 cell types must exist (spec §13.3.3)."""
    assert CellType.EMPTY == "empty"
    assert CellType.BLOCKED == "blocked"
    assert CellType.AGV_LANE == "agv_lane"
    assert CellType.AGV_NODE == "agv_node"
    assert CellType.ROBOT_LANE == "robot_lane"
    assert CellType.ROBOT_NODE == "robot_node"
    assert CellType.CHARGER == "charger"
    assert CellType.DOCK == "dock"
    assert CellType.SHELF == "shelf"
    assert CellType.WORK_ZONE == "work_zone"


def test_cell_default_empty():
    c = Cell(x=0, z=0)
    assert c.type == CellType.EMPTY
    assert c.height == 0.0
    assert c.metadata == {}


def test_site_grid_minimal_default_resolution():
    grid = SiteGrid(site_id="site-A", bounds={"w": 10.0, "d": 8.0})
    assert grid.resolution == 0.5
    # 10 / 0.5 = 20 cells x, 8 / 0.5 = 16 cells z
    assert len(grid.cells) == 16
    assert len(grid.cells[0]) == 20


def test_site_grid_custom_resolution():
    grid = SiteGrid(site_id="site-A", bounds={"w": 10.0, "d": 10.0}, resolution=1.0)
    assert len(grid.cells) == 10
    assert len(grid.cells[0]) == 10


def test_site_grid_2d_indexing():
    """cells[z][x] returns the cell at (x, z)."""
    grid = SiteGrid(site_id="site-A", bounds={"w": 2.0, "d": 2.0}, resolution=1.0)
    grid.cells[0][0].type = CellType.AGV_LANE
    assert grid.cells[0][0].type == CellType.AGV_LANE
    # bounds-check
    with pytest.raises(IndexError):
        _ = grid.cells[10][10]


def test_site_grid_serializes_to_dict():
    grid = SiteGrid(site_id="site-A", bounds={"w": 4.0, "d": 4.0}, resolution=1.0)
    d = grid.model_dump()
    assert d["site_id"] == "site-A"
    assert d["resolution"] == 1.0
    assert d["bounds"]["w"] == 4.0
    assert len(d["cells"]) == 4
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_site_grid_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rcs_backend.models.site_grid'`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/models/site_grid.py`**

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_site_grid_model.py -v`
Expected: PASS（6 tests）

- [ ] **Step 5: 跑全 suite 确认无回归**

Run: `cd rcs/backend && pytest -v`
Expected: 5 (Task 2) + 6 (Task 3) = 11 passed, no regressions

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/models/site_grid.py \
        rcs/backend/rcs_backend/models/__init__.py \
        rcs/backend/tests/unit/test_site_grid_model.py
git commit -m "feat(rcs-backend): SiteGrid raster model with 10 cell types (v2.2 spec §13.3.3)"
```