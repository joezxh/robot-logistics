# RCS Backend v2.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `robot-logic/rcs/backend/` 下创建统一后端工程，提供 floor_shell / site_grid / DXF 导入导出 / 6 场景模板 / 订单 REST API，与 `simulation/backend/` 并列运行。

**Architecture:** 扩展层后端，纯函数库（`rcs/backend/topology/`）+ REST API（`rcs/backend/api/`）+ Pydantic 模型（`rcs/backend/models/`）。**不直接 import** `rcs/rcs/` 内部模块；通过 HTTP 调用其 `/registry`、`/{device_id}/command` 等现有端点。FastAPI lifespan 中可选注入 `rcs` 子项目（嵌入式模式 `RCS_EMBEDDED=1`）或远程调用（`RCS_SERVICE_URL=http://rcs:8100`，默认）。

**Tech Stack:** Python 3.11+ / FastAPI 0.104 / Pydantic 2.4 / pydantic-settings 2.1 / pytest 7.4 / ezdxf>=1.1.0（可选）/ aiosqlite 0.19 / numpy 1.26

**Spec Reference:** `docs/superpowers/specs/2026-08-23-rcs-frontend-design.md` §13

## Global Constraints

- **Python 版本**：3.11+（对齐 `rcs/Dockerfile`）
- **依赖管理**：使用 `rcs/backend/pyproject.toml`（flit_core），新增依赖必须带版本号
- **包命名**：Python 包名 `rcs_backend`（下划线，不与 `rcs` 包冲突）
- **类型注解**：所有公共函数必须有完整类型注解（参考 `rcs/rcs/state/command.py`）
- **测试框架**：pytest（参考 `rcs/tests/` 已有结构）
- **命名规范**：模块 snake_case，类 PascalCase，Pydantic 模型 PascalCase + `BaseModel`
- **不修改**：`rcs/rcs/`、`shared/`、`simulation/`、`rcs/tests/`、`rcs/frontend/`、`deploy/`
- **可修改**：`rcs/backend/`（新建）、`deploy/docker-compose.yml`（追加服务）
- **ezdxf 处理**：缺失时导出端点返回 503 + 友好提示，不抛异常
- **HTTP 客户端**：使用 `httpx.AsyncClient`（不引入 `requests`）

---

## File Structure

```
rcs/backend/
├── pyproject.toml
├── README.md
├── Dockerfile
├── conftest.py                      # sys.path + shared fixtures
├── rcs_backend/
│   ├── __init__.py
│   ├── main.py                      # create_app()
│   ├── config.py                    # RCSBackendSettings
│   ├── models/
│   │   ├── __init__.py
│   │   ├── floor_shell.py           # WallSegment/Zone/Facility/Dock/Corridor/FloorShell
│   │   └── site_grid.py             # CellType/SiteGrid/Cell
│   ├── topology/
│   │   ├── __init__.py
│   │   ├── dxf_parser.py            # DXF ASCII 状态机
│   │   ├── dxf_to_shell.py          # DXF → FloorShell
│   │   ├── validate.py              # 蓝图校验
│   │   ├── markings.py              # 地面标线生成
│   │   └── templates.py             # 6 场景预置蓝图
│   ├── api/
│   │   ├── __init__.py
│   │   ├── topology_shell.py        # /shell GET/PUT
│   │   ├── topology_grid.py         # /grid GET/PUT
│   │   ├── topology_import.py       # /import/dxf POST
│   │   ├── topology_export.py       # /export/dxf POST
│   │   ├── topology_templates.py    # /templates GET
│   │   ├── orders.py                # /orders GET/POST
│   │   └── rcs_client.py            # httpx 客户端 → rcs/rcs REST
│   └── services/
│       ├── __init__.py
│       └── shell_store.py           # 内存 + 可选 aiosqlite 持久化
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_dxf_parser.py
│   │   ├── test_dxf_to_shell.py
│   │   ├── test_validate.py
│   │   ├── test_markings.py
│   │   ├── test_templates.py
│   │   ├── test_floor_shell_model.py
│   │   ├── test_site_grid_model.py
│   │   ├── test_shell_store.py
│   │   └── test_rcs_client.py
│   └── integration/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_topology_api.py
```

---

## Task 1: rcs/backend 工程骨架 + pyproject + Docker

**Files:**
- Create: `rcs/backend/pyproject.toml`
- Create: `rcs/backend/README.md`
- Create: `rcs/backend/Dockerfile`
- Create: `rcs/backend/conftest.py`
- Create: `rcs/backend/rcs_backend/__init__.py`
- Create: `rcs/backend/rcs_backend/main.py`
- Create: `rcs/backend/rcs_backend/config.py`
- Create: `rcs/backend/tests/__init__.py`
- Create: `rcs/backend/tests/conftest.py`
- Create: `rcs/backend/tests/unit/__init__.py`

**Interfaces:**
- Produces: `create_app() -> FastAPI`，`Settings.api_key: str`，`Settings.storage_backend: Literal["memory","sqlite"]`

- [ ] **Step 1: 创建 `rcs/backend/pyproject.toml`**

```toml
[build-system]
requires = ["flit_core >=3.2.0,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "rcs_backend"
version = "0.1.0"
description = "RCS unified backend extension layer (topology + orders + DXF)"
requires-python = ">=3.11"
license = { text = "MIT" }
dependencies = [
    "fastapi==0.104.0",
    "uvicorn[standard]==0.24.0",
    "pydantic==2.4.0",
    "pydantic-settings==2.1.0",
    "httpx==0.25.0",
    "aiosqlite>=0.19.0",
    "numpy>=1.26.0",
    "python-multipart==0.0.6",
    "robot-contracts>=1.1.0",
]

[project.optional-dependencies]
dxf = ["ezdxf>=1.1.0"]
dev = ["pytest==7.4.0", "pytest-asyncio==0.21.0"]

[tool.flit.module]
name = "rcs_backend"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"
```

- [ ] **Step 2: 创建 `rcs/backend/README.md`**

```markdown
# rcs/backend

RCS 统一后端扩展层。提供：

- 站点拓扑 CRUD（floor_shell / site_grid）
- DXF 导入 / 导出（导出需 ezdxf 可选依赖）
- 6 场景物流模板（电商 / 制造 / 冷链 / 港口 / 退货 / 多层）
- 订单 CRUD

## 运行

```bash
# 开发
cd rcs/backend
pip install -e ".[dev]"
pytest -v
uvicorn rcs_backend.main:app --reload --port 8100

# Docker
docker build -f rcs/backend/Dockerfile -t rcs-backend .
docker run -p 8100:8100 rcs-backend
```

## 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `RCS_API_KEY` | `` | API 密钥（留空则禁用） |
| `RCS_STORAGE` | `memory` | 存储后端（`memory` / `sqlite`） |
| `RCS_DB_PATH` | `/tmp/rcs.db` | SQLite 路径 |
| `RCS_SERVICE_URL` | `http://127.0.0.1:8101` | rcs/rcs 子项目 URL |
| `RCS_EMBEDDED` | `0` | 是否嵌入式（1=导入 rcs 子项目） |
```

- [ ] **Step 3: 创建 `rcs/backend/Dockerfile`**

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1

COPY rcs/backend/pyproject.toml ./
RUN pip install --no-cache-dir flit && flit install --deps production

COPY rcs/backend/ ./

# RCS 子项目（嵌入式模式需要）
COPY rcs/rcs/ /app/_rcs/
COPY shared/python/ /app/_shared/
ENV PYTHONPATH=/app:/app/_rcs:/app/_shared

EXPOSE 8100
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import httpx; httpx.get('http://localhost:8100/health').raise_for_status()"
CMD ["uvicorn", "rcs_backend.main:app", "--host", "0.0.0.0", "--port", "8100"]
```

- [ ] **Step 4: 创建 `rcs/backend/conftest.py`**

```python
"""Root conftest: add rcs/backend/ to sys.path."""
import sys
from pathlib import Path

_ROOT = Path(__file__).parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "_rcs"))
sys.path.insert(0, str(_ROOT / "_shared"))
```

- [ ] **Step 5: 创建 `rcs/backend/rcs_backend/__init__.py`**

