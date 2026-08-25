## Task 2: Pydantic 模型 — FloorShell

**Files:**
- Create: `rcs/backend/rcs_backend/models/__init__.py`
- Create: `rcs/backend/rcs_backend/models/floor_shell.py`
- Create: `rcs/backend/tests/unit/test_floor_shell_model.py`

**Interfaces:**
- Produces:
  - `class WallSegment(BaseModel)`: id, x0, z0, x1, z1, h=3.5, kind="wall"
  - `class Zone(BaseModel)`: id, ref, type, x, z, w, d, siteNodeIds=[], temperature_range?, batch_tracking?, hazard_level?, customs_regulated?, current_load_pct=0.0
  - `class Facility(BaseModel)`: id, ref, type, x, z, w, d, h=2.5
  - `class Dock(BaseModel)`: id, ref, x, z, dir="N", door_w=4.0
  - `class Corridor(BaseModel)`: id, from_zone, to_zone, w=3.0, bidirectional=True
  - `class Marking(BaseModel)`: id, kind, points=[[x,z]...], color="#fbbf24"
  - `class FloorShell(BaseModel)`: bounds{w,d,h?=0}, walls=[], zones=[], facilities=[], docks=[], corridors=[], markings=[], metadata={}, floors=[]
  - `class Floor(BaseModel)`: id, z, bounds{w,d}, walls, zones, facilities

- [ ] **Step 1: 写失败的测试 `test_floor_shell_model.py`**

```python
"""Pydantic models for floor blueprint."""
from rcs_backend.models.floor_shell import (
    WallSegment, Zone, Facility, Dock, Corridor, Marking, FloorShell, Floor,
)


def test_wall_segment_full():
    wall = WallSegment(id="w1", x0=0, z0=0, x1=10, z1=0)
    assert wall.h == 3.5
    assert wall.kind == "wall"
    assert wall.length() == pytest.approx(10.0)


def test_zone_with_cold_chain_metadata():
    zone = Zone(
        id="z1", ref="A1", type="cold_zone",
        x=0, z=0, w=10, d=10,
        temperature_range={"min": 2, "max": 8},
        batch_tracking=True,
        current_load_pct=75.0,
    )
    assert zone.temperature_range.max == 8
    assert zone.batch_tracking is True
    assert zone.current_load_pct == 75.0


def test_floor_shell_minimal():
    shell = FloorShell(bounds={"w": 100.0, "d": 80.0})
    assert shell.walls == []
    assert shell.zones == []
    assert shell.bounds.w == 100.0


def test_floor_shell_with_multi_floor():
    f1 = Floor(id="L1", z=0, bounds={"w": 80, "d": 60})
    shell = FloorShell(bounds={"w": 80, "d": 60, "h": 12}, floors=[f1])
    assert len(shell.floors) == 1
    assert shell.floors[0].z == 0


def test_zone_type_v2_2_covers_scenarios():
    """v2.2 must accept all 23 zone types from spec §13.3.2."""
    from rcs_backend.models.floor_shell import ZONE_TYPES
    expected = {
        # 电商
        "flow_rack", "high_rack", "mezzanine", "automated", "temp", "temp_bagged", "returns",
        # 制造
        "production_line", "wip_buffer", "parts_storage", "staging",
        # 冷链
        "cold_zone", "frozen_zone", "ambient_zone", "loading_bay",
        # 港口
        "container_yard", "customs_area",
        # 退货
        "returns_received", "qc_staging", "reshelving", "disposal",
        # 多层
        "floor_1", "floor_2", "floor_3", "elevator_shaft",
    }
    assert expected.issubset(ZONE_TYPES)


import pytest  # noqa: E402  (used in test_wall_segment_full)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_floor_shell_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rcs_backend.models.floor_shell'`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/models/__init__.py`**（Task 3 会追加 SiteGrid import）

```python
from rcs_backend.models.floor_shell import (
    WallSegment, Zone, Facility, Dock, Corridor, Marking, FloorShell, Floor,
)

