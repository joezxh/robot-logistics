## Task 7: 地面标线生成（markings）

**Files:**
- Create: `rcs/backend/rcs_backend/topology/markings.py`
- Create: `rcs/backend/tests/unit/test_markings.py`
- **Modify** `rcs/backend/rcs_backend/topology/__init__.py` (replace `generate_markings` placeholder)

**Interfaces:**
- Produces:
  - `def generate_markings(shell: FloorShell, lane_w=1.0) -> list[Marking]`: 自动生成走廊 lane / 装卸区 stop 线 / 货物区 crossing

- [ ] **Step 0: Replace placeholder in `topology/__init__.py`**

Edit `rcs/backend/rcs_backend/topology/__init__.py`: replace the `generate_markings` placeholder with `from rcs_backend.topology.markings import generate_markings`. Leave the other 2 placeholders (`list_templates`, `get_template`) for Task 8.

- [ ] **Step 1: 写失败的测试 `test_markings.py`**

```python
"""Auto-generate floor markings from FloorShell."""
from rcs_backend.topology.markings import generate_markings
from rcs_backend.models.floor_shell import (
    FloorShell, Bounds, WallSegment, Corridor, Zone, Marking, Dock,
)


def test_corridor_generates_lane_marking():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=10, d=10),
            Zone(id="z2", ref="B", type="staging", x=20, z=0, w=10, d=10),
        ],
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2", w=3.0)],
    )
    markings = generate_markings(shell)
    lanes = [m for m in markings if m.kind == "lane"]
    assert len(lanes) == 1
    assert lanes[0].points  # has geometry


def test_dock_zones_get_stop_markings():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        docks=[Dock(id="d1", ref="D1", x=10, z=10)],
    )
    markings = generate_markings(shell)
    stops = [m for m in markings if m.kind == "stop"]
    assert len(stops) == 1


def test_no_zones_no_corridors_no_docks_empty():
    shell = FloorShell(bounds=Bounds(w=10, d=10))
    assert generate_markings(shell) == []


def test_markings_have_color():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2")],
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=5, d=5),
            Zone(id="z2", ref="B", type="staging", x=10, z=0, w=5, d=5),
        ],
    )
    markings = generate_markings(shell)
    for m in markings:
        assert isinstance(m, Marking)
        assert m.color.startswith("#")


def test_lane_marks_both_directions_when_bidirectional():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=5, d=5),
            Zone(id="z2", ref="B", type="staging", x=10, z=0, w=5, d=5),
        ],
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2", bidirectional=True)],
    )
    markings = generate_markings(shell)
    # bidirectional corridor (default) generates 2 lane markings (forward + reverse)
    lanes = [m for m in markings if m.kind == "lane"]
    assert len(lanes) == 2
```

> **Plan patch note**: Brief's third test was named `test_no_zones_no_corridors_empty`.
> Renamed to `test_no_zones_no_corridors_no_docks_empty` to accurately describe the
> no-input case being asserted. Brief's fifth test asserted `len(markings) >= 1`,
> which is trivially true and doesn't actually verify bidirectionality. The patched
> test asserts exactly 2 lane markings for a bidirectional corridor (forward + reverse).

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && python -m pytest tests/unit/test_markings.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/markings.py`**

```python
"""Generate floor markings (lanes, stop lines) from FloorShell."""
from __future__ import annotations
import uuid
from rcs_backend.models.floor_shell import FloorShell, Marking


def generate_markings(shell: FloorShell, lane_w: float = 1.0) -> list[Marking]:
    out: list[Marking] = []

    # 1. Lane markings along each corridor
    zone_map = {z.id: z for z in shell.zones}
    for c in shell.corridors:
        if c.from_zone not in zone_map or c.to_zone not in zone_map:
            continue
        a, b = zone_map[c.from_zone], zone_map[c.to_zone]
        ax = a.x + a.w / 2
        az = a.z + a.d / 2
        bx = b.x + b.w / 2
        bz = b.z + b.d / 2
        out.append(Marking(
            id=f"m-lane-{uuid.uuid4().hex[:6]}",
            kind="lane",
            points=[[ax, az], [bx, bz]],
            color="#fbbf24",
        ))
        if c.bidirectional:
            out.append(Marking(
                id=f"m-lane-{uuid.uuid4().hex[:6]}",
                kind="lane",
                points=[[bx, bz], [ax, az]],
                color="#fbbf24",
            ))

    # 2. Stop lines at each dock
    for d in shell.docks:
        out.append(Marking(
            id=f"m-stop-{uuid.uuid4().hex[:6]}",
            kind="stop",
            points=[[d.x - 1.5, d.z], [d.x + 1.5, d.z]],
            color="#ef4444",
        ))

    return out
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && python -m pytest tests/unit/test_markings.py -v`
Expected: PASS（5 tests）

- [ ] **Step 5: 跑全 suite 确认无回归**

Run: `cd rcs/backend && python -m pytest -v`
Expected: 28 (prior) + 5 (new) = 33 passed

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/topology/markings.py \
        rcs/backend/rcs_backend/topology/__init__.py \
        rcs/backend/tests/unit/test_markings.py
git commit -m "feat(rcs-backend): auto-generate floor markings (lanes/stop lines)"
```
