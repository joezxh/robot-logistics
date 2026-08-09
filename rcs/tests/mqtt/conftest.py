"""Fake MQTT client used across the adapter tests.

Records every publish and lets tests inject inbound messages, so the adapter can
be exercised end-to-end without a real broker.
"""
from __future__ import annotations

from typing import Callable

import pytest


class FakeMqttClient:
    def __init__(self, *, fail_publish: bool = False) -> None:
        self.published: list[tuple[str, bytes | str, int, bool]] = []
        self.subscriptions: list[tuple[str, int]] = []
        self._handlers: dict[str, Callable[[str, bytes], None]] = {}
        self.connected = True
        self.publish_failures = 0
        self.publish_successes = 0
        self._fail_publish = fail_publish
        self.started = False
        self.stopped = False

    async def start(self) -> None:
        self.started = True

    async def stop(self) -> None:
        self.stopped = True

    def subscribe(self, topic_filter: str, qos: int, handler: Callable[[str, bytes], None]) -> None:
        self.subscriptions.append((topic_filter, qos))
        self._handlers[topic_filter] = handler

    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False) -> bool:
        if self._fail_publish:
            self.publish_failures += 1
            return False
        self.published.append((topic, payload, qos, retain))
        self.publish_successes += 1
        return True

    # --- test helper --------------------------------------------------------

    def inject(self, topic: str, payload: bytes) -> None:
        """Simulate an inbound broker message."""
        from rcs.mqtt.client import _topic_matches

        for topic_filter, handler in self._handlers.items():
            if _topic_matches(topic_filter, topic):
                handler(topic, payload)
                return
        raise AssertionError(f"no handler matched topic {topic!r}")

    def topics(self) -> list[str]:
        return [t for t, _, _, _ in self.published]


@pytest.fixture
def fake_client() -> FakeMqttClient:
    return FakeMqttClient()