__all__ = [
    "WallSegment", "Zone", "Facility", "Dock", "Corridor", "Marking", "FloorShell", "Floor",
]
```

- [ ] **Step 4: 创建 `rcs/backend/rcs_backend/models/floor_shell.py`**

```python
"""Floor blueprint data model — 23 zone types covering 6 scenarios."""
from __future__ import annotations
import math
from typing import Literal, Optional
from pydantic import BaseModel, Field, conlist


# v2.2 spec §13.3.2 — Zone types grouped by scenario
ZONE_TYPES = frozenset({
    # E-commerce
    "flow_rack", "high_rack", "mezzanine", "automated", "temp", "temp_bagged", "returns",
    # Manufacturing
    "production_line", "wip_buffer", "parts_storage", "staging",
    # Cold-chain
    "cold_zone", "frozen_zone", "ambient_zone", "loading_bay",
    # Port
    "container_yard", "customs_area",
    # Reverse logistics
    "returns_received", "qc_staging", "reshelving", "disposal",
    # Multi-floor
    "floor_1", "floor_2", "floor_3", "elevator_shaft",
})


class Bounds(BaseModel):
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    h: float = Field(default=0, ge=0)


class TempRange(BaseModel):
    min: float
    max: float


class WallSegment(BaseModel):
    id: str
    x0: float
    z0: float
    x1: float
    z1: float
    h: float = 3.5
    kind: Literal["wall", "glass", "rack", "fence"] = "wall"

    def length(self) -> float:
        return math.hypot(self.x1 - self.x0, self.z1 - self.z0)


class Zone(BaseModel):
    id: str
    ref: str
    type: str  # validated against ZONE_TYPES at use sites
    x: float
    z: float
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    name: Optional[str] = None
    site_node_ids: list[str] = Field(default_factory=list)
    temperature_range: Optional[TempRange] = None
    batch_tracking: bool = False
    hazard_level: Optional[Literal["none", "low", "medium", "high"]] = None
    customs_regulated: bool = False
    current_load_pct: float = Field(default=0.0, ge=0, le=100)


class Facility(BaseModel):
    id: str
    ref: str
    type: str
    x: float
    z: float
    w: float = Field(gt=0)
    d: float = Field(gt=0)
    h: float = Field(default=2.5, gt=0)


class Dock(BaseModel):
    id: str
    ref: str
    x: float
    z: float
    direction: Literal["N", "S", "E", "W"] = "N"
    door_w: float = Field(default=4.0, gt=0)


class Corridor(BaseModel):
    id: str
    from_zone: str
    to_zone: str
    w: float = Field(default=3.0, gt=0)
    bidirectional: bool = True


class Marking(BaseModel):
    id: str
    kind: Literal["lane", "stop", "crossing", "work_zone", "evac"] = "lane"
    points: conlist(conlist(float, min_length=2, max_length=2), min_length=2) = []
    color: str = "#fbbf24"


class Floor(BaseModel):
    id: str
    z: float
    bounds: Bounds
    walls: list[WallSegment] = Field(default_factory=list)
    zones: list[Zone] = Field(default_factory=list)
    facilities: list[Facility] = Field(default_factory=list)


class FloorShell(BaseModel):
    bounds: Bounds
    walls: list[WallSegment] = Field(default_factory=list)
    zones: list[Zone] = Field(default_factory=list)
    facilities: list[Facility] = Field(default_factory=list)
    docks: list[Dock] = Field(default_factory=list)
    corridors: list[Corridor] = Field(default_factory=list)
    markings: list[Marking] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    floors: list[Floor] = Field(default_factory=list)

    def zones_by_type(self, zone_type: str) -> list[Zone]:
        return [z for z in self.zones if z.type == zone_type]

    def total_zone_area_m2(self) -> float:
        return sum(z.w * z.d for z in self.zones)
```

- [ ] **Step 5: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_floor_shell_model.py -v`
Expected: PASS（5 tests）

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/models rcs/backend/tests/unit/test_floor_shell_model.py
git commit -m "feat(rcs-backend): FloorShell Pydantic model with 23 zone types (v2.2 spec §13.3.2)"
```