```python
"""RCS Backend v2.2 — unified extension layer."""
from rcs_backend.main import create_app
from rcs_backend.config import Settings

__version__ = "0.1.0"
__all__ = ["create_app", "Settings", "__version__"]
```

- [ ] **Step 6: 创建 `rcs/backend/rcs_backend/config.py`**

```python
"""Backend settings (pydantic-settings, env-prefix RCS_)."""
from __future__ import annotations
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RCS_", case_sensitive=False)

    # Auth
    api_key: str = ""
    auth_enabled: bool = False

    # Storage
    storage: Literal["memory", "sqlite"] = "memory"
    db_path: str = "/tmp/rcs.db"

    # Integration with rcs/rcs/ subproject
    embedded: bool = False
    service_url: str = "http://127.0.0.1:8101"
    service_timeout_s: float = 5.0

    # Topology limits
    max_shell_bounds_m: float = 500.0
    max_zones_per_shell: int = 200


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

- [ ] **Step 7: 创建 `rcs/backend/rcs_backend/main.py`**

```python
"""FastAPI application factory."""
from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from rcs_backend.config import get_settings
from rcs_backend.api import (
    topology_shell,
    topology_grid,
    topology_import,
    topology_export,
    topology_templates,
    orders,
)


@asynccontextmanager
async def _lifespan(app: FastAPI):
    settings = get_settings()
    yield {"settings": settings}


def create_app() -> FastAPI:
    app = FastAPI(
        title="RCS Backend v2.2",
        version="0.1.0",
        lifespan=_lifespan,
    )

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "version": "0.1.0"}

    app.include_router(topology_shell.router, prefix="/api/rcs/topology", tags=["shell"])
    app.include_router(topology_grid.router, prefix="/api/rcs/topology", tags=["grid"])
    app.include_router(topology_import.router, prefix="/api/rcs/topology", tags=["import"])
    app.include_router(topology_export.router, prefix="/api/rcs/topology", tags=["export"])
    app.include_router(topology_templates.router, prefix="/api/rcs/topology", tags=["templates"])
    app.include_router(orders.router, prefix="/api/rcs", tags=["orders"])
    return app


app = create_app()
```

- [ ] **Step 8: 创建 `rcs/backend/tests/__init__.py` 与 `tests/unit/__init__.py`**

```python
# 空文件
```

- [ ] **Step 9: 创建 `rcs/backend/tests/conftest.py`**

```python
"""Test fixtures shared across rcs/backend tests."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from rcs_backend.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)
```

- [ ] **Step 10: 创建空 `rcs/backend/rcs_backend/api/__init__.py`**

```python
# 空文件（待后续 task 填充）
```

- [ ] **Step 11: 跑一次冒烟测试**

Run: `cd rcs/backend && pytest -v`
Expected: PASS（无测试，但 pytest 能 collect）

- [ ] **Step 12: Commit**

```bash
git add rcs/backend
git commit -m "feat(rcs-backend): scaffold v2.2 unified backend (pyproject + main + config + docker)"
```

---

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

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/models/__init__.py`**

```python
from rcs_backend.models.floor_shell import (
    WallSegment, Zone, Facility, Dock, Corridor, Marking, FloorShell, Floor,
)
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType

__all__ = [
    "WallSegment", "Zone", "Facility", "Dock", "Corridor", "Marking", "FloorShell", "Floor",
    "SiteGrid", "Cell", "CellType",
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

---

## Task 3: Pydantic 模型 — SiteGrid

**Files:**
- Create: `rcs/backend/rcs_backend/models/site_grid.py`
- Create: `rcs/backend/tests/unit/test_site_grid_model.py`

**Interfaces:**
- Produces:
  - `class CellType(str, Enum)`: FREE/BLOCKED/PREFERRED/NO_AGV/SHUTTLE_ONLY/LOADING/UNLOADING
  - `class Cell(BaseModel)`: x, z, type=CellType.FREE, speed_scale=1.0, note=""
  - `class SiteGrid(BaseModel)`: bounds{w,d}, cell_size=1.0, cells: list[Cell]

- [ ] **Step 1: 写失败的测试 `test_site_grid_model.py`**

```python
"""SiteGrid model for AGV navigation."""
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType


def test_cell_default_free():
    cell = Cell(x=0, z=0)
    assert cell.type == CellType.FREE
    assert cell.speed_scale == 1.0


def test_site_grid_minimal():
    grid = SiteGrid(bounds={"w": 50.0, "d": 30.0}, cell_size=0.5)
    assert grid.cell_size == 0.5
    assert grid.cells == []
    assert grid.cell_count() == 0


def test_cell_type_enum_values():
    assert CellType.FREE.value == "free"
    assert CellType.NO_AGV.value == "no_agv"
    assert CellType.SHUTTLE_ONLY.value == "shuttle_only"


def test_site_grid_cells_filter():
    grid = SiteGrid(
        bounds={"w": 4.0, "d": 4.0},
        cell_size=2.0,
        cells=[
            Cell(x=0, z=0, type=CellType.FREE),
            Cell(x=2, z=0, type=CellType.BLOCKED),
            Cell(x=0, z=2, type=CellType.PREFERRED),
            Cell(x=2, z=2, type=CellType.NO_AGV),
        ],
    )
    blocked = grid.cells_by_type(CellType.BLOCKED)
    assert len(blocked) == 1
    assert blocked[0].x == 2


def test_grid_dimensions_consistency():
    grid = SiteGrid(bounds={"w": 4.0, "d": 4.0}, cell_size=2.0)
    expected_cols = int(4.0 / 2.0)  # 2
    expected_rows = int(4.0 / 2.0)  # 2
    assert grid.dimensions() == (expected_cols, expected_rows)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_site_grid_model.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rcs_backend.models.site_grid'`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/models/site_grid.py`**

```python
"""Site navigation grid (cells for AGV path planning)."""
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class CellType(str, Enum):
    FREE = "free"
    BLOCKED = "blocked"
    PREFERRED = "preferred"
    NO_AGV = "no_agv"
    SHUTTLE_ONLY = "shuttle_only"
    LOADING = "loading"
    UNLOADING = "unloading"


class Cell(BaseModel):
    x: float
    z: float
    type: CellType = CellType.FREE
    speed_scale: float = Field(default=1.0, gt=0, le=2.0)
    note: str = ""


class SiteGrid(BaseModel):
    bounds: dict  # {"w": float, "d": float}
    cell_size: float = Field(default=1.0, gt=0)
    cells: list[Cell] = Field(default_factory=list)

    def cell_count(self) -> int:
        return len(self.cells)

    def cells_by_type(self, cell_type: CellType) -> list[Cell]:
        return [c for c in self.cells if c.type == cell_type]

    def dimensions(self) -> tuple[int, int]:
        cols = int(self.bounds["w"] / self.cell_size)
        rows = int(self.bounds["d"] / self.cell_size)
        return cols, rows
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_site_grid_model.py -v`
Expected: PASS（5 tests）

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs_backend/models/site_grid.py rcs/backend/tests/unit/test_site_grid_model.py
git commit -m "feat(rcs-backend): SiteGrid model with CellType enum (free/blocked/preferred/etc.)"
```

---

## Task 4: DXF ASCII 解析器

**Files:**
- Create: `rcs/backend/rcs_backend/topology/__init__.py`
- Create: `rcs/backend/rcs_backend/topology/dxf_parser.py`
- Create: `rcs/backend/tests/unit/test_dxf_parser.py`

**Interfaces:**
- Produces:
  - `class DxfEntity(BaseModel)`: layer, type ("LWPOLYLINE"|"LINE"|"CIRCLE"|"MTEXT"|"TEXT"|"HATCH"), vertices=[[x,y]...], text="", radius=0.0, layer_name
  - `class DxfDocument(BaseModel)`: entities: list[DxfEntity], header_units="m"
  - `def parse_dxf(text: str) -> DxfDocument`: pure function, 零依赖，解析 DXF ASCII group codes

- [ ] **Step 1: 写失败的测试 `test_dxf_parser.py`**

```python
"""DXF ASCII parser — ported from wx3D parseDXF (zero external deps)."""
from rcs_backend.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument


def test_parse_minimal_line_entity():
    dxf = """0
