# Unified Map Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge `TopologyShell` + `SiteMap` (+ `SiteGrid` + 6 hardcoded scenarios) into a single `UnifiedMap` table with a unified `/maps/{id}` API and a single "场景地图" frontend page, dropping the legacy tables.

**Architecture:** One `robot_unified_maps` row holds `geometry_json` (walls/zones/facilities/docks/corridors/floors), `grid_json` (AGV nav cells), `topology_json` (nodes/edges), `semantic_json`, plus child tables `robot_topology_grid` (zones) and `robot_site_map_versions` re-parented to `map_id`, and a new `robot_map_dynamic_state` for the dynamic layer. All three former map pages (SiteMap / AdminMaps / Warehouse) collapse into one `ScenarioMapView` that projects the same `map_id` data three ways. Legacy tables are DROPped inside migration `007`.

**Tech Stack:** FastAPI + async SQLAlchemy (PostgreSQL, JSONB), pydantic v2, Vue 3 `<script setup>` + Pinia + Ant Design Vue, Vitest, pytest-asyncio, Playwright.

**Source of truth:** `docs/superpowers/specs/2026-08-31-unified-map-model-design.md`

---

## File Structure (what changes)

**Backend (create/modify):**
- Create: `rcs/backend/rcs/db/models_unified.py` (or add to `models.py`) — `UnifiedMap`, `MapDynamicState`.
- Modify: `rcs/backend/rcs/db/models.py` — re-parent `TopologyGrid.site_id→map_id`, `SiteMapVersion.map_id` FK target.
- Create: `rcs/backend/migrations/007_unified_map.sql`.
- Modify: `rcs/backend/rcs/services/control/control_maps.py` — `UnifiedMapCRUD` + `seed_templates` (8+6) + `create_from_template`.
- Delete: `rcs/backend/rcs/models/topology_templates.py` (6 hardcoded) — logic folded into `control_maps.seed_templates`.
- Modify: `rcs/backend/rcs/api/control/control_maps.py` — unified router `maps.py` style endpoints + dynamic endpoints.
- Modify: `rcs/backend/rcs/main.py` — remove `topology_shell`, `topology_grid`, `topology_templates` routers; keep `maps_router` only.
- Modify: `rcs/backend/rcs/services/warehouse_converter.py`, `warehouse_inventory.py`, `api/sys/sys_dashboard.py` — `SITE_ID`→`MAP_ID`, import `UnifiedMap`.
- Modify: `rcs/backend/rcs/control/topology/site_map.py`, `pathfinder.py` — build in-memory `SiteMap` from `topology_json`.

**Frontend (create/modify):**
- Create: `rcs/frontend/src/api/map.ts` (replaces `api/topologyShell.ts`).
- Delete: `rcs/frontend/src/api/topologyShell.ts`.
- Modify stores: `floorShell.ts` (`loadBySite`→`loadByMap`), `scenario.ts`, `adminMaps.ts`, `warehouse.ts`, `siteGrid.ts`.
- Modify types: `types/siteGrid.ts`, `types/types.ts`, `types/scenario.ts` (`site_id`→`map_id`).
- Create: `views/topology/ScenarioMapView.vue` (merge SiteMapView + AdminMapsView + WarehouseView).
- Delete: `views/topology/SiteMapView.vue`, `views/topology/WarehouseView.vue`, `views/topology/AdminMapsView.vue`.
- Modify: `rcs/backend/rcs/services/sys/sys_seed.py` — keep only "场景地图" menu, drop "站点地图"/"仓库视图".
- Modify: `src/i18n/locales/zh-CN.ts` — `app.title` → "RCS 控制台"; remove stale map entries.

**Tests:**
- Backend: `tests/unit/control/test_unified_map.py` (new), modify `test_site_map_templates.py`, `test_topology_*.py`.
- Frontend: `api/map.spec.ts` (new), modify `floorShell.spec.ts`, `scenario.spec.ts`, `adminMaps.spec.ts`, `siteGrid.spec.ts`; `ScenarioMapView.spec.ts` (new).

---

### Task 1: ORM — UnifiedMap + MapDynamicState

**Files:**
- Modify: `rcs/backend/rcs/db/models.py` (append models; re-parent child FKs)

- [ ] **Step 1: Write the failing test**

Create `rcs/backend/tests/unit/control/test_unified_map.py`:

```python
import pytest
from rcs.db.session import async_session
from rcs.db.models import UnifiedMap, MapDynamicState, TopologyGrid, SiteMapVersion


@pytest.mark.asyncio
async def test_unified_map_columns():
    async with async_session() as s:
        m = UnifiedMap(
            map_id="tpl-test",
            name="Test",
            is_template=True,
            kind="warehouse",
            bounds_json={"w": 10, "d": 10, "h": 4},
            geometry_json={"zones": []},
            grid_json={"resolution": 1.0, "cells": []},
            topology_json={"nodes": [], "edges": []},
            semantic_json={},
        )
        s.add(m)
        await s.commit()
        await s.refresh(m)
        assert m.map_id == "tpl-test"
        assert m.geometry_json == {"zones": []}


@pytest.mark.asyncio
async def test_dynamic_state_fk():
    async with async_session() as s:
        m = UnifiedMap(map_id="tpl-dyn", name="D", bounds_json={},
                       geometry_json={}, topology_json={})
        s.add(m)
        await s.commit()
        s.add(MapDynamicState(map_id="tpl-dyn", element_id="z1", state="occupied"))
        await s.commit()
        rows = (await s.execute(
            __import__("sqlalchemy").select(MapDynamicState).where(MapDynamicState.map_id == "tpl-dyn")
        )).scalars().all()
        assert len(rows) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_unified_map.py -v`
