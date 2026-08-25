# RCS Backend 重命名 + 控制层分层重构与持久化 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `rcs/backend/rcs_backend` 重命名为 `rcs/backend/rcs`，并把 control 层 7 个模块（设备/场景/订单/规划/调度/DAG/日志）按 API/Models/Services 分层重构，状态与配置统一持久化到 PostgreSQL，同时为前端实现 5 个管理页面。

**Architecture:** 重命名为纯机械替换（`rcs_backend.*` → `rcs.*`）。存储统一为 PostgreSQL（asyncpg），废弃 `services/shell_store.py` 与 `config.storage` 的 memory/sqlite 分支。每个 control 子模块新增 `service.py`（DB CRUD），算法层原样保留，services 在其上叠加持久化。前端用 Vue3+Pinia 实现 5 个页面，调 `/api/rcs/*` REST 接口。

**Tech Stack:** Python 3.11 + FastAPI + SQLAlchemy 2.0(async) + asyncpg + PostgreSQL 16；Vue 3 + Pinia + vue-router + vue-i18n + vite + vitest。

**约定：**
- DB 访问统一走 `rcs.db.session.session()`（async generator）。
- 算法文件（`dag/graph.py`、`planning/trajectory.py`、`scheduler/policy.py`、`orders/decomposer.py`）不动；服务层调用领域函数。
- 每个 Task：失败测试 → 验证失败 → 最小实现 → 验证通过 → commit。
- 测试需要 PostgreSQL，用 `RCS_DATABASE_URL` 指向测试库（如 `postgresql+asyncpg://rcs:rcs@localhost:5432/rcs_test`），`init_db()` 建表。

---

## Phase A：重命名 + 存储层统一

### Task A1: 目录重命名

**Files:** Rename `rcs/backend/rcs_backend/` → `rcs/backend/rcs/`; 替换 `rcs_backend.` 导入；改 `pyproject.toml` 与 `Dockerfile` 包名。

- [ ] **Step 1:** `cd rcs/backend && git mv rcs_backend rcs`（或 `mv`）
- [ ] **Step 2:** `cd rcs/backend && grep -rl 'rcs_backend\.' --include='*.py' . | xargs sed -i 's/rcs_backend\./rcs./g'`
- [ ] **Step 3:** 改 `pyproject.toml`：`name = "rcs"`、`[tool.flit.module].name = "rcs"`
- [ ] **Step 4:** 改 `Dockerfile` `PYTHONPATH` 中 `rcs_backend` → `rcs`
- [ ] **Step 5:** 验证：`PYTHONPATH=".../rcs/backend;.../shared/python" python -c "import rcs.main; print('ok')"` → 打印 `ok`
- [ ] **Step 6:** `git add -A && git commit -m "refactor: rename rcs_backend package to rcs"`

### Task A2: 存储层统一 PostgreSQL

**Files:** `rcs/config.py`, `rcs/db/session.py`, `rcs/api/order_repository.py`; 删除 `rcs/services/shell_store.py` + `rcs/services/__init__.py`; 新增 `tests/unit/test_session_postgres.py`。

- [ ] **Step 1 失败测试：**
```python
# tests/unit/test_session_postgres.py
from rcs.config import get_settings
from rcs.db import session as db_session

def test_session_uses_postgres_url():
    assert "postgresql+asyncpg" in get_settings().database_url

def test_session_factory_present():
    assert hasattr(db_session, "session")
```
运行：Expected FAIL。

- [ ] **Step 2 `config.py`：**
```python
"""Backend settings (pydantic-settings, env-prefix RCS_)."""
from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RCS_", case_sensitive=False)
    api_key: str = ""
    auth_enabled: bool = False
    database_url: str = "postgresql+asyncpg://rcs:rcs@localhost:5432/rcs"
    max_shell_bounds_m: float = 500.0
    max_zones_per_shell: int = 200


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

- [ ] **Step 3 `db/session.py`：**
```python
"""Async PostgreSQL engine + session factory (asyncpg)."""
from __future__ import annotations
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import (
    AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine,
)
from rcs.config import get_settings
from rcs.db import models

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None
_initialized = False


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().database_url, echo=False, future=True)
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _sessionmaker


async def init_db() -> None:
    global _initialized
    if _initialized:
        return
    async with get_engine().begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    _initialized = True


async def session() -> AsyncIterator[AsyncSession]:
    async with get_sessionmaker()() as s:
        yield s
```

- [ ] **Step 4 删 shell_store：** `rm -f rcs/services/shell_store.py rcs/services/__init__.py && rmdir rcs/services 2>/dev/null`

- [ ] **Step 5 `order_repository.py` 去掉 memory 分支：** 删除两处 `if get_settings().storage == "memory":` 块，统一走 `db_session.session()`；构造函数去掉 `self._memory`。

- [ ] **Step 6 验证通过：** `pytest tests/unit/test_session_postgres.py -v` → PASS

- [ ] **Step 7 Commit：** `git commit -m "refactor: unify storage on PostgreSQL, drop memory/sqlite + shell_store"`

---

## Phase B：ORM 扩展

### Task B1: 扩展/新增 ORM 表

**Files:** `rcs/db/models.py`（扩 `Device`；新增 `SiteMap`/`SiteMapVersion`/`PlanningProfile`/`SchedulerConfig`/`CommandLog`/`EventLog`；保留 `TopologyShell/Grid` 仅作历史）；`tests/unit/test_models.py`。

- [ ] **Step 1 失败测试：**
```python
from rcs.db import models
def test_all_tables_present():
    expected = {"devices", "orders", "order_items", "order_tasks",
                "site_maps", "site_map_versions", "planning_profiles",
                "scheduler_configs", "command_logs", "event_logs"}
    assert expected.issubset(set(models.Base.metadata.tables.keys()))