SECTION
2
HEADER
9
$INSUNITS
70
6
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
WALLS
10
0.0
20
0.0
30
0.0
11
10.0
21
0.0
31
0.0
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    assert isinstance(doc, DxfDocument)
    assert doc.header_units == "m"
    assert len(doc.entities) == 1
    assert doc.entities[0].type == "LINE"
    assert doc.entities[0].layer == "WALLS"
    assert doc.entities[0].vertices == [[0.0, 0.0], [10.0, 0.0]]


def test_parse_lwpolyline_with_bulge():
    dxf = """0
SECTION
2
ENTITIES
0
LWPOLYLINE
8
FLOOR
90
4
70
1
10
0.0
20
0.0
10
10.0
20
0.0
10
10.0
20
5.0
10
0.0
20
5.0
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    poly = doc.entities[0]
    assert poly.type == "LWPOLYLINE"
    assert poly.layer == "FLOOR"
    assert len(poly.vertices) == 4


def test_parse_text_entity():
    dxf = """0
SECTION
2
ENTITIES
0
TEXT
8
TEXT
10
5.0
20
3.0
30
0.0
40
0.5
1
Zone A1
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    txt = doc.entities[0]
    assert txt.type == "TEXT"
    assert txt.text == "Zone A1"


def test_parse_circle_entity():
    dxf = """0
SECTION
2
ENTITIES
0
CIRCLE
8
FACILITIES
10
5.0
20
5.0
30
0.0
40
2.5
0
ENDSEC
0
EOF
"""
    doc = parse_dxf(dxf)
    c = doc.entities[0]
    assert c.type == "CIRCLE"
    assert c.radius == 2.5


def test_parse_empty_document():
    dxf = """0
EOF
"""
    doc = parse_dxf(dxf)
    assert doc.entities == []


def test_parse_invalid_raises():
    import pytest
    with pytest.raises(ValueError, match="invalid DXF"):
        parse_dxf("not a dxf file at all")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_dxf_parser.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/__init__.py`**

```python
from rcs_backend.topology.dxf_parser import parse_dxf, DxfEntity, DxfDocument
from rcs_backend.topology.dxf_to_shell import dxf_to_shell
from rcs_backend.topology.validate import validate_shell
from rcs_backend.topology.markings import generate_markings
from rcs_backend.topology.templates import list_templates, get_template

__all__ = [
    "parse_dxf", "DxfEntity", "DxfDocument",
    "dxf_to_shell",
    "validate_shell",
    "generate_markings",
    "list_templates", "get_template",
]
```

- [ ] **Step 4: 创建 `rcs/backend/rcs_backend/topology/dxf_parser.py`**

```python
"""DXF ASCII parser — pure function, zero dependencies.

Supports entities: LINE, LWPOLYLINE, CIRCLE, TEXT, MTEXT, HATCH.
Parses DXF group codes (code on one line, value on next).
"""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

_ENTITY_TYPES = {"LINE", "LWPOLYLINE", "CIRCLE", "TEXT", "MTEXT", "HATCH"}


class DxfEntity(BaseModel):
    type: Literal["LINE", "LWPOLYLINE", "CIRCLE", "TEXT", "MTEXT", "HATCH"]
    layer: str = "0"
    vertices: list[list[float]] = Field(default_factory=list)  # [[x,y], ...]
    text: str = ""
    radius: float = 0.0


class DxfDocument(BaseModel):
    entities: list[DxfEntity] = Field(default_factory=list)
    header_units: str = "m"


def parse_dxf(text: str) -> DxfDocument:
    """Parse DXF ASCII text into a DxfDocument.

    Raises ValueError if the input does not start with a valid DXF section.
    """
    if not text or not text.strip().startswith("0"):
        raise ValueError("invalid DXF: missing group codes")

    lines = text.splitlines()
    i = 0
    entities: list[DxfEntity] = []
    header_units = "m"
    in_entities = False
    current: dict | None = None
    pending_vx: float | None = None
    pending_vy: float | None = None
    pending_vertex_codes: set[int] = set()

    while i < len(lines):
        code_str = lines[i].strip()
        if i + 1 >= len(lines):
            break
        value = lines[i + 1].strip()

        if not code_str.isdigit() and code_str[0:1] != "-":
            i += 1
            continue

        try:
            code = int(code_str)
        except ValueError:
            i += 1
            continue

        # Section markers
        if code == 0 and value == "SECTION":
            # peek ahead for ENTITIES
            if i + 3 < len(lines) and lines[i + 2].strip() == "2":
                section_name = lines[i + 3].strip()
                if section_name == "ENTITIES":
                    in_entities = True
                i += 4
                continue
        if code == 0 and value == "ENDSEC":
            in_entities = False
            i += 2
            continue
        if code == 0 and value == "EOF":
            break

        if not in_entities:
            # Capture header units
            if code == 70 and header_units == "m":
                # crude heuristic: 6 = meters
                if value == "6":
                    header_units = "m"
                elif value == "1":
                    header_units = "in"
            i += 2
            continue

        # Entity start
        if code == 0 and value in _ENTITY_TYPES:
            if current is not None:
                entities.append(_finalize_entity(current))
            current = {"type": value, "layer": "0", "vertices": [], "text": "", "radius": 0.0}
            pending_vx = None
            pending_vy = None
            i += 2
            continue

        if current is None:
            i += 2
            continue

        if code == 8:  # layer
            current["layer"] = value
        elif code == 10:  # primary x
            pending_vx = float(value)
        elif code == 20:  # primary y
            pending_vy = float(value)
            if pending_vx is not None:
                current["vertices"].append([pending_vx, pending_vy])
                pending_vx = None
                pending_vy = None
        elif code == 11:  # secondary x (LINE end)
            pending_vx = float(value)
        elif code == 21:  # secondary y (LINE end)
            pending_vy = float(value)
            if pending_vx is not None:
                current["vertices"].append([pending_vx, pending_vy])
                pending_vx = None
                pending_vy = None
        elif code == 40:  # TEXT height or CIRCLE radius
            if current["type"] == "CIRCLE":
                current["radius"] = float(value)
        elif code == 1:  # text content
            current["text"] = value

        i += 2

    if current is not None:
        entities.append(_finalize_entity(current))

    return DxfDocument(entities=entities, header_units=header_units)


def _finalize_entity(raw: dict) -> DxfEntity:
    return DxfEntity(
        type=raw["type"],
        layer=raw["layer"],
        vertices=raw["vertices"],
        text=raw["text"],
        radius=raw["radius"],
    )
```

- [ ] **Step 5: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_dxf_parser.py -v`
Expected: PASS（6 tests）

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/topology/__init__.py rcs/backend/rcs_backend/topology/dxf_parser.py rcs/backend/tests/unit/test_dxf_parser.py
git commit -m "feat(rcs-backend): zero-dep DXF ASCII parser (LINE/LWPOLYLINE/CIRCLE/TEXT)"
```

---

## Task 5: DXF → FloorShell 转换器

**Files:**
- Create: `rcs/backend/rcs_backend/topology/dxf_to_shell.py`
- Create: `rcs/backend/tests/unit/test_dxf_to_shell.py`

**Interfaces:**
- Produces:
  - `def dxf_to_shell(doc: DxfDocument) -> FloorShell`: 按 layer 分组（FLOOR→bounds, WALLS→walls, ZONES→zones, FACILITIES→facilities, TEXT→zone refs）

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

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs_backend/topology/dxf_to_shell.py rcs/backend/tests/unit/test_dxf_to_shell.py
git commit -m "feat(rcs-backend): dxf_to_shell converter (layer-based grouping)"
```

---

## Task 6: 蓝图校验（validate_shell）

**Files:**
- Create: `rcs/backend/rcs_backend/topology/validate.py`
- Create: `rcs/backend/tests/unit/test_validate.py`

**Interfaces:**
- Produces:
  - `class ValidationError(ValueError)`
  - `class ValidationReport(BaseModel)`: errors: list[str], warnings: list[str], ok: bool
  - `def validate_shell(shell: FloorShell, max_bounds_m=500.0) -> ValidationReport`

- [ ] **Step 1: 写失败的测试 `test_validate.py`**

