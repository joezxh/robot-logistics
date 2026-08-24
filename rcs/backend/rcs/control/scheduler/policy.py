from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from ..dag.node import TaskNode, SLOClass


@dataclass
class UtilityWeights:
    w1: float = 0.5
    w2: float = 0.3
    w3: float = 0.15
    w4: float = 0.05


def compute_utility(node: TaskNode, current_time: datetime, weights: UtilityWeights) -> float:
    if node.deadline is None:
        urgency = -1.0
    else:
        time_to_deadline = max((node.deadline - current_time).total_seconds(), 1.0)
        urgency = 1.0 / time_to_deadline

    slo_bonus = {
        SLOClass.HARD: 1.0,
        SLOClass.SOFT: 0.5,
        SLOClass.BEST_EFFORT: 0.0,
    }[node.slo_class]

    affinity_score = 1.0 if node.device_id else 0.5
    overrun_penalty = 0.0

    return (
        weights.w1 * urgency
        + weights.w2 * slo_bonus
        + weights.w3 * affinity_score
        - weights.w4 * overrun_penalty
    )