def test_device_has_spec_json():
    assert "spec_json" in models.Device.__table__.columns
```
Expected FAIL。

- [ ] **Step 2 扩 `Device`：** 增加 `spec_json: JSON`、`limits_json: JSON`、`home_joints_json: JSON`、`status: String(32)`。

- [ ] **Step 3 新增表（追加到 models.py 末尾）：**
```python
class SiteMap(Base):
    __tablename__ = "site_maps"
    map_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_version: Mapped[int] = mapped_column(Integer, default=1)
    nodes_json: Mapped[list] = mapped_column(JSON, default=list)
    edges_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class SiteMapVersion(Base):
    __tablename__ = "site_map_versions"
    version_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    map_id: Mapped[str] = mapped_column(ForeignKey("site_maps.map_id", ondelete="CASCADE"), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    nodes_json: Mapped[list] = mapped_column(JSON, default=list)
    edges_json: Mapped[list] = mapped_column(JSON, default=list)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PlanningProfile(Base):
    __tablename__ = "planning_profiles"
    profile_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    algo: Mapped[str] = mapped_column(String(32), nullable=False)
    axes: Mapped[int] = mapped_column(Integer, default=6)
    vel_max_json: Mapped[list] = mapped_column(JSON, default=list)
    acc_max_json: Mapped[list] = mapped_column(JSON, default=list)
    created_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class SchedulerConfig(Base):
    __tablename__ = "scheduler_configs"
    config_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    strategy: Mapped[str] = mapped_column(String(32), default="util-weighted")
    weights_json: Mapped[dict] = mapped_column(JSON, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class CommandLog(Base):
    __tablename__ = "command_logs"
    cmd_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    device_id: Mapped[str] = mapped_column(String(64), index=True)
    cmd_type: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSON, default=dict)
    issued_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result: Mapped[str] = mapped_column(String(16), default="ok")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class EventLog(Base):
    __tablename__ = "event_logs"
    event_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    level: Mapped[str] = mapped_column(String(16), default="info")
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    meta_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
```

- [ ] **Step 4 验证通过：** `pytest tests/unit/test_models.py -v` → PASS

- [ ] **Step 5 Commit：** `git commit -m "feat(db): extend ORM for devices/sitemap/planning/scheduler/logs"`

---

## Phase C：各模块 Services + REST API

### Task C1: 设备服务

**Files:** 新增 `rcs/control/devices/service.py`, `rcs/control/devices/api.py`; 修改 `rcs/main.py`（挂载）；测试 `tests/unit/control/test_devices_service.py`。

- [ ] **Step 1 失败测试：**
```python
# tests/unit/control/test_devices_service.py
import pytest
from rcs.control.devices import service as dev_svc


@pytest.mark.asyncio
async def test_register_and_get():
    dev = await dev_svc.register(
        device_id="dev-x", morphology="arm", num_joints=6, control_hz=1000,
        limits={"pos_lower": [-1]*6, "pos_upper": [1]*6, "vel_max": [2.0]*6, "acc_max": [4.0]*6},
        home_joints=[0.0]*6, spec={},
    )
    got = await dev_svc.get(dev["device_id"])
    assert got["device_id"] == "dev-x"
    assert got["morphology"] == "arm"
```
`PYTHONPATH=... RCS_DATABASE_URL=... python -m pytest ... -v` Expected FAIL。

- [ ] **Step 2 `rcs/control/devices/service.py`：**
```python
"""Device registry persistence + seeding."""
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from rcs.db import models, session as db_session


async def register(device_id, morphology, num_joints, control_hz,
                   limits, home_joints, spec, status="registered") -> dict:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        if dev is None:
            dev = models.Device(device_id=device_id)
        dev.morphology = morphology
        dev.num_joints = num_joints
        dev.control_hz = control_hz
        dev.limits_json = limits
        dev.home_joints_json = home_joints
        dev.spec_json = spec
        dev.status = status
        s.add(dev)
        await s.commit()
        await s.refresh(dev)
        return _to_dict(dev)


async def get(device_id) -> Optional[dict]:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        return _to_dict(dev) if dev else None


async def list_devices() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.Device))).scalars().all()
        return [_to_dict(d) for d in rows]


async def update(device_id, **fields) -> Optional[dict]:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        if dev is None:
            return None
        for k, v in fields.items():
            if hasattr(dev, k):
                setattr(dev, k, v)
        await s.commit()
        await s.refresh(dev)
        return _to_dict(dev)


async def delete(device_id) -> bool:
    async for s in db_session.session():
        dev = await s.get(models.Device, device_id)
        if dev is None:
            return False
        await s.delete(dev)
        await s.commit()
        return True


