import asyncio
import time
from rcs.loop import ControlLoop
from rcs.registry import registry


def test_loop_start_spawns_per_device_tasks():
    """In an async context, start() must spawn one task per registered device.
    In a sync context, start() is a documented no-op.
    """
    registry.load()
    try:
        async def _go():
            loop = ControlLoop()
            loop.start()
            try:
                # Give tasks a moment to spawn.
                await asyncio.sleep(0.05)
                expected = {p.device_id for p in registry.list_devices()}
                assert set(loop._tasks.keys()) == expected
                # Tasks should be scheduled and not done immediately.
                for t in loop._tasks.values():
                    assert isinstance(t, asyncio.Task)
                    assert not t.done()
            finally:
                loop.shutdown()
                # Allow the cancel to propagate.
                await asyncio.sleep(0.01)

        asyncio.run(_go())
    finally:
        registry._reset_for_tests()


def test_loop_start_is_noop_in_sync_context():
    """When called from a sync test (no event loop), start() is a graceful no-op
    rather than raising. The service tests rely on this when they call
    `loop.start()` from inside a TestClient.
    """
    registry.load()
    try:
        loop = ControlLoop()
        # Should not raise even though no event loop is running.
        loop.start()
        # No tasks should have been spawned.
        assert loop._tasks == {}
    finally:
        registry._reset_for_tests()
