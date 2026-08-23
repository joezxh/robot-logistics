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