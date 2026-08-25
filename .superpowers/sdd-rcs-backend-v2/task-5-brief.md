## Task 5: DXF → FloorShell 转换器

**Files:**
- Create: `rcs/backend/rcs_backend/topology/dxf_to_shell.py`
- Create: `rcs/backend/tests/unit/test_dxf_to_shell.py`
- **Modify** `rcs/backend/rcs_backend/topology/__init__.py` (replace placeholder)

**Interfaces:**
- Produces:
  - `def dxf_to_shell(doc: DxfDocument) -> FloorShell`: 按 layer 分组（FLOOR→bounds, WALLS→walls, ZONES→zones, FACILITIES→facilities, TEXT→zone refs）

- [ ] **Step 0: Replace placeholder in `topology/__init__.py`**

Edit `rcs/backend/rcs_backend/topology/__init__.py`: replace the placeholder `def dxf_to_shell(*args, **kwargs): raise NotImplementedError(...)` with the real import:

```python
from rcs_backend.topology.dxf_to_shell import dxf_to_shell
```

Also update the `__all__` list (already contains `"dxf_to_shell"` — no change needed).

- [ ] **Step 1: 写失败的测试 `test_dxf_to_shell.py`**

```python
"""Convert DXF document into FloorShell."""
from rcs_backend.topology.dxf_parser import DxfDocument, DxfEntity
from rcs_backend.topology.dxf_to_shell import dxf_to_shell
from rcs_backend.models.floor_shell import WallSegment, Zone, Facility


def _doc(entities: list[DxfEntity]) -> DxfDocument:
    return DxfDocument(entities=entities, header_units="m")


def test_walls_layer_becomes_wall_segments():
    doc = _doc([
        DxfEntity(type="LINE", layer="WALLS", vertices=[[0, 0], [10, 0]]),
        DxfEntity(type="LINE", layer="WALLS", vertices=[[10, 0], [10, 8]]),
    ])
    shell = dxf_to_shell(doc)
    assert len(shell.walls) == 2
    assert all(isinstance(w, WallSegment) for w in shell.walls)
    assert shell.walls[0].kind == "wall"


def test_zones_layer_becomes_zones_with_ref():
    doc = _doc([
        DxfEntity(type="LWPOLYLINE", layer="ZONES", vertices=[[0, 0], [10, 0], [10, 5], [0, 5]]),
        DxfEntity(type="TEXT", layer="TEXT", vertices=[[5, 2]], text="A1"),
    ])
    shell = dxf_to_shell(doc)
    assert len(shell.zones) == 1
    zone = shell.zones[0]
    assert zone.ref == "A1"
    assert zone.type == "staging"  # default type
    assert zone.w > 0 and zone.d > 0


def test_facilities_layer_becomes_facilities():
    doc = _doc([
        DxfEntity(type="CIRCLE", layer="FACILITIES", vertices=[[5, 5]], radius=2.0),
    ])
    shell = dxf_to_shell(doc)
    assert len(shell.facilities) == 1
    assert isinstance(shell.facilities[0], Facility)


def test_floor_layer_sets_bounds():
    doc = _doc([
        DxfEntity(type="LWPOLYLINE", layer="FLOOR", vertices=[[0, 0], [100, 0], [100, 80], [0, 80]]),
    ])
    shell = dxf_to_shell(doc)
    assert shell.bounds.w == pytest.approx(100.0)
    assert shell.bounds.d == pytest.approx(80.0)


def test_empty_doc_yields_empty_shell():
    shell = dxf_to_shell(_doc([]))
    assert shell.bounds.w == 0
    assert shell.walls == []
    assert shell.zones == []


import pytest  # noqa: E402
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_dxf_to_shell.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/dxf_to_shell.py`**

```python
"""Convert parsed DXF document into FloorShell model."""
from __future__ import annotations
import uuid
from rcs_backend.topology.dxf_parser import DxfDocument, DxfEntity
from rcs_backend.models.floor_shell import (
    FloorShell, WallSegment, Zone, Facility, Bounds,
)


def dxf_to_shell(doc: DxfDocument) -> FloorShell:
    """Group DXF entities by layer to produce a FloorShell."""
    walls: list[WallSegment] = []
    zones: list[Zone] = []
    facilities: list[Facility] = []
    bounds = Bounds(w=0.0, d=0.0)
    text_refs: dict[tuple[float, float], str] = {}

    # First pass: collect TEXT entities for zone references
    for e in doc.entities:
        if e.type in ("TEXT", "MTEXT") and e.vertices:
            pos = tuple(e.vertices[0])
            text_refs[pos] = e.text.strip()

    # Second pass: build shell
    for e in doc.entities:
        layer = e.layer.upper()
        if layer == "FLOOR" and e.type == "LWPOLYLINE":
            xs = [v[0] for v in e.vertices]
            zs = [v[1] for v in e.vertices]
            bounds = Bounds(w=max(xs) - min(xs), d=max(zs) - min(zs))
        elif layer == "WALLS" and e.type in ("LINE", "LWPOLYLINE"):
            if e.type == "LINE" and len(e.vertices) == 2:
                walls.append(WallSegment(
                    id=f"w-{uuid.uuid4().hex[:8]}",
                    x0=e.vertices[0][0], z0=e.vertices[0][1],
                    x1=e.vertices[1][0], z1=e.vertices[1][1],
                ))
            elif e.type == "LWPOLYLINE":
                for i in range(len(e.vertices) - 1):
                    walls.append(WallSegment(
                        id=f"w-{uuid.uuid4().hex[:8]}",
                        x0=e.vertices[i][0], z0=e.vertices[i][1],
                        x1=e.vertices[i + 1][0], z1=e.vertices[i + 1][1],
                    ))
        elif layer == "ZONES" and e.type == "LWPOLYLINE":
            xs = [v[0] for v in e.vertices]
            zs = [v[1] for v in e.vertices]
            x_min, x_max = min(xs), max(xs)
            z_min, z_max = min(zs), max(zs)
            cx, cz = (x_min + x_max) / 2, (z_min + z_max) / 2
            ref = text_refs.get((cx, cz)) or text_refs.get((round(cx, 1), round(cz, 1))) or f"Z-{uuid.uuid4().hex[:4]}"
            zones.append(Zone(
                id=f"z-{uuid.uuid4().hex[:8]}",
                ref=ref, type="staging",
                x=x_min, z=z_min,
                w=x_max - x_min, d=z_max - z_min,
            ))
        elif layer == "FACILITIES" and e.type == "CIRCLE":
            cx, cz = e.vertices[0]
            facilities.append(Facility(
                id=f"f-{uuid.uuid4().hex[:8]}",
                ref=f"F-{uuid.uuid4().hex[:4]}",
                type="generic",
                x=cx - e.radius, z=cz - e.radius,
                w=2 * e.radius, d=2 * e.radius,
            ))

    return FloorShell(
        bounds=bounds,
        walls=walls,
        zones=zones,
        facilities=facilities,
        metadata={"source": "dxf", "entity_count": len(doc.entities)},
    )
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_dxf_to_shell.py -v`
Expected: PASS（5 tests）

- [ ] **Step 5: 跑全 suite 确认无回归**

Run: `cd rcs/backend && pytest -v`
Expected: 17 (Tasks 2-4) + 5 (Task 5) = 22 passed

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/topology/dxf_to_shell.py \
        rcs/backend/rcs_backend/topology/__init__.py \
        rcs/backend/tests/unit/test_dxf_to_shell.py
git commit -m "feat(rcs-backend): dxf_to_shell converter (layer-based grouping)"
```