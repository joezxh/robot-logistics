## Task 9: Shell 存储服务（in-memory + 可选 SQLite）

**Files:**
- Create: `rcs/backend/rcs_backend/services/__init__.py`
- Create: `rcs/backend/rcs_backend/services/shell_store.py`
- Create: `rcs/backend/tests/unit/test_shell_store.py`

**Interfaces:**
- Produces:
  - `class ShellStore(Protocol)`: async `get_shell(site_id)` / `save_shell(site_id, shell)` / `list_sites()`
  - `def MemoryShellStore() -> ShellStore`
  - `async def SqliteShellStore.create(path) -> ShellStore`

> **Plan note**: brief has no Step 0. This task doesn't touch `topology/__init__.py`. Confirmed `aiosqlite 0.22.1` is installed (already declared in `pyproject.toml` dep `"aiosqlite>=0.19.0"`).

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
        assert out.metadata.get("site_id") == "site-1"
        await s2.close()
    asyncio.run(run())
```

> **Plan patch note**: brief's `test_sqlite_store_persists` only asserted `out is not None`. Added a `metadata.get("site_id") == "site-1"` check so the test actually verifies the saved round-tripped payload (not just non-null).

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/backend && python -m pytest tests/unit/test_shell_store.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rcs_backend.services'`

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
import time
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
        payload = shell.model_dump_json()
        await self._conn.execute(
            "INSERT OR REPLACE INTO shells (site_id, payload, updated_at) VALUES (?, ?, ?)",
            (site_id, payload, time.time()),
        )
        await self._conn.commit()

    async def list_sites(self) -> list[str]:
        async with self._conn.execute("SELECT site_id FROM shells") as cur:
            rows = await cur.fetchall()
            return [r[0] for r in rows]
```

> **Plan patch note**: brief had `import time as _t` *inside* `save_shell`. Hoisted to module top — better hygiene, same behavior.

- [ ] **Step 5: 跑测试确认通过**

Run: `cd rcs/backend && python -m pytest tests/unit/test_shell_store.py -v`
Expected: PASS（4 tests）

- [ ] **Step 6: 跑全 suite 确认无回归**

Run: `cd rcs/backend && python -m pytest -v`
Expected: 41 (prior) + 4 (new) = 45 passed

- [ ] **Step 7: Commit**

```bash
git add rcs/backend/rcs_backend/services rcs/backend/tests/unit/test_shell_store.py
git commit -m "feat(rcs-backend): async shell store (memory + sqlite backends)"
```