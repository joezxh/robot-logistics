from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import math
from typing import List


class DeviceStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    CHARGING = "charging"
    FAULT = "fault"


@dataclass
class Device:
    device_id: str
    device_type: str
    name: str
    position: List[float]
    route: List[List[float]] = field(default_factory=list)
    speed: float = 0.8
    status: DeviceStatus = DeviceStatus.IDLE
    progress: float = 0.0
    battery: float = 100.0
    current_task: str | None = None

    def start(self, task_id: str, route: List[List[float]]) -> None:
        self.current_task = task_id
        self.route = route
        self.progress = 0.0
        self.status = DeviceStatus.RUNNING

    def tick(self, seconds: float) -> None:
        if self.status != DeviceStatus.RUNNING:
            return
        self.progress = min(1.0, self.progress + seconds * self.speed / 12.0)
        self.battery = max(0.0, self.battery - seconds * 0.04)
        self.position = self._route_position(self.progress)
        if math.isclose(self.progress, 1.0):
            self.status = DeviceStatus.IDLE
            self.current_task = None

    def _route_position(self, progress: float) -> List[float]:
        if len(self.route) < 2:
            return self.position
        segment_float = progress * (len(self.route) - 1)
        index = min(int(segment_float), len(self.route) - 2)
        local = segment_float - index
        return [
            self.route[index][axis] * (1 - local) + self.route[index + 1][axis] * local
            for axis in range(3)
        ]

    def snapshot(self) -> dict:
        data = asdict(self)
        data["status"] = self.status.value
        return data