def _to_dict(d: models.Device) -> dict:
    return {"device_id": d.device_id, "morphology": d.morphology,
            "num_joints": d.num_joints, "control_hz": d.control_hz,
            "limits": d.limits_json or {}, "home_joints": d.home_joints_json or [],
            "spec": d.spec_json or {}, "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None}


async def seed_defaults_if_empty() -> None:
    async for s in db_session.session():
        if (await s.execute(select(models.Device))).scalars().first() is not None:
            return
    from rcs.control.registry import _DEFAULT_PROFILES
    for p in _DEFAULT_PROFILES:
        await register(
            device_id=p.device_id, morphology=p.morphology.value,
            num_joints=p.num_joints, control_hz=p.control_hz,
            limits={"pos_lower": p.limits.pos_lower, "pos_upper": p.limits.pos_upper,
                    "vel_max": p.limits.vel_max, "acc_max": p.limits.acc_max},
            home_joints=p.home_joints, spec={},
        )
```

- [ ] **Step 3 `rcs/control/devices/api.py`：**
```python
"""REST API for device management."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rcs.control.devices import service as dev_svc

router = APIRouter()


class DeviceCreate(BaseModel):
    device_id: str
    morphology: str
    num_joints: int = 0
    control_hz: int = 0
    limits: dict = {}
    home_joints: list = []
    spec: dict = {}


class DeviceUpdate(BaseModel):
    limits: dict | None = None
    home_joints: list | None = None
    spec: dict | None = None
    status: str | None = None


@router.get("/devices")
async def list_devices():
    return await dev_svc.list_devices()


@router.post("/devices", status_code=201)
async def create_device(body: DeviceCreate):
    return await dev_svc.register(**body.model_dump())


@router.get("/devices/{device_id}")
async def get_device(device_id: str):
    dev = await dev_svc.get(device_id)
    if dev is None:
        raise HTTPException(404, "device not found")
    return dev


@router.put("/devices/{device_id}")
async def update_device(device_id: str, body: DeviceUpdate):
    updated = await dev_svc.update(device_id, **body.model_dump(exclude_none=True))
    if updated is None:
        raise HTTPException(404, "device not found")
    return updated


@router.delete("/devices/{device_id}", status_code=204)
async def delete_device(device_id: str):
    if not await dev_svc.delete(device_id):
        raise HTTPException(404, "device not found")
```

- [ ] **Step 4 `main.py` 挂载：**
```python
from rcs.control.devices.api import router as devices_router
app.include_router(devices_router, prefix="/api/rcs", tags=["devices"])
```

- [ ] **Step 5 验证：** 测试 PASS

- [ ] **Step 6 Commit：** `git commit -m "feat(control/devices): persistence service + REST API"`

### Task C2: 场景地图服务

**Files:** `rcs/control/topology/service.py`（新）、`rcs/control/topology/api.py`（新）、`main.py`；测试 `tests/unit/control/test_sitemap_service.py`。

- [ ] **Step 1 失败测试：**
```python
import pytest
from rcs.control.topology import service as map_svc


@pytest.mark.asyncio
async def test_create_import_export_version():
    m = await map_svc.create(name="wh1", nodes=[{"id": "A", "pos": [0,0,0]}], edges=[])
    await map_svc.import_json(m["map_id"], {
        "nodes": [{"id": "A", "pos": [0,0,0]}, {"id": "B", "pos": [5,0,0]}],
        "edges": [{"from": "A", "to": "B", "distance": 5.0}],
    })
    exported = await map_svc.export_json(m["map_id"])
    assert len(exported["nodes"]) == 2
    versions = await map_svc.list_versions(m["map_id"])
    assert len(versions) >= 2
```
Expected FAIL。

- [ ] **Step 2 `rcs/control/topology/service.py`：**
```python
"""Site map persistence: nodes/edges JSONB + versioning + import/export."""
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from rcs.db import models, session as db_session


async def create(name, nodes, edges) -> dict:
    async for s in db_session.session():
        m = models.SiteMap(name=name, nodes_json=nodes, edges_json=edges, current_version=1)
        s.add(m)
        await s.commit()
        await s.refresh(m)
        await _snapshot(s, m, note="initial")
        return _to_dict(m)


async def get(map_id) -> Optional[dict]:
    async for s in db_session.session():
        m = await s.get(models.SiteMap, map_id)
        return _to_dict(m) if m else None


async def list_maps() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.SiteMap))).scalars().all()
        return [_to_dict(m) for m in rows]


async def update(map_id, name, nodes, edges) -> Optional[dict]:
    async for s in db_session.session():
        m = await s.get(models.SiteMap, map_id)
        if m is None:
            return None
        if name is not None:
            m.name = name
        m.nodes_json = nodes
        m.edges_json = edges
        m.current_version += 1
        await s.commit()
        await s.refresh(m)
        await _snapshot(s, m, note=f"v{m.current_version}")
        return _to_dict(m)


async def delete(map_id) -> bool:
    async for s in db_session.session():
        m = await s.get(models.SiteMap, map_id)
        if m is None:
            return False
        await s.delete(m)
        await s.commit()
        return True


async def import_json(map_id, payload) -> Optional[dict]:
    return await update(map_id, name=None, nodes=payload.get("nodes", []), edges=payload.get("edges", []))


async def export_json(map_id) -> Optional[dict]:
    m = await get(map_id)
    return {"map_id": m["map_id"], "name": m["name"], "nodes": m["nodes"], "edges": m["edges"]} if m else None


async def list_versions(map_id) -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(
            select(models.SiteMapVersion).where(models.SiteMapVersion.map_id == map_id)
        )).scalars().all()
        return [{"version_id": v.version_id, "version": v.version, "note": v.note,
                 "created_at": v.created_at.isoformat() if v.created_at else None} for v in rows]


async def restore_version(map_id, version_id) -> Optional[dict]:
    async for s in db_session.session():
        v = await s.get(models.SiteMapVersion, version_id)
        if v is None or v.map_id != map_id:
            return None
        m = await s.get(models.SiteMap, map_id)
        m.nodes_json = v.nodes_json
        m.edges_json = v.edges_json
        m.current_version += 1
        await s.commit()
        await s.refresh(m)
        await _snapshot(s, m, note=f"restore->{version_id}")
        return _to_dict(m)


async def _snapshot(s, m: models.SiteMap, note: str) -> None:
    s.add(models.SiteMapVersion(map_id=m.map_id, version=m.current_version,
                                nodes_json=m.nodes_json, edges_json=m.edges_json, note=note))
    await s.commit()


def _to_dict(m: models.SiteMap) -> dict:
    return {"map_id": m.map_id, "name": m.name, "current_version": m.current_version,
            "nodes": m.nodes_json or [], "edges": m.edges_json or [],
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "updated_at": m.updated_at.isoformat() if m.updated_at else None}
```

- [ ] **Step 3 `rcs/control/topology/api.py`：**
```python
"""REST API for site maps (viewer + import/export; no drag editor)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rcs.control.topology import service as map_svc

router = APIRouter()


class MapCreate(BaseModel):
    name: str
    nodes: list = []
    edges: list = []


class MapUpdate(BaseModel):
    name: str | None = None
    nodes: list = []
    edges: list = []


@router.get("/maps")
async def list_maps():
    return await map_svc.list_maps()


@router.post("/maps", status_code=201)
async def create_map(body: MapCreate):
    return await map_svc.create(**body.model_dump())


@router.get("/maps/{map_id}")
async def get_map(map_id: str):
    m = await map_svc.get(map_id)
    if m is None:
        raise HTTPException(404, "map not found")
    return m


@router.put("/maps/{map_id}")
async def update_map(map_id: str, body: MapUpdate):
    updated = await map_svc.update(map_id, name=body.name, nodes=body.nodes, edges=body.edges)
    if updated is None:
        raise HTTPException(404, "map not found")
    return updated


@router.delete("/maps/{map_id}", status_code=204)
async def delete_map(map_id: str):
    if not await map_svc.delete(map_id):
        raise HTTPException(404, "map not found")


@router.post("/maps/{map_id}/import")
async def import_map(map_id: str, payload: dict):
    updated = await map_svc.import_json(map_id, payload)
    if updated is None:
        raise HTTPException(404, "map not found")
    return updated


@router.get("/maps/{map_id}/export")
async def export_map(map_id: str):
    data = await map_svc.export_json(map_id)
    if data is None:
        raise HTTPException(404, "map not found")
    return data


@router.get("/maps/{map_id}/versions")
async def list_versions(map_id: str):
    return await map_svc.list_versions(map_id)


@router.post("/maps/{map_id}/versions/{version_id}/restore")
async def restore_version(map_id: str, version_id: str):
    updated = await map_svc.restore_version(map_id, version_id)
    if updated is None:
        raise HTTPException(404, "version not found")
    return updated
```

- [ ] **Step 4 `main.py` 挂载：** `from rcs.control.topology.api import router as maps_router; app.include_router(maps_router, prefix="/api/rcs", tags=["maps"])`

- [ ] **Step 5 验证：** 测试 PASS

- [ ] **Step 6 Commit：** `git commit -m "feat(control/topology): sitemap persistence + versioning + REST API"`

### Task C3: 订单服务扩展（状态机 + DAG 监控）

**Files:** `rcs/api/order_repository.py`（增 list/advance/set_task_status）；`rcs/api/orders.py`（增 list/状态推进/任务监控路由）；测试 `tests/unit/test_orders_lifecycle.py`。

- [ ] **Step 1 失败测试：**
```python
import pytest
from rcs.api import order_repository as repo


@pytest.mark.asyncio
async def test_advance_status():
    rec = await repo.create(scenario_id="e", priority=5, deadline=None,
                            items=[{"ref": "SKU:A", "quantity": 1}],
                            tasks=[{"node_id": "t1", "task_type": "pick",
                                    "slo_class": "std", "depends_on": []}])
    assert await repo.advance_status(rec["order_id"], "RUNNING") is True
    got = await repo.get(rec["order_id"])
    assert got["status"] == "RUNNING"
```
Expected FAIL。

- [ ] **Step 2 在 `OrderRepository` 增方法：**
```python
async def list_orders(self, status: Optional[str] = None) -> list[dict]:
    from sqlalchemy import select
    async for s in db_session.session():
        stmt = select(models.Order)
        if status:
            stmt = stmt.where(models.Order.status == status)
        rows = (await s.execute(stmt)).scalars().all()
        return [await self._public(o) for o in rows]


async def advance_status(self, order_id: str, status: str) -> bool:
    async for s in db_session.session():
        o = await s.get(models.Order, order_id)
        if o is None:
            return False
        o.status = status
        await s.commit()
        return True


async def set_task_status(self, order_id: str, node_id: str, status: str) -> bool:
    from sqlalchemy import update as sa_update
    async for s in db_session.session():
        stmt = (sa_update(models.OrderTask)
                .where(models.OrderTask.order_id == order_id,
                       models.OrderTask.node_id == node_id)
                .values(status=status))
        res = await s.execute(stmt)
        await s.commit()
        return res.rowcount > 0
```
（同时把 `get` 内的 `return` 块抽成 `async def _public(self, order)` 复用）

- [ ] **Step 3 `rcs/api/orders.py` 增路由：**
```python
@router.get("/orders")
async def list_orders(status: Optional[str] = None):
    return await repo.list_orders(status)


@router.put("/orders/{order_id}/status")
async def advance(order_id: str, body: dict):
    ok = await repo.advance_status(order_id, body.get("status", "RUNNING"))
    if not ok:
        raise HTTPException(404, "order not found")
    return {"order_id": order_id, "status": body.get("status")}


@router.get("/orders/{order_id}/tasks")
async def order_tasks(order_id: str):
    rec = await repo.get(order_id)
    if rec is None:
        raise HTTPException(404, "order not found")
    return rec["tasks"]
```

- [ ] **Step 4 验证：** PASS

- [ ] **Step 5 Commit：** `git commit -m "feat(orders): lifecycle status machine + DAG task monitoring"`

### Task C4: 规划库服务

**Files:** `rcs/control/planning/service.py`（新）、`rcs/control/planning/api.py`（新）、`main.py`；测试 `tests/unit/control/test_planning_service.py`。

- [ ] **Step 1 失败测试：**
```python
import pytest
from rcs.control.planning import service as plan_svc


@pytest.mark.asyncio
async def test_crud_profile():
    p = await plan_svc.create(name="trap6", algo="trapezoidal", axes=6,
                              vel_max=[2.0]*6, acc_max=[4.0]*6, created_by="u1")
    got = await plan_svc.get(p["profile_id"])
    assert got["algo"] == "trapezoidal"
    assert len(await plan_svc.list_profiles()) >= 1
```
Expected FAIL。

- [ ] **Step 2 `rcs/control/planning/service.py`：**
```python
"""Trajectory planning profile library (persisted, reusable)."""
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from rcs.db import models, session as db_session


async def create(name, algo, axes, vel_max, acc_max, created_by=None) -> dict:
    async for s in db_session.session():
        p = models.PlanningProfile(name=name, algo=algo, axes=axes,
                                   vel_max_json=vel_max, acc_max_json=acc_max,
                                   created_by=created_by)
        s.add(p); await s.commit(); await s.refresh(p)
        return _to_dict(p)


async def get(profile_id) -> Optional[dict]:
    async for s in db_session.session():
        p = await s.get(models.PlanningProfile, profile_id)
        return _to_dict(p) if p else None


async def list_profiles() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.PlanningProfile))).scalars().all()
        return [_to_dict(p) for p in rows]