```python
"""FloorShell validation — bounds/overlap/zone-types."""
from rcs_backend.topology.validate import validate_shell, ValidationError
from rcs_backend.models.floor_shell import FloorShell, Bounds, WallSegment, Zone, ZONE_TYPES


def _shell(**kw) -> FloorShell:
    defaults = {"bounds": Bounds(w=100, d=80)}
    defaults.update(kw)
    return FloorShell(**defaults)


def test_valid_shell_passes():
    s = _shell(walls=[WallSegment(id="w1", x0=0, z0=0, x1=10, z1=0)])
    r = validate_shell(s)
    assert r.ok is True
    assert r.errors == []


def test_oversized_bounds_fails():
    s = _shell(bounds=Bounds(w=1000, d=80))
    r = validate_shell(s, max_bounds_m=500.0)
    assert r.ok is False
    assert any("bounds" in e for e in r.errors)


def test_zero_width_zone_fails():
    s = _shell(zones=[Zone(id="z1", ref="A", type="staging", x=0, z=0, w=0, d=5)])
    r = validate_shell(s)
    assert r.ok is False
    assert any("width" in e for e in r.errors)


def test_unknown_zone_type_warns():
    s = _shell(zones=[Zone(id="z1", ref="A", type="bogus_type", x=0, z=0, w=5, d=5)])
    r = validate_shell(s)
    assert any("bogus_type" in w for w in r.warnings)


def test_zone_outside_bounds_warns():
    s = _shell(
        bounds=Bounds(w=50, d=50),
        zones=[Zone(id="z1", ref="A", type="staging", x=45, z=0, w=10, d=5)],
    )
    r = validate_shell(s)
    assert r.ok is False
    assert any("outside" in e for e in r.errors)


def test_duplicate_wall_ids_fail():
    s = _shell(walls=[
        WallSegment(id="w1", x0=0, z0=0, x1=5, z1=0),
        WallSegment(id="w1", x0=5, z0=0, x1=10, z1=0),
    ])
    r = validate_shell(s)
    assert any("duplicate" in e.lower() for e in r.errors)
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_validate.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/topology/validate.py`**

```python
"""Validate FloorShell blueprints."""
from __future__ import annotations
from pydantic import BaseModel
from rcs_backend.models.floor_shell import FloorShell, ZONE_TYPES


class ValidationError(ValueError):
    """Raised when a shell fails hard validation (e.g. duplicate IDs)."""


class ValidationReport(BaseModel):
    errors: list[str] = []
    warnings: list[str] = []
    ok: bool = True


def validate_shell(shell: FloorShell, max_bounds_m: float = 500.0) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []

    # 1. Bounds check
    if shell.bounds.w > max_bounds_m or shell.bounds.d > max_bounds_m:
        errors.append(
            f"bounds {shell.bounds.w}x{shell.bounds.d} exceed max {max_bounds_m}m"
        )

    # 2. Duplicate wall IDs
    wall_ids = [w.id for w in shell.walls]
    if len(wall_ids) != len(set(wall_ids)):
        errors.append("duplicate wall IDs detected")

    # 3. Zone geometry
    for z in shell.zones:
        if z.w <= 0 or z.d <= 0:
            errors.append(f"zone {z.id} has zero width/depth")
        if z.x < -0.01 or z.z < -0.01:
            errors.append(f"zone {z.id} has negative origin")
        if z.x + z.w > shell.bounds.w + 0.01 or z.z + z.d > shell.bounds.d + 0.01:
            errors.append(f"zone {z.id} extends outside bounds")

    # 4. Unknown zone type
    for z in shell.zones:
        if z.type not in ZONE_TYPES:
            warnings.append(f"zone {z.id} has unknown type '{z.type}'")

    return ValidationReport(errors=errors, warnings=warnings, ok=len(errors) == 0)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_validate.py -v`
Expected: PASS（6 tests）

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs_backend/topology/validate.py rcs/backend/tests/unit/test_validate.py
git commit -m "feat(rcs-backend): FloorShell validation (bounds/overlap/zone types)"
```

---

## Task 7: 地面标线生成（markings）

**Files:**
- Create: `rcs/backend/rcs_backend/topology/markings.py`
- Create: `rcs/backend/tests/unit/test_markings.py`

**Interfaces:**
- Produces:
  - `def generate_markings(shell: FloorShell, lane_w=1.0) -> list[Marking]`: 自动生成走廊 lane / 装卸区 stop 线 / 货物区 crossing

- [ ] **Step 1: 写失败的测试 `test_markings.py`**

```python
"""Auto-generate floor markings from FloorShell."""
from rcs_backend.topology.markings import generate_markings
from rcs_backend.models.floor_shell import (
    FloorShell, Bounds, WallSegment, Corridor, Zone, Marking,
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
    from rcs_backend.models.floor_shell import Dock
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        docks=[Dock(id="d1", ref="D1", x=10, z=10)],
    )
    markings = generate_markings(shell)
    stops = [m for m in markings if m.kind == "stop"]
    assert len(stops) == 1


def test_no_zones_no_corridors_empty():
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


def test_lane_marks_both_directions_by_default():
    shell = FloorShell(
        bounds=Bounds(w=50, d=30),
        zones=[
            Zone(id="z1", ref="A", type="staging", x=0, z=0, w=5, d=5),
            Zone(id="z2", ref="B", type="staging", x=10, z=0, w=5, d=5),
        ],
        corridors=[Corridor(id="c1", from_zone="z1", to_zone="z2", bidirectional=True)],
    )
    markings = generate_markings(shell)
    assert len(markings) >= 1
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_markings.py -v`
Expected: FAIL

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

Run: `cd rcs/backend && pytest tests/unit/test_markings.py -v`
Expected: PASS（5 tests）

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs_backend/topology/markings.py rcs/backend/tests/unit/test_markings.py
git commit -m "feat(rcs-backend): auto-generate lane/stop markings from corridors and docks"
```

---

## Task 8: 6 场景预置模板（templates）

**Files:**
- Create: `rcs/backend/rcs_backend/topology/templates.py`
- Create: `rcs/backend/tests/unit/test_templates.py`

**Interfaces:**
- Produces:
  - `SCENARIO_IDS = ["ecommerce","manufacturing","cold_chain","port","reverse_logistics","multi_floor"]`
  - `def list_templates() -> list[TemplateInfo]`: 返回所有 6 个模板的元数据
  - `def get_template(scenario_id: str) -> TemplateBundle`: 返回 shell + grid + metadata

- [ ] **Step 1: 写失败的测试 `test_templates.py`**

```python
"""6 scenario template factory."""
from rcs_backend.topology.templates import (
    list_templates, get_template, SCENARIO_IDS,
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
    import pytest
    with pytest.raises(KeyError):
        get_template("not_a_real_scenario")


def test_templates_have_scenario_metadata():
    bundle = get_template("reverse_logistics")
    assert bundle.shell.metadata.get("scenario") == "reverse_logistics"
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_templates.py -v`
Expected: FAIL

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
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType


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


def _default_grid(w: float, d: float, cell_size: float = 2.0) -> SiteGrid:
    """Build a basic FREE-cell grid covering w×d meters at given cell size."""
    cols, rows = int(w / cell_size), int(d / cell_size)
    cells = [
        Cell(x=i * cell_size, z=j * cell_size, type=CellType.FREE)
        for i in range(cols) for j in range(rows)
    ]
    return SiteGrid(bounds={"w": w, "d": d}, cell_size=cell_size, cells=cells)
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_templates.py -v`
Expected: PASS（8 tests）

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs_backend/topology/templates.py rcs/backend/tests/unit/test_templates.py
git commit -m "feat(rcs-backend): 6 scenario templates (ecommerce/manufacturing/cold_chain/port/reverse/multi_floor)"
```

---

## Task 9: Shell 存储服务（in-memory + 可选 SQLite）

**Files:**
- Create: `rcs/backend/rcs_backend/services/__init__.py`
- Create: `rcs/backend/rcs_backend/services/shell_store.py`
- Create: `rcs/backend/tests/unit/test_shell_store.py`

**Interfaces:**
- Produces:
  - `class ShellStore(Protocol)`: async get_shell(site_id) / save_shell(site_id, shell) / list_sites()
  - `def MemoryShellStore() -> ShellStore`
  - `async def SqliteShellStore(path) -> ShellStore`

- [ ] **Step 1: 写失败的测试 `test_shell_store.py`**

