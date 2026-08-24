from __future__ import annotations
from dataclasses import dataclass
from ..dag.node import TaskNode


@dataclass
class DeviceCandidate:
    device_id: str
    type: str
    load_capacity: float
    current_utilization: float = 0.0


def select_device(
    task: TaskNode,
    candidates: list[DeviceCandidate],
    max_utilization: float = 0.9,
) -> DeviceCandidate | None:
    eligible = [c for c in candidates if c.current_utilization <= max_utilization]
    if not eligible:
        return None

    def score(c: DeviceCandidate) -> float:
        utilization_score = 1.0 - c.current_utilization
        capacity_score = min(c.load_capacity / 1000.0, 1.0)
        return 0.4 * utilization_score + 0.3 * capacity_score + 0.3 * 1.0

    return max(eligible, key=score)