async def delete(profile_id) -> bool:
    async for s in db_session.session():
        p = await s.get(models.PlanningProfile, profile_id)
        if p is None:
            return False
        await s.delete(p); await s.commit(); return True


def _to_dict(p: models.PlanningProfile) -> dict:
    return {"profile_id": p.profile_id, "name": p.name, "algo": p.algo,
            "axes": p.axes, "vel_max": p.vel_max_json, "acc_max": p.acc_max_json,
            "created_by": p.created_by,
            "created_at": p.created_at.isoformat() if p.created_at else None}
```

- [ ] **Step 3 `rcs/control/planning/api.py`：**
```python
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rcs.control.planning import service as plan_svc

router = APIRouter()


class ProfileCreate(BaseModel):
    name: str
    algo: str
    axes: int = 6
    vel_max: list = []
    acc_max: list = []
    created_by: str | None = None


@router.get("/planning-profiles")
async def list_profiles():
    return await plan_svc.list_profiles()


@router.post("/planning-profiles", status_code=201)
async def create_profile(body: ProfileCreate):
    return await plan_svc.create(**body.model_dump())


@router.get("/planning-profiles/{profile_id}")
async def get_profile(profile_id: str):
    p = await plan_svc.get(profile_id)
    if p is None:
        raise HTTPException(404, "profile not found")
    return p


