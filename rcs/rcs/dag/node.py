"""DAG node model: TaskNode, TaskType, and SLOClass."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class TaskType(str, Enum):
    TRANSPORT = "transport"
    PICK = "pick"
    PLACE = "place"
    WAIT = "wait"
    SYNC = "sync"


class SLOClass(str, Enum):
    HARD = "hard"
    SOFT = "soft"
    BEST_EFFORT = "best-effort"


@dataclass
class TaskNode:
    task_id: str
    type: TaskType
    device_id: str | None = None
    params: dict = field(default_factory=dict)
    dependencies: list[str] = field(default_factory=list)
    deadline: datetime | None = None
    slo_class: SLOClass = SLOClass.SOFT
