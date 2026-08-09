from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
import time
from typing import List


class TaskPriority(IntEnum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    task_id: str
    task_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    source: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    target: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    status: ExecutionStatus = ExecutionStatus.PENDING
    created_time: float = field(default_factory=time.time)