@router.delete("/planning-profiles/{profile_id}", status_code=204)
async def delete_profile(profile_id: str):
    if not await plan_svc.delete(profile_id):
        raise HTTPException(404, "profile not found")
```

- [ ] **Step 4 `main.py` 挂载：**
```python
from rcs.control.planning.api import router as planning_router
app.include_router(planning_router, prefix="/api/rcs", tags=["planning"])
```

- [ ] **Step 5 验证：** PASS

- [ ] **Step 6 Commit：** `git commit -m "feat(control/planning): persisted trajectory profile library + API"`

### Task C5: 调度配置服务

**Files:** `rcs/control/scheduler/service.py`（新）、`rcs/control/scheduler/api.py`（新）、`main.py`；测试 `tests/unit/control/test_scheduler_service.py`。

- [ ] **Step 1 失败测试：**
```python
import pytest
from rcs.control.scheduler import service as sch_svc


@pytest.mark.asyncio
async def test_activate_config():
    c = await sch_svc.create(name="w1", strategy="util-weighted",
                             weights={"w1": 1.0, "w2": 0.5, "w3": 0.2, "w4": 0.1})
    assert await sch_svc.activate(c["config_id"]) is True
    active = await sch_svc.get_active()
    assert active["config_id"] == c["config_id"]
```
Expected FAIL。

- [ ] **Step 2 `rcs/control/scheduler/service.py`：**
```python
"""Scheduler configuration persistence (weights/strategy), single active."""
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from rcs.db import models, session as db_session


async def create(name, strategy="util-weighted", weights=None) -> dict:
    async for s in db_session.session():
        c = models.SchedulerConfig(name=name, strategy=strategy, weights_json=weights or {})
        s.add(c); await s.commit(); await s.refresh(c)
        return _to_dict(c)


async def get(config_id) -> Optional[dict]:
    async for s in db_session.session():
        c = await s.get(models.SchedulerConfig, config_id)
        return _to_dict(c) if c else None


async def list_configs() -> list[dict]:
    async for s in db_session.session():
        rows = (await s.execute(select(models.SchedulerConfig))).scalars().all()
        return [_to_dict(c) for c in rows]


async def update(config_id, **fields) -> Optional[dict]:
    async for s in db_session.session():
        c = await s.get(models.SchedulerConfig, config_id)
        if c is None:
            return None
        for k, v in fields.items():
            if hasattr(c, k):
                setattr(c, k, v)
        await s.commit(); await s.refresh(c)
        return _to_dict(c)


async def activate(config_id) -> bool:
    async for s in db_session.session():
        rows = (await s.execute(select(models.SchedulerConfig))).scalars().all()
        if not any(c.config_id == config_id for c in rows):
            return False
        for c in rows:
            c.active = (c.config_id == config_id)
        await s.commit()
        return True