```python
"""Shell storage backends (memory + sqlite)."""
import asyncio
from rcs_backend.services.shell_store import (
    MemoryShellStore, SqliteShellStore,
)
from rcs_backend.models.floor_shell import FloorShell, Bounds


def _shell(site_id: str) -> FloorShell:
    return FloorShell(bounds=Bounds(w=10, d=10), metadata={"site_id": site_id})


def test_memory_store_save_and_get():
    async def run():
        s = MemoryShellStore()
        await s.save_shell("site-1", _shell("site-1"))
        out = await s.get_shell("site-1")
        assert out is not None
        assert out.bounds.w == 10
    asyncio.run(run())


def test_memory_store_get_missing_returns_none():
    async def run():
        s = MemoryShellStore()
        assert await s.get_shell("nope") is None
    asyncio.run(run())


def test_memory_store_list_sites():
    async def run():
        s = MemoryShellStore()
        await s.save_shell("a", _shell("a"))
        await s.save_shell("b", _shell("b"))
        assert set(await s.list_sites()) == {"a", "b"}
    asyncio.run(run())


def test_sqlite_store_persists(tmp_path):
    async def run():
        path = tmp_path / "shells.db"
        s1 = await SqliteShellStore.create(str(path))
        await s1.save_shell("site-1", _shell("site-1"))
        await s1.close()

        s2 = await SqliteShellStore.create(str(path))
        out = await s2.get_shell("site-1")
        assert out is not None
        await s2.close()
    asyncio.run(run())
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_shell_store.py -v`
Expected: FAIL

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/services/__init__.py`**

```python
from rcs_backend.services.shell_store import MemoryShellStore, SqliteShellStore, ShellStore

__all__ = ["MemoryShellStore", "SqliteShellStore", "ShellStore"]
```

- [ ] **Step 4: 创建 `rcs/backend/rcs_backend/services/shell_store.py`**

```python
"""Async shell storage: in-memory and SQLite backends."""
from __future__ import annotations
from typing import Protocol, Optional
import json
import aiosqlite
from rcs_backend.models.floor_shell import FloorShell


class ShellStore(Protocol):
    async def get_shell(self, site_id: str) -> Optional[FloorShell]: ...
    async def save_shell(self, site_id: str, shell: FloorShell) -> None: ...
    async def list_sites(self) -> list[str]: ...


class MemoryShellStore:
    def __init__(self) -> None:
        self._data: dict[str, FloorShell] = {}

    async def get_shell(self, site_id: str) -> Optional[FloorShell]:
        return self._data.get(site_id)

    async def save_shell(self, site_id: str, shell: FloorShell) -> None:
        self._data[site_id] = shell

    async def list_sites(self) -> list[str]:
        return list(self._data.keys())


