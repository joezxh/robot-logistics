"""Async event bus for RCS-1 internal events.

Used to surface halt/fault/estop events to future subscribers (e.g. an
AlertEngine bridge) without RCS-1 importing the alert service.
"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Subscription:
    name: str
    callback: Callable[[Any], None]
    bus: "EventBus"
    _active: bool = True

    def unsubscribe(self) -> None:
        if not self._active:
            return
        self._active = False
        self.bus._drop(self)


class EventBus:
    def __init__(self) -> None:
        self._subs: list[Subscription] = []
        self._lock = asyncio.Lock()

    def subscribe(self, name: str, callback: Callable[[Any], None]) -> Subscription:
        sub = Subscription(name=name, callback=callback, bus=self)
        self._subs.append(sub)
        return sub

    def _drop(self, sub: Subscription) -> None:
        try:
            self._subs.remove(sub)
        except ValueError:
            pass

    def publish(self, name: str, payload: Any) -> None:
        for sub in list(self._subs):
            if sub._active and sub.name == name:
                try:
                    sub.callback(payload)
                except Exception:  # pragma: no cover - callback isolation
                    pass