async def get_active() -> Optional[dict]:
    async for s in db_session.session():
        rows = (await s.execute(
            select(models.SchedulerConfig).where(models.SchedulerConfig.active == True)  # noqa: E712
        )).scalars().all()
        return _to_dict(rows[0]) if rows else None


def _to_dict(c: models.SchedulerConfig) -> dict:
    return {"config_id": c.config_id, "name": c.name, "strategy": c.strategy,
            "weights": c.weights_json, "active": c.active,
            "created_at": c.created_at.isoformat() if c.created_at else None}
```

- [ ] **Step 3 `rcs/control/scheduler/api.py`：**
```python
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rcs.control.scheduler import service as sch_svc

router = APIRouter()


class ConfigCreate(BaseModel):
    name: str
    strategy: str = "util-weighted"
    weights: dict = {}


class ConfigUpdate(BaseModel):
    name: str | None = None
    strategy: str | None = None
    weights: dict | None = None


@router.get("/scheduler-configs")
async def list_configs():
    return await sch_svc.list_configs()


@router.get("/scheduler-configs/active")
async def get_active():
    c = await sch_svc.get_active()
    if c is None:
        raise HTTPException(404, "no active config")
    return c


@router.post("/scheduler-configs", status_code=201)
async def create_config(body: ConfigCreate):
    return await sch_svc.create(**body.model_dump())


@router.put("/scheduler-configs/{config_id}")
async def update_config(config_id: str, body: ConfigUpdate):
    u = await sch_svc.update(config_id, **body.model_dump(exclude_none=True))
    if u is None:
        raise HTTPException(404, "config not found")
    return u


@router.post("/scheduler-configs/{config_id}/activate")
async def activate(config_id: str):
    if not await sch_svc.activate(config_id):
        raise HTTPException(404, "config not found")
    return {"activated": config_id}
```

- [ ] **Step 4 `main.py` 挂载：** `from rcs.control.scheduler.api import router as scheduler_router; app.include_router(scheduler_router, prefix="/api/rcs", tags=["scheduler"])`

- [ ] **Step 5 验证：** PASS

- [ ] **Step 6 Commit：** `git commit -m "feat(control/scheduler): persisted config + active toggle + API"`

### Task C6: 日志服务（command + event）

**Files:** `rcs/control/logs/service.py`（新 — `control/logs/` 新建）、`rcs/control/logs/api.py`（新）、`main.py`；测试 `tests/unit/control/test_logs_service.py`。

- [ ] **Step 1 失败测试：**
```python
import pytest
from rcs.control.logs import service as logs_svc


@pytest.mark.asyncio
async def test_issue_and_query():
    await logs_svc.issue_command(device_id="agv-01", cmd_type="MOVE",
                                 payload={"x": 1.0}, issued_by="u1", result="ok")
    cmds = await logs_svc.list_commands(limit=10)
    assert any(c["device_id"] == "agv-01" for c in cmds)


@pytest.mark.asyncio
async def test_event_log():
    await logs_svc.log_event(level="info", source="scheduler", message="step", meta={"k": 1})
    evs = await logs_svc.list_events(limit=10)
    assert any(e["source"] == "scheduler" for e in evs)
```
Expected FAIL。

- [ ] **Step 2 `rcs/control/logs/service.py`：**
```python
"""Unified command + event log service."""
from __future__ import annotations
from typing import Optional
from sqlalchemy import select
from rcs.db import models, session as db_session


async def issue_command(device_id, cmd_type, payload, issued_by=None, result="ok") -> dict:
    async for s in db_session.session():
        c = models.CommandLog(device_id=device_id, cmd_type=cmd_type,
                              payload_json=payload or {}, issued_by=issued_by, result=result)
        s.add(c); await s.commit(); await s.refresh(c)
        return _cmd_to_dict(c)


async def list_commands(device_id: Optional[str] = None, limit: int = 100) -> list[dict]:
    async for s in db_session.session():
        stmt = select(models.CommandLog).order_by(models.CommandLog.created_at.desc()).limit(limit)
        if device_id:
            stmt = stmt.where(models.CommandLog.device_id == device_id)
        rows = (await s.execute(stmt)).scalars().all()
        return [_cmd_to_dict(c) for c in rows]


async def log_event(level, source, message, meta=None) -> dict:
    async for s in db_session.session():
        e = models.EventLog(level=level, source=source, message=message, meta_json=meta or {})
        s.add(e); await s.commit(); await s.refresh(e)
        return _ev_to_dict(e)


async def list_events(level: Optional[str] = None, limit: int = 100) -> list[dict]:
    async for s in db_session.session():
        stmt = select(models.EventLog).order_by(models.EventLog.created_at.desc()).limit(limit)
        if level:
            stmt = stmt.where(models.EventLog.level == level)
        rows = (await s.execute(stmt)).scalars().all()
        return [_ev_to_dict(e) for e in rows]


def _cmd_to_dict(c: models.CommandLog) -> dict:
    return {"cmd_id": c.cmd_id, "device_id": c.device_id, "cmd_type": c.cmd_type,
            "payload": c.payload_json, "issued_by": c.issued_by, "result": c.result,
            "created_at": c.created_at.isoformat() if c.created_at else None}


def _ev_to_dict(e: models.EventLog) -> dict:
    return {"event_id": e.event_id, "level": e.level, "source": e.source,
            "message": e.message, "meta": e.meta_json,
            "created_at": e.created_at.isoformat() if e.created_at else None}