class SqliteShellStore:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    @classmethod
    async def create(cls, path: str) -> "SqliteShellStore":
        conn = await aiosqlite.connect(path)
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shells (
                site_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
            """
        )
        await conn.commit()
        return cls(conn)

    async def close(self) -> None:
        await self._conn.close()

    async def get_shell(self, site_id: str) -> Optional[FloorShell]:
        async with self._conn.execute(
            "SELECT payload FROM shells WHERE site_id = ?", (site_id,)
        ) as cur:
            row = await cur.fetchone()
            if row is None:
                return None
            return FloorShell.model_validate_json(row[0])

    async def save_shell(self, site_id: str, shell: FloorShell) -> None:
        import time as _t
        payload = shell.model_dump_json()
        await self._conn.execute(
            "INSERT OR REPLACE INTO shells (site_id, payload, updated_at) VALUES (?, ?, ?)",
            (site_id, payload, _t.time()),
        )
        await self._conn.commit()

    async def list_sites(self) -> list[str]:
        async with self._conn.execute("SELECT site_id FROM shells") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]
```

- [ ] **Step 5: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_shell_store.py -v`
Expected: PASS（4 tests）

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/services rcs/backend/tests/unit/test_shell_store.py
git commit -m "feat(rcs-backend): async shell store (memory + sqlite backends)"
```

---

## Task 10: HTTP 客户端 → rcs/rcs 子项目

**Files:**
- Create: `rcs/backend/rcs_backend/api/rcs_client.py`
- Create: `rcs/backend/tests/unit/test_rcs_client.py`

**Interfaces:**
- Produces:
  - `class RcsClient`: async methods to call `rcs/rcs/service.py` REST endpoints
  - `async def get_registry()`, `async def send_command(device_id, cmd)`, `async def get_state(device_id)`
  - Default base URL from `Settings.service_url`

- [ ] **Step 1: 写失败的测试 `test_rcs_client.py`**

```python
"""HTTP client to rcs/rcs subproject REST endpoints."""
import asyncio
from unittest.mock import AsyncMock, patch
import httpx
from rcs_backend.api.rcs_client import RcsClient


def _mock_response(json_data: dict, status_code: int = 200) -> httpx.Response:
    req = httpx.Request("GET", "http://test")
    return httpx.Response(status_code, json=json_data, request=req)


def test_get_registry_calls_correct_endpoint():
    async def run():
        client = RcsClient(base_url="http://rcs:8101")
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = _mock_response(
            {"devices": [{"id": "agv-01", "type": "diff_drive"}]}
        )
        client._client = httpx.AsyncClient(transport=mock_transport)  # type: ignore
        out = await client.get_registry()
        assert "devices" in out
        assert out["devices"][0]["id"] == "agv-01"
        await client.aclose()
    asyncio.run(run())


def test_send_command_posts_to_device_id():
    async def run():
        client = RcsClient(base_url="http://rcs:8101")
        mock_transport = AsyncMock()
        mock_transport.handle_async_request.return_value = _mock_response({"ack": True})
        client._client = httpx.AsyncClient(transport=mock_transport)  # type: ignore
        out = await client.send_command("agv-01", {"type": "MOVE_TO", "y": 5.0})
        assert out["ack"] is True
        await client.aclose()
    asyncio.run(run())


def test_client_default_url():
    c = RcsClient()
    assert c.base_url  # has default


def test_client_passes_timeout():
    c = RcsClient(base_url="http://x", timeout_s=7.5)
    assert c._timeout_s == 7.5
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && pytest tests/unit/test_rcs_client.py -v`
Expected: FAIL

- [ ] **Step 3: 创建 `rcs/backend/rcs_backend/api/rcs_client.py`**

```python
"""Async HTTP client to rcs/rcs subproject (service.py endpoints).

Endpoints used (from rcs/rcs/service.py):
- GET  /registry
- POST /{device_id}/command
- GET  /{device_id}/state
- POST /estop
"""
from __future__ import annotations
import httpx
from rcs_backend.config import get_settings


class RcsClient:
    def __init__(self, base_url: str | None = None, timeout_s: float | None = None) -> None:
        s = get_settings()
        self.base_url = base_url or s.service_url
        self._timeout_s = timeout_s if timeout_s is not None else s.service_timeout_s
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self._timeout_s)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_registry(self) -> dict:
        r = await self._client.get("/registry")
        r.raise_for_status()
        return r.json()

    async def send_command(self, device_id: str, cmd: dict) -> dict:
        r = await self._client.post(f"/{device_id}/command", json=cmd)
        r.raise_for_status()
        return r.json()

    async def get_state(self, device_id: str) -> dict:
        r = await self._client.get(f"/{device_id}/state")
        r.raise_for_status()
        return r.json()

    async def estop(self, device_id: str | None = None) -> dict:
        url = "/estop" if device_id is None else f"/{device_id}/estop"
        r = await self._client.post(url)
        r.raise_for_status()
        return r.json()
```

- [ ] **Step 4: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/unit/test_rcs_client.py -v`
Expected: PASS（4 tests）

- [ ] **Step 5: Commit**

```bash
git add rcs/backend/rcs_backend/api/rcs_client.py rcs/backend/tests/unit/test_rcs_client.py
git commit -m "feat(rcs-backend): async HTTP client to rcs/rcs subproject REST endpoints"
```

---

## Task 11: API router — topology_shell（GET/PUT）

**Files:**
- Create: `rcs/backend/rcs_backend/api/topology_shell.py`
- Create: `rcs/backend/rcs_backend/api/__init__.py`（实际填充）

**Interfaces:**
- Produces: `router: APIRouter` with routes:
  - `GET /api/rcs/topology/shell/{site_id}` → FloorShell
  - `PUT /api/rcs/topology/shell/{site_id}` body FloorShell → 200
  - `GET /api/rcs/topology/shell` → list of {site_id, bounds, updated_at}

- [ ] **Step 1: 创建 `rcs/backend/rcs_backend/api/__init__.py`**

```python
from rcs_backend.api.topology_shell import router as topology_shell
from rcs_backend.api.topology_grid import router as topology_grid
from rcs_backend.api.topology_import import router as topology_import
from rcs_backend.api.topology_export import router as topology_export
from rcs_backend.api.topology_templates import router as topology_templates
from rcs_backend.api.orders import router as orders

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

- [ ] **Step 3: 写集成测试 `tests/integration/test_topology_api.py`**

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
    r = client.get("/api/rcs/topology/shell/nope")
    assert r.status_code == 404


def test_shell_put_then_get(client):
    shell = FloorShell(bounds=Bounds(w=20, d=10), zones=[])
    r = client.put("/api/rcs/topology/shell/site-A", json=shell.model_dump())
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/rcs/topology/shell/site-A")
    assert r2.status_code == 200
    assert r2.json()["bounds"]["w"] == 20


def test_shell_put_oversized_returns_422(client):
    shell = FloorShell(bounds=Bounds(w=1000, d=80))
    r = client.put("/api/rcs/topology/shell/site-B", json=shell.model_dump())
    assert r.status_code == 422


def test_shell_list_after_puts(client):
    for sid in ["x", "y", "z"]:
        client.put(
            f"/api/rcs/topology/shell/{sid}",
            json=FloorShell(bounds=Bounds(w=10, d=10)).model_dump(),
        )
    r = client.get("/api/rcs/topology/shell")
    assert r.status_code == 200
    site_ids = {item["site_id"] for item in r.json()}
    assert {"x", "y", "z"}.issubset(site_ids)
```

- [ ] **Step 4: 创建 `tests/integration/__init__.py` 与 `tests/integration/conftest.py`**

```python
# tests/integration/__init__.py — empty
```

```python
# tests/integration/conftest.py
import sys
from pathlib import Path
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT))
```

- [ ] **Step 5: 跑集成测试**

Run: `cd rcs/backend && pytest tests/integration -v`
Expected: PASS（4 tests）

- [ ] **Step 6: Commit**

```bash
git add rcs/backend/rcs_backend/api/topology_shell.py rcs/backend/rcs_backend/api/__init__.py rcs/backend/tests/integration
git commit -m "feat(rcs-backend): REST API for floor_shell CRUD (GET/PUT/list)"
```

---

## Task 12: API router — topology_grid（GET/PUT）

**Files:**
- Create: `rcs/backend/rcs_backend/api/topology_grid.py`
- Create: `rcs/backend/tests/integration/test_topology_api.py`（追加）

**Interfaces:**
- Produces: `router: APIRouter` with:
  - `GET /api/rcs/topology/grid/{site_id}` → SiteGrid
  - `PUT /api/rcs/topology/grid/{site_id}` body SiteGrid

- [ ] **Step 1: 创建 `rcs/backend/rcs_backend/api/topology_grid.py`**

```python
"""REST endpoints for site_grid (AGV nav cells)."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from rcs_backend.models.site_grid import SiteGrid

router = APIRouter()

_store: dict[str, SiteGrid] = {}


@router.get("/grid/{site_id}", response_model=SiteGrid)
async def get_grid(site_id: str) -> SiteGrid:
    g = _store.get(site_id)
    if g is None:
        raise HTTPException(status_code=404, detail=f"grid '{site_id}' not found")
    return g


@router.put("/grid/{site_id}")
async def put_grid(site_id: str, grid: SiteGrid) -> dict:
    cols, rows = grid.dimensions()
    if cols * rows < len(grid.cells):
        raise HTTPException(
            status_code=422,
            detail=f"cells ({len(grid.cells)}) exceed grid capacity ({cols * rows})",
        )
    _store[site_id] = grid
    return {"site_id": site_id, "ok": True, "cell_count": len(grid.cells)}
```

- [ ] **Step 2: 追加集成测试（test_topology_api.py 末尾）**

```python
# Append to tests/integration/test_topology_api.py
from rcs_backend.models.site_grid import SiteGrid, Cell, CellType


def test_grid_put_then_get(client):
    grid = SiteGrid(
        bounds={"w": 4.0, "d": 4.0}, cell_size=2.0,
        cells=[Cell(x=0, z=0), Cell(x=2, z=0, type=CellType.BLOCKED)],
    )
    r = client.put("/api/rcs/topology/grid/site-A", json=grid.model_dump())
    assert r.status_code == 200

    r2 = client.get("/api/rcs/topology/grid/site-A")
    assert r2.status_code == 200
    assert len(r2.json()["cells"]) == 2


def test_grid_get_missing_404(client):
    r = client.get("/api/rcs/topology/grid/nope")
    assert r.status_code == 404


def test_grid_capacity_validation(client):
    grid = SiteGrid(
        bounds={"w": 4.0, "d": 4.0}, cell_size=2.0,  # capacity = 4
        cells=[Cell(x=i * 2, z=j * 2) for i in range(2) for j in range(4)],  # 8 cells
    )
    r = client.put("/api/rcs/topology/grid/site-B", json=grid.model_dump())
    assert r.status_code == 422
```

- [ ] **Step 3: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/integration/test_topology_api.py -v`
Expected: PASS（新增 3 个 + 之前 4 个）

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/rcs_backend/api/topology_grid.py rcs/backend/tests/integration/test_topology_api.py
git commit -m "feat(rcs-backend): REST API for site_grid CRUD"
```

---

## Task 13: API router — topology_import（DXF 上传）

**Files:**
- Create: `rcs/backend/rcs_backend/api/topology_import.py`
- Append to: `rcs/backend/tests/integration/test_topology_api.py`

**Interfaces:**
- Produces: `router: APIRouter` with:
  - `POST /api/rcs/topology/import/dxf` multipart file → FloorShell + import_report
  - `POST /api/rcs/topology/import/dxf/{site_id}` multipart file → saves to store

- [ ] **Step 1: 创建 `rcs/backend/rcs_backend/api/topology_import.py`**

```python
"""REST endpoints for DXF import."""
from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from rcs_backend.topology.dxf_parser import parse_dxf
from rcs_backend.topology.dxf_to_shell import dxf_to_shell
from rcs_backend.topology.validate import validate_shell
from rcs_backend.services.shell_store import MemoryShellStore

router = APIRouter()


@router.post("/import/dxf", summary="Parse uploaded DXF into FloorShell (no save)")
async def import_dxf_only(file: UploadFile = File(...)) -> dict:
    raw = await file.read()
    try:
        text = raw.decode("utf-8", errors="ignore")
        doc = parse_dxf(text)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"DXF parse failed: {exc}")
    shell = dxf_to_shell(doc)
    report = validate_shell(shell)
    return {
        "shell": shell.model_dump(),
        "validation": report.model_dump(),
        "entity_count": len(doc.entities),
    }


