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