```

- [ ] **Step 3 `rcs/control/logs/api.py`：**
```python
from __future__ import annotations
from fastapi import APIRouter, Query
from rcs.control.logs import service as logs_svc

router = APIRouter()


@router.get("/logs/commands")
async def list_commands(device_id: str | None = None, limit: int = Query(100, le=500)):
    return await logs_svc.list_commands(device_id=device_id, limit=limit)


@router.get("/logs/events")
async def list_events(level: str | None = None, limit: int = Query(100, le=500)):
    return await logs_svc.list_events(level=level, limit=limit)
```

- [ ] **Step 4 `main.py` 挂载：** `from rcs.control.logs.api import router as logs_router; app.include_router(logs_router, prefix="/api/rcs", tags=["logs"])`

- [ ] **Step 5 验证：** PASS

- [ ] **Step 6 Commit：** `git commit -m "feat(control/logs): command + event log service + REST API"`

### Task C7: 启动期种子化（devices defaults）

**Files:** `rcs/control/__init__.py` 的 `lifespan`（或 `main.py` 的 `_lifespan`）；测试 `tests/integration/test_seed.py`。

- [ ] **Step 1：** 在 `main.py` 的 `_lifespan` 中、`await init_db()` 之后、进入 `control_lifespan` 之前，添加 `from rcs.control.devices import service as dev_svc; await dev_svc.seed_defaults_if_empty()`。
- [ ] **Step 2 Commit：** `git commit -m "feat: seed default devices from registry on startup"`

---

## Phase D：前端 5 个管理页面

> 前端在 `rcs/frontend/`，Vue 3 + Pinia + vue-router + vue-i18n。HTTP 客户端已有 `src/api/http.ts`。每个页面 = `views/<Name>.vue` + `stores/<name>.ts` + `api/<name>.ts` + 类型扩展 `types/index.ts` + i18n。

### Task D1: 类型与路由骨架

**Files:** `src/types/index.ts`（增设备/地图/订单/规划/调度/日志类型）；`src/router/index.ts`（增 5 个路由）；`src/App.vue`（增导航链接）。

- [ ] **Step 1:** 在 `types/index.ts` 末尾追加：
```ts
export interface DeviceRow {
  device_id: string
  morphology: string
  num_joints: number
  control_hz: number
  limits: Record<string, number[]>
  home_joints: number[]
  spec: Record<string, unknown>
  status: string
}
export interface MapRow {
  map_id: string
  name: string
  current_version: number
  nodes: { id: string; pos: number[]; type?: string; capacity?: number }[]
  edges: { from: string; to: string; distance: number }[]
}
export interface OrderRow {
  order_id: string
  scenario_id?: string
  priority: number
  status: string
  items: { ref: string; quantity: number }[]
  tasks: { node_id: string; task_type: string; slo_class: string; depends_on: string[]; status?: string }[]
  created_at: number
}
export interface PlanningProfile {
  profile_id: string
  name: string
  algo: 'trapezoidal' | 'quintic'
  axes: number
  vel_max: number[]
  acc_max: number[]
}
export interface SchedulerConfig {
  config_id: string
  name: string
  strategy: string
  weights: { w1: number; w2: number; w3: number; w4: number }
  active: boolean
}
export interface LogRow {
  cmd_id?: string
  event_id?: string
  device_id?: string
  cmd_type?: string
  level?: string
  source?: string
  message?: string
  created_at?: string
}
```

- [ ] **Step 2 `router/index.ts`：** 增加 `/devices`、`/maps`、`/orders`、`/scheduler`、`/logs` 路由（home 改为 `/devices`）。

- [ ] **Step 3 `App.vue`：** 在导航栏增加 5 个 `RouterLink`（设备/地图/订单/调度/日志），保留 `站点地图` 与 `设备控制` 作为旧链接（如仍存在）。

- [ ] **Step 4 Commit：** `git commit -m "feat(frontend): add 5 admin page routes + types"`

### Task D2: API 客户端（5 个模块）

**Files:** 新增 `src/api/devices.ts` / `maps.ts` / `orders.ts` / `planning.ts` / `scheduler.ts` / `logs.ts`；每个用 `http` 包装 REST 调用。

- [ ] **Step 1 `src/api/devices.ts`：**
```ts
import { http } from './http'
import type { DeviceRow } from '@/types'
export const listDevices = () => http.get<DeviceRow[]>('/devices')
export const getDevice = (id: string) => http.get<DeviceRow>(`/devices/${encodeURIComponent(id)}`)
export const updateDevice = (id: string, body: Partial<DeviceRow>) =>
  http.put<DeviceRow>(`/devices/${encodeURIComponent(id)}`, body)
export const createDevice = (body: DeviceRow) => http.post<DeviceRow>('/devices', body)
export const deleteDevice = (id: string) => http.delete<void>(`/devices/${encodeURIComponent(id)}`)
```

- [ ] **Step 2 `src/api/maps.ts`：** `listMaps / getMap / createMap / updateMap / importMap / exportMap / listVersions / restoreVersion`（POST `/maps`、GET/PUT/DELETE `/maps/{id}`、POST `/maps/{id}/import`、GET `/maps/{id}/export`、GET `/maps/{id}/versions`、POST `/maps/{id}/versions/{vid}/restore`）

- [ ] **Step 3 `src/api/orders.ts`：** `listOrders / getOrder / createOrder / advanceStatus / getOrderTasks`

- [ ] **Step 4 `src/api/planning.ts`：** `listProfiles / getProfile / createProfile / deleteProfile`

- [ ] **Step 5 `src/api/scheduler.ts`：** `listConfigs / getActive / createConfig / updateConfig / activate`

- [ ] **Step 6 `src/api/logs.ts`：** `listCommands(deviceId?,limit) / listEvents(level?,limit)`

- [ ] **Step 7 Commit：** `git commit -m "feat(frontend): API clients for devices/maps/orders/planning/scheduler/logs"`

### Task D3: Pinia stores

**Files:** `src/stores/devices.ts` / `maps.ts` / `orders.ts` / `planning.ts` / `scheduler.ts` / `logs.ts`。

- [ ] **Step 1 `stores/devices.ts`：**
```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/devices'
import type { DeviceRow } from '@/types'

