## Task 8: 6 场景预置模板（templates）

**Files:**
- Create: `rcs/backend/rcs_backend/topology/templates.py`
- Create: `rcs/backend/tests/unit/test_templates.py`
- **Modify** `rcs/backend/rcs_backend/topology/__init__.py` (replace `list_templates`, `get_template` placeholders)

**Interfaces:**
- Produces:
  - `SCENARIO_IDS = ["ecommerce","manufacturing","cold_chain","port","reverse_logistics","multi_floor"]`
  - `def list_templates() -> list[TemplateInfo]`: 返回所有 6 个模板的元数据
  - `def get_template(scenario_id: str) -> TemplateBundle`: 返回 shell + grid + metadata

- [ ] **Step 0: Replace placeholders in `topology/__init__.py`**

Edit `rcs/backend/rcs_backend/topology/__init__.py`: replace the `list_templates` and `get_template` placeholders with:

```python
from rcs_backend.topology.templates import (
    list_templates, get_template, SCENARIO_IDS, TemplateInfo, TemplateBundle,
)
```

Verify that after edits:
- The file still has the real imports from Tasks 4, 5, 6, 7 (parse_dxf, DxfEntity, DxfDocument, dxf_to_shell, validate_shell, ValidationError, ValidationReport, generate_markings).
- All 7 names are in `__all__` (or update `__all__` accordingly).
- No NotImplementedError placeholders remain.

- [ ] **Step 1: 写失败的测试 `test_templates.py`**

```python
"""6 scenario template factory."""
import pytest
from rcs_backend.topology.templates import (
    list_templates, get_template, SCENARIO_IDS, TemplateBundle, TemplateInfo,
)
from rcs_backend.models.floor_shell import FloorShell
from rcs_backend.models.site_grid import SiteGrid


def test_scenario_ids_count():
    assert len(SCENARIO_IDS) == 6
    assert "ecommerce" in SCENARIO_IDS
    assert "multi_floor" in SCENARIO_IDS


def test_list_templates_returns_six():
    templates = list_templates()
    assert len(templates) == 6
    for t in templates:
        assert isinstance(t, TemplateInfo)
        assert t.scenario_id
        assert t.bounds
        assert t.zone_count >= 1


def test_get_ecommerce_template():
    bundle = get_template("ecommerce")
    assert isinstance(bundle.shell, FloorShell)
    assert isinstance(bundle.grid, SiteGrid)
    assert bundle.shell.bounds.w > 0
    zone_types = {z.type for z in bundle.shell.zones}
    assert "flow_rack" in zone_types or "high_rack" in zone_types


def test_get_cold_chain_template():
    bundle = get_template("cold_chain")
    zone_types = {z.type for z in bundle.shell.zones}
    assert "cold_zone" in zone_types
    assert "frozen_zone" in zone_types


def test_get_port_template():
    bundle = get_template("port")
    zone_types = {z.type for z in bundle.shell.zones}
    assert "container_yard" in zone_types
    assert "customs_area" in zone_types


def test_get_multi_floor_has_floors():
    bundle = get_template("multi_floor")
    assert len(bundle.shell.floors) >= 3


def test_get_unknown_template_raises():
    with pytest.raises(KeyError):
        get_template("not_a_real_scenario")


def test_templates_have_scenario_metadata():
    bundle = get_template("reverse_logistics")
    assert bundle.shell.metadata.get("scenario") == "reverse_logistics"
```

