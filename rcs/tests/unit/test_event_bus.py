import asyncio
from rcs.events import EventBus


def test_subscribe_receives_event():
    bus = EventBus()
    seen: list = []

    async def collect():
        sub = bus.subscribe("e1", lambda p: seen.append(p))
        bus.publish("e1", {"x": 1})
        await asyncio.sleep(0.01)
        assert seen == [{"x": 1}]
        sub.unsubscribe()

    asyncio.run(collect())


def test_unsubscribe_stops_delivery():
    bus = EventBus()
    seen: list = []

    async def collect():
        sub = bus.subscribe("e1", lambda p: seen.append(p))
        sub.unsubscribe()
        bus.publish("e1", {"x": 1})
        await asyncio.sleep(0.01)
        assert seen == []

    asyncio.run(collect())


def test_isolated_by_name():
    bus = EventBus()
    seen: list = []

    async def collect():
        sub = bus.subscribe("e1", lambda p: seen.append(("e1", p)))
        bus.publish("e2", {"x": 1})
        await asyncio.sleep(0.01)
        assert seen == []
        sub.unsubscribe()

    asyncio.run(collect())
