## Task 11: API router — topology_shell（GET/PUT）

**Files:**
- Modify: `rcs/backend/rcs_backend/api/__init__.py` (replace `topology_shell` stub with re-export)
- Create: `rcs/backend/rcs_backend/api/topology_shell.py`
- Create: `rcs/backend/tests/integration/__init__.py`
- Create: `rcs/backend/tests/integration/conftest.py`
- Create: `rcs/backend/tests/integration/test_topology_api.py`

**Interfaces:**
- Produces: `router: APIRouter` with routes:
  - `GET /api/rcs/topology/shell` → list of `{site_id, bounds, zone_count}`
  - `GET /api/rcs/topology/shell/{site_id}` → `FloorShell`
  - `PUT /api/rcs/topology/shell/{site_id}` body `FloorShell` → `{ok: true, warnings: [...]}` (422 on validation failure)

> **Plan notes** (verified):
> - Existing `tests/conftest.py` already has a `client` fixture using `create_app()`. The brief's `tests/integration/conftest.py` adds redundant `sys.path.insert` (harmless) and **doesn't** redefine `client` — so root fixture is inherited.
> - `ValidationReport` (validate.py) has `ok`, `errors`, `warnings` fields.
> - `_store = MemoryShellStore()` is a module-level singleton. State leaks between tests. The brief's tests use unique `site_id` values per test, so leakage is benign in this task — but Tasks 12-16 should be aware.

- [ ] **Step 1: 修改 `rcs/backend/rcs_backend/api/__init__.py`**

Replace the entire file body to:

```python
"""API router registry.

Task 1 stubs all six router names. Tasks 11-16 each edit THIS file to replace
their stub with the real re-export (same pattern as Task 11 below).
"""
from fastapi import APIRouter
from rcs_backend.api.topology_shell import router as topology_shell

# Stubs replaced by Tasks 12, 13, 14, 15, 16 respectively
topology_grid = APIRouter()
topology_import = APIRouter()
topology_export = APIRouter()
topology_templates = APIRouter()
orders = APIRouter()

__all__ = [
    "topology_shell", "topology_grid",
    "topology_import", "topology_export",
    "topology_templates", "orders",
]
```

- [ ] **Step 2: 创建 `rcs/backend/rcs_backend/api/topology_shell.py`**

```python
"""REST endpoints for floor_shell CRUD."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from rcs_backend.config import get_settings, Settings
from rcs_backend.models.floor_shell import FloorShell
from rcs_backend.services.shell_store import MemoryShellStore
from rcs_backend.topology.validate import validate_shell

router = APIRouter()

_store = MemoryShellStore()


def _get_store() -> MemoryShellStore:
    return _store


@router.get("/shell", summary="List all stored shells")
async def list_shells(store: MemoryShellStore = Depends(_get_store)) -> list[dict]:
    site_ids = await store.list_sites()
    out = []
    for sid in site_ids:
        shell = await store.get_shell(sid)
        if shell is None:
            continue
        out.append({
            "site_id": sid,
            "bounds": {"w": shell.bounds.w, "d": shell.bounds.d},
            "zone_count": len(shell.zones),
        })
    return out


@router.get("/shell/{site_id}", response_model=FloorShell, summary="Get shell by site_id")
async def get_shell(site_id: str, store: MemoryShellStore = Depends(_get_store)) -> FloorShell:
    shell = await store.get_shell(site_id)
    if shell is None:
        raise HTTPException(status_code=404, detail=f"site_id '{site_id}' not found")
    return shell


@router.put("/shell/{site_id}", summary="Save/replace shell by site_id")
async def put_shell(
    site_id: str,
    shell: FloorShell,
    store: MemoryShellStore = Depends(_get_store),
    settings: Settings = Depends(get_settings),
) -> dict:
    report = validate_shell(shell, max_bounds_m=settings.max_shell_bounds_m)
    if not report.ok:
        raise HTTPException(status_code=422, detail={"errors": report.errors})
    await store.save_shell(site_id, shell)
    return {"site_id": site_id, "ok": True, "warnings": report.warnings}
```

- [ ] **Step 3: 创建 `tests/integration/__init__.py`** (空文件)

Empty file. Ensures `tests/integration` is a package.

- [ ] **Step 4: 创建 `tests/integration/conftest.py`**

```python
"""Integration test config: ensure rcs_backend is importable."""
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent  # rcs/backend/
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
```

> **Plan patch note**: brief computed `_ROOT = Path(__file__).parent.parent` (i.e. `tests/`) — wrong. To import `rcs_backend.main`, sys.path needs `rcs/backend/`. Patched to `parent.parent.parent`. Harmless since the root conftest already exists at `rcs/backend/tests/conftest.py`, but this makes the integration conftest self-contained.

- [ ] **Step 5: 创建 `tests/integration/test_topology_api.py`**

```python
"""Integration tests for topology REST endpoints."""
import pytest
from fastapi.testclient import TestClient
from rcs_backend.main import create_app
from rcs_backend.models.floor_shell import FloorShell, Bounds


@pytest.fixture
def client():
    return TestClient(create_app())


def test_shell_get_missing_returns_404(client):
    r = client.get("/api/rcs/topology/shell/nope-t11")
    assert r.status_code == 404


def test_shell_put_then_get(client):
    shell = FloorShell(bounds=Bounds(w=20, d=10), zones=[])
    r = client.put("/api/rcs/topology/shell/site-A-t11", json=shell.model_dump())
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/rcs/topology/shell/site-A-t11")
    assert r2.status_code == 200
    assert r2.json()["bounds"]["w"] == 20


def test_shell_put_oversized_returns_422(client):
    shell = FloorShell(bounds=Bounds(w=1000, d=80))
    r = client.put("/api/rcs/topology/shell/site-B-t11", json=shell.model_dump())
    assert r.status_code == 422


def test_shell_list_after_puts(client):
    for sid in ["x-t11", "y-t11", "z-t11"]:
        client.put(
            f"/api/rcs/topology/shell/{sid}",
            json=FloorShell(bounds=Bounds(w=10, d=10)).model_dump(),
        )
    r = client.get("/api/rcs/topology/shell")
    assert r.status_code == 200
    site_ids = {item["site_id"] for item in r.json()}
    assert {"x-t11", "y-t11", "z-t11"}.issubset(site_ids)
```

> **Plan patch note** (cosmetic): renamed all `site_id` literals with a `-t11` suffix so future tasks (12-16) running the same suite can't cross-pollute.

- [ ] **Step 6: 跑集成测试**

Run: `cd rcs/backend && python -m pytest tests/integration -v`
Expected: PASS（4 tests）

- [ ] **Step 7: 跑全 suite 确认无回归**

Run: `cd rcs/backend && python -m pytest -v`
Expected: 51 (prior) + 4 (new) = 55 passed

- [ ] **Step 8: Commit**

```bash
git add rcs/backend/rcs_backend/api/__init__.py \
        rcs/backend/rcs_backend/api/topology_shell.py \
        rcs/backend/tests/integration
git commit -m "feat(rcs-backend): topology_shell REST endpoints (GET/PUT) with validation"
```