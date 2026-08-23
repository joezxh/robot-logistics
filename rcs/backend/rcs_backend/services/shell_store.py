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


_default_memory_store: MemoryShellStore | None = None


def default_memory_store() -> MemoryShellStore:
    """Module-level shared singleton so multiple routers hit the same store."""
    global _default_memory_store
    if _default_memory_store is None:
        _default_memory_store = MemoryShellStore()
    return _default_memory_store


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