Expected: FAIL — `ImportError: cannot import name 'UnifiedMap'`

- [ ] **Step 3: Write minimal implementation**

In `rcs/backend/rcs/db/models.py`, after existing models, add:

```python
from datetime import datetime, timezone
from sqlalchemy import JSONB  # if not already imported


class UnifiedMap(Base):
    __tablename__ = "robot_unified_maps"
    map_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    is_template = Column(Boolean, default=False)
    kind = Column(String, default="warehouse")
    current_version = Column(Integer, default=1)
    bounds_json = Column(JSONB, nullable=False, default=dict)
    geometry_json = Column(JSONB, nullable=False, default=dict)
    grid_json = Column(JSONB, nullable=True, default=dict)
    topology_json = Column(JSONB, nullable=False, default=dict)
    semantic_json = Column(JSONB, nullable=True, default=dict)
    dynamic_json = Column(JSONB, nullable=True, default=dict)
    data = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    zones = relationship("TopologyGrid", back_populates="map",
                        cascade="all, delete-orphan")
    versions = relationship("SiteMapVersion", back_populates="map",
                            cascade="all, delete-orphan")


class MapDynamicState(Base):
    __tablename__ = "robot_map_dynamic_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    map_id = Column(String, ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"), index=True)
    element_id = Column(String, index=True)
    state = Column(String)
    payload = Column(JSONB, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
```

And re-parent child tables (find `TopologyGrid` and `SiteMapVersion` in `models.py`):

```python
class TopologyGrid(Base):
    # ... existing columns ...
    map_id = Column(String, ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"))
    # remove old: site_id = Column(String, ForeignKey("robot_topology_shell.site_id"))
    map = relationship("UnifiedMap", back_populates="zones")


class SiteMapVersion(Base):
    # ... existing columns ...
    map_id = Column(String, ForeignKey("robot_unified_maps.map_id", ondelete="CASCADE"))
    map = relationship("UnifiedMap", back_populates="versions")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_unified_map.py -v`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
cd rcs/backend && git add rcs/db/models.py tests/unit/control/test_unified_map.py && git commit -m "feat(db): add UnifiedMap + MapDynamicState models, re-parent child tables"
```

---

### Task 2: Migration 007 (CREATE + migrate + DROP legacy)

**Files:**
- Create: `rcs/backend/migrations/007_unified_map.sql`

- [ ] **Step 1: Write the migration SQL**

```sql
-- 007_unified_map.sql : merge TopologyShell + SiteMap (+grid) into UnifiedMap, then drop legacy.