> **Plan patch notes**:
> - Added `pytest` import (brief used it without import).
> - Added `TemplateInfo`/`TemplateBundle` to the import list (they're the public dataclass types; tests that do `isinstance` checks need them imported).
> - Test `test_list_templates_returns_six` now does `isinstance(t, TemplateInfo)` (brief only checked attributes).

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && python -m pytest tests/unit/test_templates.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/templates.py`**

```python
"""Pre-built floor blueprints for 6 logistics scenarios.

Each template returns a `TemplateBundle` containing:
- shell: FloorShell with scenario-appropriate zones/walls
- grid: SiteGrid with AGV navigation cells
- metadata: dict with bounds, theme, alert types
"""
from __future__ import annotations
from dataclasses import dataclass
from pydantic import BaseModel
from rcs_backend.models.floor_shell import (
    FloorShell, Bounds, Zone, Facility, Floor,
)
from rcs_backend.models.site_grid import SiteGrid


SCENARIO_IDS = [
    "ecommerce", "manufacturing", "cold_chain",
    "port", "reverse_logistics", "multi_floor",
]


class TemplateInfo(BaseModel):
    scenario_id: str
    name: str
    bounds: dict
    zone_count: int


@dataclass
class TemplateBundle:
    shell: FloorShell
    grid: SiteGrid
    metadata: dict


def list_templates() -> list[TemplateInfo]:
    out = []
    for sid in SCENARIO_IDS:
        b = get_template(sid)
        out.append(TemplateInfo(
            scenario_id=sid,
            name=sid.replace("_", " ").title(),
            bounds={"w": b.shell.bounds.w, "d": b.shell.bounds.d},
            zone_count=len(b.shell.zones) + sum(len(f.zones) for f in b.shell.floors),
        ))
    return out


def get_template(scenario_id: str) -> TemplateBundle:
    if scenario_id not in SCENARIO_IDS:
        raise KeyError(f"unknown scenario: {scenario_id}")
    builders = {
        "ecommerce": _ecommerce,
        "manufacturing": _manufacturing,
        "cold_chain": _cold_chain,
        "port": _port,
        "reverse_logistics": _reverse_logistics,
        "multi_floor": _multi_floor,
    }
    return builders[scenario_id]()


def _ecommerce() -> TemplateBundle:
    bounds = Bounds(w=160, d=100)
    zones = [
        Zone(id="z1", ref="R1", type="flow_rack", x=0, z=0, w=60, d=40),
        Zone(id="z2", ref="R2", type="high_rack", x=60, z=0, w=60, d=40),
        Zone(id="z3", ref="R3", type="mezzanine", x=120, z=0, w=40, d=40),
        Zone(id="z4", ref="ASRS", type="automated", x=0, z=40, w=40, d=60),
        Zone(id="z5", ref="TEMP", type="temp", x=40, z=40, w=30, d=20),
        Zone(id="z6", ref="TEMP-BAG", type="temp_bagged", x=70, z=40, w=30, d=20),
        Zone(id="z7", ref="RET", type="returns", x=100, z=40, w=30, d=20),
        Zone(id="z8", ref="STG", type="staging", x=130, z=40, w=30, d=60),
    ]
    shell = FloorShell(
        bounds=bounds, zones=zones,
        metadata={"scenario": "ecommerce", "theme": "warm"},
    )
    grid = _default_grid(160, 100)
    return TemplateBundle(
        shell=shell, grid=grid,
        metadata={"alert_types": ["overstock", "stockout"], "highlight_color": "#f59e0b"},
    )


def _manufacturing() -> TemplateBundle:
    bounds = Bounds(w=100, d=80)
    zones = []
    # 4 production lines + WIP + parts storage
    for i in range(4):
        zones.append(Zone(
            id=f"pl{i+1}", ref=f"PL{i+1}", type="production_line",
            x=10 + i * 22, z=10, w=20, d=15,
        ))
    zones += [
        Zone(id="wip1", ref="WIP-A", type="wip_buffer", x=10, z=30, w=80, d=15),
        Zone(id="ps1", ref="PS-A", type="parts_storage", x=10, z=50, w=40, d=20),
        Zone(id="stg1", ref="STG-OUT", type="staging", x=55, z=50, w=35, d=20),
    ]
    shell = FloorShell(bounds=bounds, zones=zones, metadata={"scenario": "manufacturing"})
    return TemplateBundle(
        shell=shell, grid=_default_grid(100, 80),
        metadata={"alert_types": ["material_shortage", "line_stop"], "highlight_color": "#64748b"},
    )


def _cold_chain() -> TemplateBundle:
    bounds = Bounds(w=80, d=60)
    zones = [
        Zone(id="fz", ref="FZ", type="frozen_zone", x=0, z=0, w=30, d=30,
             temperature_range={"min": -25, "max": -18}, batch_tracking=True),
        Zone(id="cz", ref="CZ", type="cold_zone", x=30, z=0, w=30, d=30,
             temperature_range={"min": 2, "max": 8}, batch_tracking=True),
        Zone(id="az", ref="AZ", type="ambient_zone", x=60, z=0, w=20, d=30),
        Zone(id="lb1", ref="LB1", type="loading_bay", x=0, z=30, w=40, d=20),
        Zone(id="lb2", ref="LB2", type="loading_bay", x=40, z=30, w=40, d=20),
        Zone(id="stg", ref="STG", type="staging", x=0, z=50, w=80, d=10),
    ]
    shell = FloorShell(bounds=bounds, zones=zones, metadata={"scenario": "cold_chain"})
    return TemplateBundle(
        shell=shell, grid=_default_grid(80, 60),
        metadata={"alert_types": ["temp_exceed", "humidity_exceed"], "highlight_color": "#3b82f6"},
    )


def _port() -> TemplateBundle:
    bounds = Bounds(w=200, d=150)
    zones = [
        Zone(id="cy1", ref="CY-A", type="container_yard", x=0, z=0, w=80, d=60),
        Zone(id="cy2", ref="CY-B", type="container_yard", x=80, z=0, w=80, d=60),
        Zone(id="ca", ref="CUSTOMS", type="customs_area", x=160, z=0, w=40, d=40,
             customs_regulated=True),
        Zone(id="lb1", ref="LB-IN", type="loading_bay", x=0, z=60, w=50, d=20),
        Zone(id="lb2", ref="LB-OUT", type="loading_bay", x=50, z=60, w=50, d=20),
        Zone(id="stg1", ref="STG-IM", type="staging", x=100, z=60, w=40, d=20,
             hazard_level="medium"),
        Zone(id="stg2", ref="STG-EX", type="staging", x=140, z=60, w=40, d=20),
        Zone(id="cz", ref="REEFER", type="cold_zone", x=0, z=80, w=60, d=30,
             temperature_range={"min": -25, "max": -18}),
    ]
    shell = FloorShell(bounds=bounds, zones=zones, metadata={"scenario": "port"})
    return TemplateBundle(
        shell=shell, grid=_default_grid(200, 150),
        metadata={"alert_types": ["customs_hold", "container_stuck"], "highlight_color": "#0ea5e9"},
    )


def _reverse_logistics() -> TemplateBundle:
    bounds = Bounds(w=60, d=40)
    zones = [
        Zone(id="rr", ref="RR", type="returns_received", x=0, z=0, w=60, d=10),
        Zone(id="qc1", ref="QC-A", type="qc_staging", x=0, z=10, w=30, d=15),
        Zone(id="qc2", ref="QC-B", type="qc_staging", x=30, z=10, w=30, d=15),
        Zone(id="rs", ref="RS", type="reshelving", x=0, z=25, w=40, d=15),
        Zone(id="dp", ref="DP", type="disposal", x=40, z=25, w=20, d=15),
    ]
    shell = FloorShell(bounds=bounds, zones=zones, metadata={"scenario": "reverse_logistics"})
    return TemplateBundle(
        shell=shell, grid=_default_grid(60, 40),
        metadata={"alert_types": ["return_surge", "disposal_exceeded"], "highlight_color": "#ef4444"},
    )


def _multi_floor() -> TemplateBundle:
    bounds = Bounds(w=80, d=60, h=12)
    floors = []
    for i, z_floor in enumerate([0.0, 4.0, 8.0]):
        floors.append(Floor(
            id=f"L{i+1}", z=z_floor,
            bounds=Bounds(w=80, d=60),
            zones=[
                Zone(id=f"f{i+1}-s", ref=f"STG-{i+1}", type="staging",
                     x=0, z=0, w=30, d=20),
                Zone(id=f"f{i+1}-r", ref=f"RACK-{i+1}",
                     type="floor_1" if i == 0 else ("floor_2" if i == 1 else "floor_3"),
                     x=30, z=0, w=50, d=40),
            ],
        ))
    zones = [Zone(id="el1", ref="EL-1", type="elevator_shaft", x=70, z=50, w=5, d=5)]
    shell = FloorShell(bounds=bounds, zones=zones, floors=floors, metadata={"scenario": "multi_floor"})
    return TemplateBundle(
        shell=shell, grid=_default_grid(80, 60),
        metadata={"alert_types": ["elevator_fault"], "highlight_color": "#475569"},
    )


def _default_grid(w: float, d: float, resolution: float = 2.0) -> SiteGrid:
    """Build a basic EMPTY-cell grid covering w×d meters at the given resolution.

    Plan patch: brief's `_default_grid` called
        SiteGrid(bounds={"w": w, "d": d}, cell_size=2.0, cells=cells)
    which fails for four reasons in the actual `SiteGrid` model:
      1. `SiteGrid` requires `site_id: str` (no default) — brief omits it.
      2. `SiteGrid` uses `resolution` not `cell_size`.
      3. `SiteGrid.cells` is `list[list[Cell]]` (2D), brief passes a flat list
         and uses `CellType.FREE` which doesn't exist in the enum.
      4. Cells are int-indexed (`x: int`, `z: int`), not float meters.

    We use SiteGrid's built-in `_auto_populate` which fills an empty grid with
    EMPTY cells at the requested resolution — exactly the "basic FREE-cell grid"
    the brief described, just spelled differently.
    """
    return SiteGrid(
        site_id="default",
        bounds={"w": w, "d": d},
        resolution=resolution,
    )
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && python -m pytest tests/unit/test_templates.py -v`
Expected: PASS（8 tests）

- [ ] **Step 5: 跑全 suite 确认无回归**

Run: `cd rcs/backend && python -m pytest -v`
Expected: 33 (prior) + 8 (new) = 41 passed

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/topology/templates.py \
        rcs/backend/rcs_backend/topology/__init__.py \
        rcs/backend/tests/unit/test_templates.py
git commit -m "feat(rcs-backend): 6 scenario templates (ecommerce/manufacturing/cold_chain/port/reverse/multi_floor)"
```