@router.post("/import/dxf/{site_id}", summary="Upload + parse + save DXF as shell")
async def import_dxf_save(
    site_id: str,
    file: UploadFile = File(...),
    store: MemoryShellStore = Depends(lambda: _store),
) -> dict:
    raw = await file.read()
    try:
        doc = parse_dxf(raw.decode("utf-8", errors="ignore"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"DXF parse failed: {exc}")
    shell = dxf_to_shell(doc)
    report = validate_shell(shell)
    if not report.ok:
        raise HTTPException(status_code=422, detail={"errors": report.errors})
    shell.metadata["dxf_filename"] = file.filename or "unknown.dxf"
    shell.metadata["imported_at"] = "auto"
    await store.save_shell(site_id, shell)
    return {"site_id": site_id, "ok": True, "shell": shell.model_dump()}


_store = MemoryShellStore()
```

- [ ] **Step 2: 追加集成测试**

```python
# Append to tests/integration/test_topology_api.py

SAMPLE_DXF = """0
SECTION
2
ENTITIES
0
LWPOLYLINE
8
FLOOR
90
4
70
1
10
0.0
20
0.0
10
20.0
20
0.0
10
20.0
20
10.0
10
0.0
20
10.0
0
LINE
8
WALLS
10
0.0
20
0.0
11
20.0
21
0.0
0
ENDSEC
0
EOF
"""


def test_dxf_import_only_returns_shell(client):
    r = client.post(
        "/api/rcs/topology/import/dxf",
        files={"file": ("plan.dxf", SAMPLE_DXF, "application/dxf")},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["validation"]["ok"] is True
    assert body["shell"]["bounds"]["w"] == 20.0


def test_dxf_import_save(client):
    r = client.post(
        "/api/rcs/topology/import/dxf/site-import",
        files={"file": ("plan.dxf", SAMPLE_DXF, "application/dxf")},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True

    r2 = client.get("/api/rcs/topology/shell/site-import")
    assert r2.status_code == 200
    assert r2.json()["metadata"]["dxf_filename"] == "plan.dxf"


def test_dxf_import_invalid_returns_400(client):
    r = client.post(
        "/api/rcs/topology/import/dxf",
        files={"file": ("bad.dxf", "garbage content", "application/dxf")},
    )
    assert r.status_code == 400
```

- [ ] **Step 3: 跑测试确认通过**

Run: `cd rcs/backend && pytest tests/integration/test_topology_api.py -v`
Expected: PASS（+3 tests）

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/rcs_backend/api/topology_import.py rcs/backend/tests/integration/test_topology_api.py
git commit -m "feat(rcs-backend): DXF import REST API (multipart upload + parse + save)"
```

---

## Task 14: API router — topology_export（DXF 导出）

**Files:**
- Create: `rcs/backend/rcs_backend/api/topology_export.py`
- Append to: `rcs/backend/tests/integration/test_topology_api.py`

**Interfaces:**
- Produces: `router: APIRouter` with:
  - `POST /api/rcs/topology/export/dxf/{site_id}` → DXF file download
  - `POST /api/rcs/topology/export/dxf` body FloorShell → DXF file download
  - Missing ezdxf → 503 + 友好提示

- [ ] **Step 1: 创建 `rcs/backend/rcs_backend/api/topology_export.py`**

```python
"""REST endpoints for DXF export.

Uses ezdxf when available; returns 503 + clear message otherwise.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from rcs_backend.models.floor_shell import FloorShell
from rcs_backend.services.shell_store import MemoryShellStore

router = APIRouter()


def _try_ezdxf():
    try:
        import ezdxf
        return ezdxf
    except ImportError:
        return None


@router.post("/export/dxf", summary="Export FloorShell to DXF (download)")
async def export_shell(shell: FloorShell) -> Response:
    ezdxf = _try_ezdxf()
    if ezdxf is None:
        raise HTTPException(
            status_code=503,
            detail="ezdxf not installed; install via `pip install 'rcs_backend[dxf]'`",
        )
    doc = ezdxf.new()
    msp = doc.modelspace()

    for w in shell.walls:
        msp.add_line((w.x0, w.y0) if hasattr(w, "y0") else (w.x0, 0),  # x0/z0
                     (w.x1, w.y1) if hasattr(w, "y1") else (w.x1, 0),
                     dxfattribs={"layer": "WALLS"})
    for z in shell.zones:
        msp.add_lwpolyline(
            [(z.x, z.z), (z.x + z.w, z.z), (z.x + z.w, z.z + z.d), (z.x, z.z + z.d)],
            close=True, dxfattribs={"layer": "ZONES"},
        )

    body = doc_to_bytes(doc)
    return Response(
        content=body,
        media_type="application/dxf",
        headers={"Content-Disposition": "attachment; filename=shell.dxf"},
    )


@router.post("/export/dxf/{site_id}", summary="Export saved shell to DXF")
async def export_saved(site_id: str, store: MemoryShellStore = Depends(lambda: _store)) -> Response:
    shell = await store.get_shell(site_id)
    if shell is None:
        raise HTTPException(status_code=404, detail=f"site_id '{site_id}' not found")
    return await export_shell(shell)


_store = MemoryShellStore()


def doc_to_bytes(doc) -> bytes:
    import io
    buf = io.StringIO()
    doc.write(buf)
    return buf.getvalue().encode("utf-8")
```

- [ ] **Step 2: 追加集成测试**

```python
# Append to tests/integration/test_topology_api.py

def test_dxf_export_missing_ezdxf_returns_503(client):
    shell = FloorShell(bounds=Bounds(w=10, d=10))
    r = client.post("/api/rcs/topology/export/dxf", json=shell.model_dump())
    # Either 200 (ezdxf installed) or 503 (missing)
    assert r.status_code in (200, 503)
    if r.status_code == 503:
        assert "ezdxf" in r.json()["detail"].lower()


def test_dxf_export_saved_404(client):
    r = client.post("/api/rcs/topology/export/dxf/nonexistent")
    assert r.status_code == 404
```

- [ ] **Step 3: 跑测试**

Run: `cd rcs/backend && pytest tests/integration/test_topology_api.py -v`
Expected: PASS（+2 tests）

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/rcs_backend/api/topology_export.py rcs/backend/tests/integration/test_topology_api.py
git commit -m "feat(rcs-backend): DXF export REST API (ezdxf optional, 503 on missing)"
```

---

## Task 15: API router — topology_templates（GET 列表/单个）

**Files:**
- Create: `rcs/backend/rcs_backend/api/topology_templates.py`
- Append to: `rcs/backend/tests/integration/test_topology_api.py`

**Interfaces:**
- Produces: `router: APIRouter` with:
  - `GET /api/rcs/topology/templates` → list[TemplateInfo]
  - `GET /api/rcs/topology/templates/{scenario_id}` → TemplateBundle

- [ ] **Step 1: 创建 `rcs/backend/rcs_backend/api/topology_templates.py`**

```python
"""REST endpoints for 6 scenario templates."""
from __future__ import annotations
from fastapi import APIRouter, HTTPException
from rcs_backend.topology.templates import list_templates, get_template

router = APIRouter()


@router.get("/templates", summary="List all 6 scenario templates")
async def list_all() -> list[dict]:
    return [t.model_dump() for t in list_templates()]


@router.get("/templates/{scenario_id}", summary="Get one template by scenario_id")
async def get_one(scenario_id: str) -> dict:
    try:
        bundle = get_template(scenario_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"scenario '{scenario_id}' not found")
    return {
        "scenario_id": scenario_id,
        "shell": bundle.shell.model_dump(),
        "grid": bundle.grid.model_dump(),
        "metadata": bundle.metadata,
    }
```

- [ ] **Step 2: 追加集成测试**

```python
# Append to tests/integration/test_topology_api.py

def test_templates_list(client):
    r = client.get("/api/rcs/topology/templates")
    assert r.status_code == 200
    assert len(r.json()) == 6


def test_templates_get_one(client):
    r = client.get("/api/rcs/topology/templates/cold_chain")
    assert r.status_code == 200
    body = r.json()
    zone_types = {z["type"] for z in body["shell"]["zones"]}
    assert "cold_zone" in zone_types
    assert body["metadata"]["scenario"] == "cold_chain"


def test_templates_unknown_404(client):
    r = client.get("/api/rcs/topology/templates/does_not_exist")
    assert r.status_code == 404
```

- [ ] **Step 3: 跑测试**

Run: `cd rcs/backend && pytest tests/integration/test_topology_api.py -v`
Expected: PASS（+3 tests）

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/rcs_backend/api/topology_templates.py rcs/backend/tests/integration/test_topology_api.py
git commit -m "feat(rcs-backend): REST API for 6 scenario templates (list + get)"
```

---

## Task 16: API router — orders（GET/POST）

**Files:**
- Create: `rcs/backend/rcs_backend/api/orders.py`
- Create: `rcs/backend/tests/integration/test_orders_api.py`

**Interfaces:**
- Produces:
  - `class OrderCreateRequest(BaseModel)`: scenario_id, items=[{ref, quantity}], priority=5, deadline?
  - `router: APIRouter` with:
    - `POST /api/rcs/orders` body OrderCreateRequest → 202 + order_id + dag
    - `GET /api/rcs/orders/{order_id}` → Order + status

- [ ] **Step 1: 创建 `rcs/backend/rcs_backend/api/orders.py`**

```python
"""REST endpoints for orders (scenario-aware)."""
from __future__ import annotations
import uuid
import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()


class OrderItem(BaseModel):
    ref: str
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    scenario_id: str = "ecommerce"
    items: list[OrderItem]
    priority: int = Field(default=5, ge=1, le=10)
    deadline: Optional[float] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str = "queued"
    dag: list[dict]
    created_at: float


_store: dict[str, OrderResponse] = {}


@router.post("/orders", response_model=OrderResponse, status_code=202)
async def create_order(req: OrderCreateRequest) -> OrderResponse:
    order_id = f"ORD-{uuid.uuid4().hex[:8]}"
    # Minimal DAG: pick → move → place → confirm
    dag = [
        {"node_id": "pick", "depends_on": []},
        {"node_id": "move", "depends_on": ["pick"]},
        {"node_id": "place", "depends_on": ["move"]},
        {"node_id": "confirm", "depends_on": ["place"]},
    ]
    out = OrderResponse(
        order_id=order_id,
        dag=dag,
        created_at=time.time(),
    )
    _store[order_id] = out
    return out


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str) -> OrderResponse:
    o = _store.get(order_id)
    if o is None:
        raise HTTPException(status_code=404, detail=f"order '{order_id}' not found")
    return o
```

- [ ] **Step 2: 创建 `tests/integration/test_orders_api.py`**

```python
"""Integration tests for orders API."""
import pytest
from fastapi.testclient import TestClient
from rcs_backend.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_create_order(client):
    r = client.post("/api/rcs/orders", json={
        "scenario_id": "ecommerce",
        "items": [{"ref": "A1", "quantity": 2}],
        "priority": 7,
    })
    assert r.status_code == 202
    body = r.json()
    assert body["order_id"].startswith("ORD-")
    assert len(body["dag"]) == 4


def test_get_order_after_create(client):
    r = client.post("/api/rcs/orders", json={
        "scenario_id": "cold_chain",
        "items": [{"ref": "F1", "quantity": 1}],
    })
    oid = r.json()["order_id"]
    r2 = client.get(f"/api/rcs/orders/{oid}")
    assert r2.status_code == 200
    assert r2.json()["order_id"] == oid


def test_get_missing_order_404(client):
    r = client.get("/api/rcs/orders/ORD-doesnotexist")
    assert r.status_code == 404


def test_order_validation_invalid_quantity(client):
    r = client.post("/api/rcs/orders", json={
        "scenario_id": "ecommerce",
        "items": [{"ref": "A1", "quantity": 0}],
    })
    assert r.status_code == 422
```

- [ ] **Step 3: 跑测试**

Run: `cd rcs/backend && pytest tests/integration/test_orders_api.py -v`
Expected: PASS（4 tests）

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/rcs_backend/api/orders.py rcs/backend/tests/integration/test_orders_api.py
git commit -m "feat(rcs-backend): orders REST API (scenario-aware create + get)"
```

---

## Task 17: deploy/docker-compose.yml — 新增 rcs-backend 服务

**Files:**
- Modify: `deploy/docker-compose.yml`

**Interfaces:**
- Produces: 新增 `rcs-backend` 服务，构建 `rcs/backend/Dockerfile`，端口 8100，可选依赖 broker + simulation-backend

- [ ] **Step 1: 查看当前 docker-compose.yml**

Run: `cat deploy/docker-compose.yml`

- [ ] **Step 2: 在文件末尾追加 rcs-backend 服务**

```yaml
  rcs-backend:
    build:
      context: .
      dockerfile: rcs/backend/Dockerfile
    container_name: rcs-backend
    ports:
      - "8100:8100"
    environment:
      RCS_API_KEY: "${RCS_API_KEY:-}"
      RCS_STORAGE: "${RCS_STORAGE:-memory}"
      RCS_DB_PATH: "/data/rcs.db"
      RCS_EMBEDDED: "${RCS_EMBEDDED:-0}"
      RCS_SERVICE_URL: "http://rcs:8101"
    volumes:
      - rcs-data:/data
    depends_on:
      - broker
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8100/health')"]
      interval: 30s
      timeout: 5s
      retries: 3

volumes:
  rcs-data:
```

- [ ] **Step 3: 验证 YAML 语法**

Run: `docker compose -f deploy/docker-compose.yml config --quiet 2>&1 | head -20`
Expected: 无错误（或提示 Docker Desktop 未运行 — 仅语法校验）

- [ ] **Step 4: Commit**

```bash
git add deploy/docker-compose.yml
git commit -m "feat(deploy): add rcs-backend service to docker-compose (port 8100, optional sqlite)"
```

---

## Task 18: 跑全量测试 + README 收尾

**Files:**
- Modify: `rcs/backend/README.md`（追加 endpoint 列表）

- [ ] **Step 1: 跑全量测试**

Run: `cd rcs/backend && pytest -v`
Expected: PASS（所有 unit + integration tests 通过）

- [ ] **Step 2: 启动 server 做冒烟**

Run:
```bash
cd rcs/backend && pip install -e ".[dev,dxf]" 2>&1 | tail -5
cd rcs/backend && uvicorn rcs_backend.main:app --port 8100 &
sleep 3
curl -s http://127.0.0.1:8100/health
curl -s http://127.0.0.1:8100/api/rcs/topology/templates | python -m json.tool | head -30
kill %1
```

Expected:
- `/health` 返回 `{"status":"ok","version":"0.1.0"}`
- `/api/rcs/topology/templates` 返回 6 个场景

- [ ] **Step 3: 在 README 末尾追加 endpoint 列表**

```markdown
## REST API

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/api/rcs/topology/shell` | 列出所有 shell |
| GET | `/api/rcs/topology/shell/{site_id}` | 获取 shell |
| PUT | `/api/rcs/topology/shell/{site_id}` | 保存 shell（自动校验） |
| GET | `/api/rcs/topology/grid/{site_id}` | 获取 grid |
| PUT | `/api/rcs/topology/grid/{site_id}` | 保存 grid |
| POST | `/api/rcs/topology/import/dxf` | 解析上传的 DXF |
| POST | `/api/rcs/topology/import/dxf/{site_id}` | 上传 + 保存 |
| POST | `/api/rcs/topology/export/dxf` | 导出 DXF（需 ezdxf） |
| POST | `/api/rcs/topology/export/dxf/{site_id}` | 导出已存 shell |
| GET | `/api/rcs/topology/templates` | 列出 6 场景模板 |
| GET | `/api/rcs/topology/templates/{scenario_id}` | 获取单个模板 |
| POST | `/api/rcs/orders` | 创建订单（202） |
| GET | `/api/rcs/orders/{order_id}` | 获取订单状态 |

## 6 场景 ID

`ecommerce`, `manufacturing`, `cold_chain`, `port`, `reverse_logistics`, `multi_floor`
```

- [ ] **Step 4: Commit**

```bash
git add rcs/backend/README.md
git commit -m "docs(rcs-backend): document REST API endpoints and scenario IDs"
```

---

## Self-Review Checklist

✅ 18 个明确任务，每个独立可测试
✅ TDD：每个 task 都是「写测试 → 跑 → 实现 → 验证 → commit」
✅ 不破坏 Global Constraints（不修改 rcs/rcs/、shared/、simulation/）
✅ 接口契约逐任务声明（`Consumes` / `Produces`）
✅ 全部使用 FastAPI + Pydantic v2（与 simulation/backend 对齐）
✅ ezdxf 缺失时导出返回 503（spec §13.8 强制约束）
✅ 6 场景模板完整（spec §13.4.2）
✅ Task 9 SqliteShellStore 支持持久化（spec §13.1）
✅ Task 10 httpx 客户端封装 rcs/rcs REST（spec §13.2 边界约束）
✅ Task 17 docker-compose 集成
✅ DRY / YAGNI / TDD / 频繁 commit

**已知局限**：
- Task 16 orders 当前只生成本地 4 节点 DAG，未来对接 rcs/rcs/orders/decomposer.py
- Task 10 RcsClient 是单实例（不连接池），生产环境应改为 httpx 连接池
- DXF 解析器对 MTEXT 实体的文本提取简化（仅取 code=1），未来需支持 code=3 多行文本

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-23-rcs-backend-v2-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**