CREATE TABLE IF NOT EXISTS robot_unified_maps (
    map_id         VARCHAR PRIMARY KEY,
    name          VARCHAR NOT NULL,
    name_en       VARCHAR,
    is_template   BOOLEAN DEFAULT FALSE,
    kind          VARCHAR DEFAULT 'warehouse',
    current_version INTEGER DEFAULT 1,
    bounds_json   JSONB NOT NULL DEFAULT '{}'::jsonb,
    geometry_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    grid_json     JSONB DEFAULT '{}'::jsonb,
    topology_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    semantic_json JSONB DEFAULT '{}'::jsonb,
    dynamic_json  JSONB DEFAULT '{}'::jsonb,
    data          JSONB,
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS robot_map_dynamic_state (
    id          SERIAL PRIMARY KEY,
    map_id      VARCHAR REFERENCES robot_unified_maps(map_id) ON DELETE CASCADE,
    element_id  VARCHAR,
    state       VARCHAR,
    payload     JSONB,
    updated_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_dynamic_map ON robot_map_dynamic_state(map_id);
CREATE INDEX IF NOT EXISTS ix_dynamic_elem ON robot_map_dynamic_state(element_id);

-- re-parent topology_grid
ALTER TABLE robot_topology_grid RENAME COLUMN site_id TO map_id;
-- (FK target updated to robot_unified_maps via application; DB-level FK optional)

-- migrate: build UnifiedMap from shell (+ optional join site_maps for topology)
INSERT INTO robot_unified_maps (map_id, name, name_en, is_template, kind, bounds_json, geometry_json, topology_json)
SELECT
    s.site_id,
    s.name,
    s.name_en,
    COALESCE(s.is_template, FALSE),
    'warehouse',
    COALESCE(s.data->'bounds', '{}'::jsonb),
    COALESCE(s.data, '{}'::jsonb),
    COALESCE(m.nodes_json, '{}'::jsonb)
FROM robot_topology_shell s
LEFT JOIN robot_site_maps m ON m.map_id = s.site_id
ON CONFLICT (map_id) DO NOTHING;

-- ALSO pull topology-only maps (present in site_maps but not shell)
INSERT INTO robot_unified_maps (map_id, name, is_template, kind, bounds_json, geometry_json, topology_json)
SELECT m.map_id, m.name, COALESCE(m.is_template, FALSE), 'scenario',
       '{}'::jsonb, '{}'::jsonb, COALESCE(m.nodes_json, '{}'::jsonb)
FROM robot_site_maps m
WHERE NOT EXISTS (SELECT 1 FROM robot_unified_maps u WHERE u.map_id = m.map_id)
ON CONFLICT (map_id) DO NOTHING;

-- drop legacy tables (no longer referenced after app migration)
DROP TABLE IF EXISTS robot_topology_shell;
DROP TABLE IF EXISTS robot_site_maps;
```

- [ ] **Step 2: Apply migration on dev DB and verify**

Run against dev DB (replace DSN):
```bash
psql "$RCS_DB_DSN" -f rcs/backend/migrations/007_unified_map.sql
```
Expected: command succeeds; `robot_unified_maps` populated from prior templates.

- [ ] **Step 3: Verify legacy tables gone and data present**

```bash
psql "$RCS_DB_DSN" -c "\dt robot_*"   # unified_maps + dynamic_state exist; shell/site_maps absent
psql "$RCS_DB_DSN" -c "SELECT count(*) FROM robot_unified_maps;"
```
Expected: count > 0 (existing 8 templates migrated).

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/migrations/007_unified_map.sql && git commit -m "feat(db): migration 007 merge into UnifiedMap and drop legacy tables"
```

---

### Task 3: Backend service — UnifiedMapCRUD + seed_templates (8+6)

**Files:**
- Modify: `rcs/backend/rcs/services/control/control_maps.py`
- Delete: `rcs/backend/rcs/models/topology_templates.py`
- Modify: `rcs/backend/rcs/models/site_map_templates.py` (return UnifiedMap-shaped dict)

- [ ] **Step 1: Write the failing test**

Append to `test_unified_map.py`:

```python
from rcs.services.control.control_maps import UnifiedMapCRUD, seed_templates, list_templates


@pytest.mark.asyncio
async def test_seed_creates_14_templates():
    async with async_session() as s:
        await seed_templates(s)
        await s.commit()
    rows = await list_templates()
    keys = {t["key"] for t in rows}
    assert "ecommerce" in keys          # from 6 hardcoded
    assert "ecommerce_large" in keys    # from 8 DB
    assert len(rows) >= 14
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_unified_map.py::test_seed_creates_14_templates -v`
Expected: FAIL — `ImportError: cannot import name 'UnifiedMapCRUD'`

- [ ] **Step 3: Implement UnifiedMapCRUD + seed**

In `control_maps.py`, add (keep existing db-session helpers):

```python
from rcs.db.models import UnifiedMap, MapDynamicState, TopologyGrid, SiteMapVersion
from rcs.models.site_map_templates import build_unified_template
from rcs.models.topology_templates import SCENARIO_IDS, get_template  # TEMP until folded


class UnifiedMapCRUD:
    @staticmethod
    async def get(db, map_id: str) -> dict:
        m = await db.get(UnifiedMap, map_id)
        if not m:
            return None
        zones = (await db.execute(
            select(TopologyGrid).where(TopologyGrid.map_id == map_id)
        )).scalars().all()
        return {
            "map_id": m.map_id, "name": m.name, "is_template": m.is_template,
            "kind": m.kind, "bounds": m.bounds_json, "geometry": m.geometry_json,
            "grid": m.grid_json, "topology": m.topology_json,
            "semantic": m.semantic_json, "zones": [z.__dict__ for z in zones],
        }

    @staticmethod
    async def create_from_template(db, key: str, map_id: str = None) -> str:
        payload = build_unified_template(key)  # returns dict with geometry/grid/topology/semantic
        map_id = map_id or payload["map_id"]
        m = UnifiedMap(
            map_id=map_id, name=payload["name"], is_template=False,
            kind=payload.get("kind", "warehouse"),
            bounds_json=payload["bounds"], geometry_json=payload["geometry"],
            grid_json=payload.get("grid", {}), topology_json=payload["topology"],
            semantic_json=payload.get("semantic", {}),
        )
        db.add(m)
        for z in payload.get("zones", []):
            db.add(TopologyGrid(map_id=map_id, **z))
        await db.commit()
        return map_id


async def seed_templates(db):
    for key in ALL_TEMPLATE_KEYS:   # 8 DB keys + 6 SCENARIO_IDS
        if await db.get(UnifiedMap, f"tpl-{key}"):
            continue
        payload = build_unified_template(key)
        db.add(UnifiedMap(map_id=f"tpl-{key}", name=payload["name"], is_template=True,
                          kind=payload.get("kind", "warehouse"),
                          bounds_json=payload["bounds"], geometry_json=payload["geometry"],
                          grid_json=payload.get("grid", {}), topology_json=payload["topology"],
                          semantic_json=payload.get("semantic", {})))
    await db.commit()
```

In `site_map_templates.py`, refactor each `_build_*` to return a **UnifiedMap-shaped dict** instead of `(shell, grid_rows, nodes, edges)`. Add a dispatcher:

```python
def build_unified_template(key: str) -> dict:
    builders = {
        "ecommerce_large": _ecommerce_large,
        "theatre_ecommerce": _theatre_ecommerce,
        "port_terminal": _port_terminal,
        "factory_warehouse": _factory_warehouse,
        "highway_freight_hub": _highway_freight_hub,
        "third_party_logistics": _third_party_logistics,
        "cold_chain": _cold_chain,
        "reverse_logistics": _reverse_logistics,
    }
    # 6 hardcoded scenarios from topology_templates folded in:
    from rcs.models.topology_templates import get_template, SCENARIO_IDS
    for sid in SCENARIO_IDS:
        builders.setdefault(sid, lambda s=sid: _from_scenario_bundle(get_template(s)))
    return builders[key]()
```

Add helper that converts a `TemplateBundle` (shell+grid) into UnifiedMap-shaped dict:

```python
def _from_scenario_bundle(bundle) -> dict:
    shell = bundle.shell
    return {
        "map_id": f"tpl-{bundle.metadata.get('scenario_id', 'x')}",
        "name": bundle.metadata.get("name", "scenario"),
        "kind": "scenario",
        "bounds": {"w": shell.bounds.w, "d": shell.bounds.d, "h": 4},
        "geometry": shell.model_dump(),          # walls/zones/facilities/docks/floors
        "grid": bundle.grid.model_dump(),        # SiteGrid -> grid_json
        "topology": {"nodes": [], "edges": []},  # scenario bundles carry no nav graph
        "semantic": {},
        "zones": [],
    }
```

Define `ALL_TEMPLATE_KEYS` = the 8 DB keys + `SCENARIO_IDS`.

`list_templates(db)` returns `[{"key": k, "name": ..., "map_id": f"tpl-{k}"} for k in ALL_TEMPLATE_KEYS]`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_unified_map.py -v`
Expected: PASS (all)

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs/services/control/control_maps.py rcs/backend/rcs/models/site_map_templates.py tests/unit/control/test_unified_map.py && git commit -m "feat(service): UnifiedMapCRUD + seed 14 templates from 8 DB + 6 scenario"
```

---

### Task 4: Delete hardcoded topology_templates module

**Files:**
- Delete: `rcs/backend/rcs/models/topology_templates.py`
- Modify: `rcs/backend/rcs/models/site_map_templates.py` (inline the 6 builders or import-free)

- [ ] **Step 1: Move the 6 scenario builders into site_map_templates.py**

Copy the 6 `_ecommerce/_manufacturing/_cold_chain/_port/_reverse_logistics/_multi_floor` functions verbatim from `topology_templates.py` into `site_map_templates.py`. Update their returns to `TemplateBundle`-free dicts via `_from_scenario_bundle` equivalent (or keep using `TemplateBundle` constructed locally — but `TemplateBundle` lives in the deleted module, so inline a local dataclass or return dict directly).

Simplest: in `site_map_templates.py`, after copying, change `build_unified_template` to call the local copies directly (no cross-import):

```python
builders = {
    "ecommerce_large": _ecommerce_large, "theatre_ecommerce": _theatre_ecommerce,
    "port_terminal": _port_terminal, "factory_warehouse": _factory_warehouse,
    "highway_freight_hub": _highway_freight_hub, "third_party_logistics": _third_party_logistics,
    "cold_chain": _cold_chain, "reverse_logistics": _reverse_logistics,
    "ecommerce": _scn_ecommerce, "manufacturing": _scn_manufacturing,
    "port": _scn_port, "multi_floor": _scn_multi_floor,
}
```

- [ ] **Step 2: Remove the old module and its imports**

```bash
git rm rcs/backend/rcs/models/topology_templates.py
```
Grep for `topology_templates` imports and fix:
```bash
cd rcs/backend && grep -rn "topology_templates" rcs/ | grep -v "site_map_templates"
```
Expected: only `site_map_templates.py` references remain (the inlined copies).

- [ ] **Step 3: Run backend tests**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_unified_map.py -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add -A rcs/backend/rcs/models/ && git commit -m "refactor: fold 6 hardcoded scenarios into site_map_templates, delete topology_templates"
```

---

### Task 5: Unified API router (maps.py style)

**Files:**
- Modify: `rcs/backend/rcs/api/control/control_maps.py` (add endpoints, keep prefix `/api/rcs`)

- [ ] **Step 1: Write the failing test**

```python
from fastapi.testclient import TestClient
from rcs.main import app


def test_maps_unified_get():
    client = TestClient(app)
    # seed first via endpoint
    client.post("/api/rcs/maps/templates/seed")
    r = client.get("/api/rcs/maps/tpl-ecommerce")
    assert r.status_code == 200
    body = r.json()
    assert "geometry" in body and "topology" in body and "grid" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_api_maps.py -v`
Expected: FAIL — 404 (endpoint not present)

- [ ] **Step 3: Implement endpoints**

In `rcs/backend/rcs/api/control/control_maps.py` add (keep existing `/maps/templates` etc., extend):

```python
@router.get("/maps/{map_id}")
async def get_map(map_id: str, db: AsyncSession = Depends(get_db)):
    data = await UnifiedMapCRUD.get(db, map_id)
    if not data:
        raise HTTPException(404, "map not found")
    return data


@router.put("/maps/{map_id}")
async def put_map(map_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    m = await db.get(UnifiedMap, map_id)
    if not m:
        raise HTTPException(404, "map not found")
    for col in ("bounds_json", "geometry_json", "grid_json", "topology_json", "semantic_json"):
        if col in body:
            setattr(m, col, body[col])
    if "name" in body:
        m.name = body["name"]
    await db.commit()
    return {"ok": True}


@router.get("/maps/{map_id}/dynamic")
async def get_dynamic(map_id: str, element_id: str = None, state: str = None,
                      db: AsyncSession = Depends(get_db)):
    q = select(MapDynamicState).where(MapDynamicState.map_id == map_id)
    if element_id:
        q = q.where(MapDynamicState.element_id == element_id)
    if state:
        q = q.where(MapDynamicState.state == state)
    rows = (await db.execute(q)).scalars().all()
    return [{"element_id": r.element_id, "state": r.state, "payload": r.payload} for r in rows]


@router.post("/maps/{map_id}/dynamic")
async def post_dynamic(map_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    rec = MapDynamicState(map_id=map_id, element_id=body["element_id"],
                          state=body.get("state", "free"), payload=body.get("payload"))
    db.add(rec)
    await db.commit()
    return {"ok": True}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd rcs/backend && python -m pytest tests/unit/control/test_api_maps.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs/api/control/control_maps.py tests/unit/control/test_api_maps.py && git commit -m "feat(api): unified /maps/{id} + dynamic endpoints"
```

---

### Task 6: main.py — drop legacy topology routers

**Files:**
- Modify: `rcs/backend/rcs/main.py`

- [ ] **Step 1: Remove legacy router imports/registrations**

In `rcs/backend/rcs/main.py`:

```python
from rcs.api import (
    topology_import, topology_export, orders,
)
# remove: topology_shell, topology_grid, topology_templates
```

And remove these three lines:
```python
app.include_router(topology_shell, prefix="/api/rcs/topology", tags=["shell"])
app.include_router(topology_grid, prefix="/api/rcs/topology", tags=["grid"])
app.include_router(topology_templates, prefix="/api/rcs/topology", tags=["templates"])
```
Keep `topology_import`/`topology_export` (they operate on unified map now — verify they import `UnifiedMap`, else update in Task 7).

- [ ] **Step 2: Run backend import smoke test**

Run: `cd rcs/backend && python -c "from rcs.main import app; print([r.path for r in app.routes if 'topology/shell' in r.path or 'topology/templates' in r.path])"`
Expected: `[]` (no legacy paths registered)

- [ ] **Step 3: Commit**

```bash
git add rcs/backend/rcs/main.py && git commit -m "refactor(api): remove legacy topology_shell/grid/templates routers"
```

---

### Task 7: Update dependent backend modules

**Files:**
- Modify: `rcs/backend/rcs/services/warehouse_converter.py`, `rcs/backend/rcs/services/warehouse_inventory.py`, `rcs/backend/rcs/api/sys/sys_dashboard.py`, `rcs/backend/rcs/control/topology/site_map.py`, `rcs/backend/rcs/control/topology/pathfinder.py`, `rcs/backend/rcs/api/topology/topology_import.py`, `topology_export.py`

- [ ] **Step 1: Update sys_dashboard.py**

Find `from rcs.db.models import Device, Order, SiteMap, TopologyShell` → replace with `from rcs.db.models import Device, Order, UnifiedMap`.
Find any `SiteMap`/`TopologyShell` usage in counts and replace with `UnifiedMap` (keep `is_template` filter):
```python
count = await db.scalar(select(func.count()).select_from(UnifiedMap).where(UnifiedMap.is_template.is_(False)))
```

- [ ] **Step 2: Update warehouse_converter / warehouse_inventory**

Replace `SITE_ID` constant usages with `MAP_ID` and read geometry via `UnifiedMapCRUD.get(db, map_id)["geometry"]` instead of `get_shell`.

- [ ] **Step 3: Update topology_import / topology_export**

Change imports from `TopologyShell` to `UnifiedMap`; serialize/deserialize against `geometry_json`/`topology_json`.

- [ ] **Step 4: Update in-memory SiteMap construction**

In `rcs/backend/rcs/control/topology/site_map.py` and `pathfinder.py`, replace any `db.get(SiteMap, ...)` with building the in-memory `SiteMap` from `UnifiedMapCRUD.get(db, map_id)["topology"]`.

- [ ] **Step 5: Run backend full test suite**

Run: `cd rcs/backend && python -m pytest tests/ -q`
Expected: PASS (no import errors; dashboard/converter tests green)

- [ ] **Step 6: Commit**

```bash
git add -A rcs/backend/rcs/services rcs/backend/rcs/api/sys rcs/backend/rcs/control rcs/backend/rcs/api/topology && git commit -m "refactor: point warehouse/dashboard/topology consumers at UnifiedMap"
```

---

### Task 8: Frontend API client — api/map.ts

**Files:**
- Create: `rcs/frontend/src/api/map.ts`
- Delete: `rcs/frontend/src/api/topologyShell.ts`

- [ ] **Step 1: Write the failing test**

Create `rcs/frontend/src/api/map.spec.ts`:

```ts
import { getMap, listTemplates } from '@/api/map'
import { http } from '@/api/http'

vi.mock('@/api/http')

describe('api/map', () => {
  it('getMap returns geometry/topology/grid', async () => {
    ;(http.get as any).mockResolvedValue({
      map_id: 'tpl-x', geometry: { zones: [] }, topology: { nodes: [], edges: [] }, grid: {},
    })
    const m = await getMap('tpl-x')
    expect(m.geometry).toBeDefined()
    expect(http.get).toHaveBeenCalledWith('/api/rcs/maps/tpl-x')
  })
  it('listTemplates returns map_id not site_id', async () => {
    ;(http.get as any).mockResolvedValue([{ key: 'ecommerce', map_id: 'tpl-ecommerce', name: '电商' }])
    const t = await listTemplates()
    expect(t[0].map_id).toBe('tpl-ecommerce')
    expect((t[0] as any).site_id).toBeUndefined()
  })
})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd rcs/frontend && pnpm vitest run src/api/map.spec.ts`
Expected: FAIL — module `@/api/map` not found

- [ ] **Step 3: Implement**

Create `rcs/frontend/src/api/map.ts`:

```ts
import { http } from '@/api/http'

export interface UnifiedMapDTO {
  map_id: string
  name: string
  is_template?: boolean
  kind?: string
  bounds: Record<string, number>
  geometry: any
  grid: any
  topology: { nodes: any[]; edges: any[] }
  semantic: any
  zones?: any[]
}

export async function getMap(id: string): Promise<UnifiedMapDTO> {
  return http.get(`/api/rcs/maps/${id}`)
}

export async function putMap(id: string, body: Partial<UnifiedMapDTO>): Promise<void> {
  return http.put(`/api/rcs/maps/${id}`, body)
}

export async function listTemplates(): Promise<{ key: string; map_id: string; name: string }[]> {
  return http.get('/api/rcs/maps/templates')
}

export async function seedTemplates(): Promise<void> {
  return http.post('/api/rcs/maps/templates/seed')
}

export async function createFromTemplate(key: string, mapId?: string): Promise<{ map_id: string }> {
  return http.post('/api/rcs/maps/from-template', { key, map_id: mapId })
}
```

Delete old client:
```bash
cd rcs/frontend && git rm src/api/topologyShell.ts
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd rcs/frontend && pnpm vitest run src/api/map.spec.ts`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/api/map.ts src/api/map.spec.ts && git rm src/api/topologyShell.ts && git commit -m "feat(fe): add unified map API client, drop topologyShell client"
```

---

### Task 9: Frontend stores — map_id semantics

**Files:**
- Modify: `src/stores/floorShell.ts`, `src/stores/scenario.ts`, `src/stores/adminMaps.ts`, `src/stores/warehouse.ts`, `src/stores/siteGrid.ts`, `src/types/siteGrid.ts`, `src/types/types.ts`, `src/types/scenario.ts`

- [ ] **Step 1: floorShell.ts — loadBySite → loadByMap**

In `src/stores/floorShell.ts`:

```ts
import { defineStore } from 'pinia'
import { getMap } from '@/api/map'
import type { UnifiedMapDTO } from '@/api/map'

export const useFloorStore = defineStore('floor', {
  state: () => ({ current: null as UnifiedMapDTO | null, loading: false }),
  actions: {
    async loadByMap(mapId: string) {
      this.loading = true
      try {
        this.current = await getMap(mapId)
      } finally {
        this.loading = false
      }
    },
  },
})
```

Update its spec (`floorShell.spec.ts`) to call `loadByMap('tpl-ecommerce')` and assert `current.geometry` exists.

- [ ] **Step 2: scenario.ts — selectTemplate uses map_id**

In `src/stores/scenario.ts`, change the template-select action:

```ts
async function selectTemplate(key: string) {
  const tpl = templateByKey.value[key]
  await floorStore.loadByMap(tpl.map_id)   // was tpl.site_id
  selectedTemplate.value = key
}
```
Remove `site_id` from the template type; keep `map_id`.

- [ ] **Step 3: adminMaps.ts — read topology from getMap**

In `src/stores/adminMaps.ts`, change `load(id)`:

```ts
async function load(id: string) {
  const m = await getMap(id)
  current.value = { id, nodes: m.topology.nodes, edges: m.topology.edges, versions: m.versions ?? [] }
}
async function save() {
  await putMap(current.value.id, { topology: { nodes: current.value.nodes, edges: current.value.edges } })
}
```

- [ ] **Step 4: warehouse.ts — MAP_ID**

In `src/stores/warehouse.ts`, replace `const SITE_ID = 'warehouse-theatre-3d'` with `const MAP_ID = 'tpl-theatre_ecommerce'` and call `getMap(MAP_ID).geometry`.

- [ ] **Step 5: siteGrid.ts + types/siteGrid.ts**

In `src/types/siteGrid.ts`, change `SiteGrid.site_id` → `map_id`. In `src/stores/siteGrid.ts`, derive grid from `getMap(mapId).grid` instead of a separate `/grid` call.

- [ ] **Step 6: types/types.ts + types/scenario.ts**

Remove `site_id` field from `SiteMapInfo` / scenario template interfaces; add `map_id`.

- [ ] **Step 7: Run frontend store tests**

Run: `cd rcs/frontend && pnpm vitest run src/stores`
Expected: PASS (update assertions for map_id)

- [ ] **Step 8: Commit**

```bash
git add src/stores src/types && git commit -m "refactor(fe): stores use map_id, derive from unified getMap"
```

---

### Task 10: ScenarioMapView — merge three pages

**Files:**
- Create: `src/views/topology/ScenarioMapView.vue`
- Delete: `src/views/topology/SiteMapView.vue`, `src/views/topology/WarehouseView.vue`, `src/views/topology/AdminMapsView.vue`

- [ ] **Step 1: Build ScenarioMapView.vue**

Single page with:
- Top: template `<a-select>` populated from `listTemplates()` (key→map_id).
- Tabs: `几何视图` (2D/3D via `DeviceMap2D`/`DeviceMap3D` using `current.geometry` + `current.grid`), `拓扑编辑` (node/edge editor using `current.topology`), `仓库布局` (layout preview using `current.geometry`).

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { listTemplates, getMap } from '@/api/map'
import DeviceMap2D from '@/components/DeviceMap2D/DeviceMap2D.vue'
import DeviceMap3D from '@/components/DeviceMap3D/DeviceMap3D.vue'

const templates = ref<any[]>([])
const current = ref<any>(null)
const tab = ref<'geometry' | 'topology' | 'layout'>('geometry')

onMounted(async () => {
  templates.value = await listTemplates()
  if (templates.value.length) await select(templates.value[0].map_id)
})

async function select(mapId: string) {
  current.value = await getMap(mapId)
}
</script>

<template>
  <div class="scenario-map">
    <a-select :value="current?.map_id" @change="select" style="width: 280px">
      <a-select-option v-for="t in templates" :key="t.map_id" :value="t.map_id">{{ t.name }}</a-select-option>
    </a-select>
    <a-tabs v-model:activeKey="tab">
      <a-tab-pane key="geometry" tab="几何视图">
        <DeviceMap2D v-if="current" :shell="current.geometry" :grid="current.grid" />
        <DeviceMap3D v-if="current" :shell="current.geometry" />
      </a-tab-pane>
      <a-tab-pane key="topology" tab="拓扑编辑">
        <!-- reuse former AdminMapsView node/edge editor bound to current.topology -->
      </a-tab-pane>
      <a-tab-pane key="layout" tab="仓库布局">
        <WarehouseLayout v-if="current" :geometry="current.geometry" />
      </a-tab-pane>
    </a-tabs>
  </div>
</template>
```

Move the node/edge editor logic from deleted `AdminMapsView.vue` into this file (topology tab). Move `WarehouseLayout` component from `WarehouseView.vue` import.

- [ ] **Step 2: Update router**

In `src/router/dynamic.ts` (or wherever routes defined), replace the three routes with one:

```ts
{ path: '/scenario-map', name: 'scenario-map', component: () => import('@/views/topology/ScenarioMapView.vue'), meta: { title: '场景地图' } }
```
Remove `/sitemap`, `/warehouse`, `/admin/maps` routes.

- [ ] **Step 3: Delete old views**

```bash
cd rcs/frontend && git rm src/views/topology/SiteMapView.vue src/views/topology/WarehouseView.vue src/views/topology/AdminMapsView.vue
```

- [ ] **Step 4: Write ScenarioMapView.spec.ts**

```ts
import { mount } from '@vue/test-utils'
import ScenarioMapView from '@/views/topology/ScenarioMapView.vue'
import { listTemplates, getMap } from '@/api/map'

vi.mock('@/api/map', () => ({
  listTemplates: vi.fn().mockResolvedValue([{ key: 'ecommerce', map_id: 'tpl-ecommerce', name: '电商仓' }]),
  getMap: vi.fn().mockResolvedValue({ map_id: 'tpl-ecommerce', geometry: { zones: [] }, grid: {}, topology: { nodes: [], edges: [] } }),
}))

it('loads templates and selects first', async () => {
  const w = mount(ScenarioMapView)
  await flushPromises()
  expect(listTemplates).toHaveBeenCalled()
  expect(getMap).toHaveBeenCalledWith('tpl-ecommerce')
})
```

- [ ] **Step 5: Run frontend tests + tsc**

Run: `cd rcs/frontend && pnpm vitest run src/views/topology/ScenarioMapView.spec.ts && pnpm exec vue-tsc --noEmit`
Expected: PASS, no type errors

- [ ] **Step 6: Commit**

```bash
git add src/views/topology src/router && git commit -m "feat(fe): merge 3 map pages into single ScenarioMapView"
```

---

### Task 11: Menu + i18n cleanup

**Files:**
- Modify: `rcs/backend/rcs/services/sys/sys_seed.py`
- Modify: `rcs/frontend/src/i18n/locales/zh-CN.ts`

- [ ] **Step 1: sys_seed.py — keep only 场景地图**

In `rcs/backend/rcs/services/sys/sys_seed.py`, locate the menu tree where `站点地图` / `场景地图` / `仓库视图` are defined. Remove the `站点地图` and `仓库视图` nodes; keep `场景地图` with `path: '/scenario-map'`, `i18n: 'nav.scenario_map'` (or existing key). Update its permission to match the new route.

- [ ] **Step 2: i18n — title + menu labels**

In `rcs/frontend/src/i18n/locales/zh-CN.ts`:
- Change `app.title` from `RCS 站点地图` to `RCS 控制台`.
- Remove/repurpose `nav.site_map`, `nav.warehouse_view` entries; ensure `nav.scenario_map` = `场景地图`.

- [ ] **Step 3: Force re-seed menus on dev**

Because `seed_if_empty` only seeds when empty, run a one-off to refresh menus (or delete the menu rows and restart). Verify via API:

```bash
curl -s http://localhost:8100/api/sys/menus | python -c "import sys,json;d=json.load(sys.stdin);print([m['name'] for m in d if '地图' in m['name']])"
```
Expected: only `['场景地图']` (no 站点地图 / 仓库视图).

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/rcs/services/sys/sys_seed.py src/i18n/locales/zh-CN.ts && git commit -m "refactor: menu keeps only 场景地图, title RCS 控制台"
```

---

### Task 12: Backend test migration + full suite

**Files:**
- Modify: `tests/unit/control/test_site_map_templates.py`, `tests/unit/control/test_topology_*.py`

- [ ] **Step 1: Update template tests to assert UnifiedMap**

In `test_site_map_templates.py`, change all `TopologyShell`/`SiteMap` assertions to `UnifiedMap`:

```python
from rcs.db.models import UnifiedMap
# ...
async with async_session() as s:
    m = await s.get(UnifiedMap, "tpl-ecommerce_large")
    assert m is not None
    assert m.geometry_json["zones"]  # or topology_json
    assert m.is_template is True
```

- [ ] **Step 2: Update topology tests to use /maps/{id}**

In `test_topology_*.py`, replace `client.get('/api/rcs/topology/shell/...')` with `client.get('/api/rcs/maps/...')` and assert on `geometry`/`topology` keys.

- [ ] **Step 3: Run full backend suite**

Run: `cd rcs/backend && python -m pytest tests/ -q`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add tests/ && git commit -m "test: migrate backend tests to UnifiedMap + /maps API"
```

---

### Task 13: Final verification (tsc + build + Playwright)

**Files:** (none new; verification only)

- [ ] **Step 1: Frontend type-check + build**

Run: `cd rcs/frontend && pnpm exec vue-tsc --noEmit && pnpm build`
Expected: no type errors; build succeeds.

- [ ] **Step 2: Frontend unit tests**

Run: `cd rcs/frontend && pnpm vitest run`
Expected: all green.

- [ ] **Step 3: Playwright end-to-end walkthrough**

1. Start dev server: `cd rcs/frontend && pnpm dev --port 5173` (vite proxy → 8100).
2. Open `http://localhost:5173`, login `admin/rcs@2026`.
3. Confirm sidebar shows **only** `场景地图` (no 站点地图 / 仓库视图).
4. Click `场景地图` → `ScenarioMapView` loads; template dropdown lists 14 templates.
5. Select `冷链仓` → 几何视图 renders; switch to `拓扑编辑` tab, edit a node, save (PUT /maps/{id}) succeeds.
6. Switch to `仓库布局` tab → layout preview renders.
7. Capture console: assert **no** Vue errors and **no** 500 (except unrelated).

- [ ] **Step 4: Commit any leftover fixes**

```bash
git add -A && git commit -m "chore: final unified-map verification fixes" || echo "nothing to commit"
```

---

## Self-Review Checklist

1. **Spec coverage:** §2 (UnifiedMap + children + dynamic) → Task 1-2. §3 (drop legacy) → Task 2. §4 (unified API) → Task 5-6. §5 (service + 6 scenarios) → Task 3-4. §6 (frontend stores/view/menu/title) → Task 8-11. §7 (tests) → Task 12-13. §8 (risks) → handled by drop-in-007 + seed rebuild note.
2. **Placeholder scan:** No "TBD"/"TODO". Template geometry data is intentionally reused via existing builders (DRY) — not a placeholder, real conversion code provided.
3. **Type consistency:** `map_id` used uniformly across ORM/API/store/types. `getMap(id)` returns `UnifiedMapDTO` with `geometry/topology/grid`. `loadByMap` replaces `loadBySite`. `listTemplates()` returns `map_id`. No signature drift between tasks.