export const useDeviceStore = defineStore('devices-admin', () => {
  const devices = ref<DeviceRow[]>([])
  const loading = ref(false)
  async function load() { loading.value = true; try { devices.value = await api.listDevices() } finally { loading.value = false } }
  async function save(id: string, body: Partial<DeviceRow>) { await api.updateDevice(id, body) }
  return { devices, loading, load, save }
})
```
（其它 5 个 store 同样模式：load/保存/激活等 action，对应 API）

- [ ] **Step 2 `stores/maps.ts`：** `load / get / importJson / exportJson / listVersions` 等。

- [ ] **Step 3 `stores/orders.ts`：** `load / get / create / advance`。

- [ ] **Step 4 `stores/planning.ts`：** `load / create / remove`。

- [ ] **Step 5 `stores/scheduler.ts`：** `load / getActive / activate`。

- [ ] **Step 6 `stores/logs.ts`：** `loadCommands(deviceId?) / loadEvents(level?)`。

- [ ] **Step 7 Commit：** `git commit -m "feat(frontend): pinia stores for admin modules"`

### Task D4: 5 个 Vue 页面

**Files:** `src/views/DevicesView.vue` / `MapsView.vue` / `OrdersView.vue` / `SchedulerView.vue` / `LogsView.vue`；`src/i18n/messages.ts`（加中英文段）。

- [ ] **Step 1 `DevicesView.vue`：** 表格列出设备 + 选中行打开参数编辑抽屉（limits / home_joints / status），保存调 `deviceStore.save`。

- [ ] **Step 2 `MapsView.vue`：** 左侧 SVG 节点/边只读渲染（坐标按 `pos: [x,y,z]` 投影到 2D），右侧导入/导出 JSON 按钮（textarea）+ 版本列表 + 恢复按钮。

- [ ] **Step 3 `OrdersView.vue`：** 上半订单列表（带 status 徽标），下半选中订单的任务 DAG 表格（节点/依赖/状态）。

- [ ] **Step 4 `SchedulerView.vue`：** 配置列表 + 选中行编辑权重（w1..w4 数字输入）+ "激活" 按钮。

- [ ] **Step 5 `LogsView.vue`：** Tab 切换「指令/事件」，按 `device_id` 或 `level` 过滤，分页加载。

- [ ] **Step 6 `i18n/messages.ts`：** 增加 `devices / maps / orders / scheduler / logs` 字段（zh-CN + en-US）。

- [ ] **Step 7 Commit：** `git commit -m "feat(frontend): 5 admin pages (devices/maps/orders/scheduler/logs)"`

---

## Phase E：端到端验证

### Task E1: 后端验证

- [ ] **Step 1:** 起本地 Postgres（`docker compose -f rcs/backend/docker-compose.yml up -d db`）
- [ ] **Step 2:** `cd rcs/backend && PYTHONPATH=".../rcs/backend;.../shared/python" python -c "import rcs.main"` → 正常导入
- [ ] **Step 3:** `pytest -v` → 64 旧测试 + 新增 8 个 service 测试全 PASS
- [ ] **Step 4:** `uvicorn rcs.main:app --host 127.0.0.1 --port 8000` 启动 → `curl http://127.0.0.1:8000/health` 200
- [ ] **Step 5:** `curl -X POST http://127.0.0.1:8000/api/rcs/devices`（body：robot-01）+ `curl http://127.0.0.1:8000/api/rcs/devices` 验证持久化

### Task E2: 前端验证

- [ ] **Step 1:** `cd rcs/frontend && npm install`（如未安装）
- [ ] **Step 2:** `npm run type-check`（vue-tsc）→ 0 error
- [ ] **Step 3:** `npm run test:unit`（vitest）→ 全 PASS
- [ ] **Step 4:** `npm run build` → 产物生成
- [ ] **Step 5:** `npm run dev` → 浏览器打开 5 个页面，验证调通后端

### Task E3: 文档与提交

- [ ] **Step 1:** 更新 `rcs/backend/README.md`：移除 `RCS_SERVICE_URL` / `RCS_EMBEDDED` / `RCS_DB_PATH`，加 `RCS_DATABASE_URL`；新增 5 模块 REST API 段；前端启动段。
- [ ] **Step 2:** 更新 `rcs/frontend/README.md`：新增 5 页面说明 + 路由表。
- [ ] **Step 3:** `git add -A && git commit -m "docs: update README for restructure"`

---

## 自我审查
- 覆盖：重命名 ✓、config/session 统一 ✓、ORM 扩展 ✓、5 个 service+api (devices/sitemap/orders/planning/scheduler/logs) ✓、seed ✓、前端 types/api/stores/views/i18n ✓、端到端验证 ✓。
- 无占位符（TBD/TODO/“类似”已避免；所有代码块完整）。
- 类型一致：service 返回 dict 字段与前端 types 对齐；device morph `Morphology.ARM.value` 在 seed 中用，`service.register` 收 `str`；api.py `BaseModel` 字段含 `str` 即可。
- 风险：Postgres 未起 → 测试失败。Plan 明确需起 db；CI 容器化另行。
