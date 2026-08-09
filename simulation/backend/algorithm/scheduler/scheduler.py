from __future__ import annotations

import heapq
from typing import Dict, List

from .task import Task


class TaskScheduler:
    def __init__(self) -> None:
        self.tasks: Dict[str, Task] = {}
        self.completed: set[str] = set()

    def add_task(self, task: Task) -> None:
        if task.task_id in self.tasks:
            raise ValueError(f"duplicate task: {task.task_id}")
        self.tasks[task.task_id] = task
        self._assert_acyclic()

    def mark_completed(self, task_id: str) -> None:
        if task_id not in self.tasks:
            raise KeyError(task_id)
        self.completed.add(task_id)
        self.tasks[task_id].status = "completed"

    def get_next_batch(self, max_concurrent: int = 3) -> List[Task]:
        ready = []
        for task in self.tasks.values():
            if task.task_id in self.completed or task.status != "pending":
                continue
            if all(dependency in self.completed for dependency in task.dependencies):
                heapq.heappush(ready, (int(task.priority), task.created_time, task.task_id, task))
        return [heapq.heappop(ready)[-1] for _ in range(min(max_concurrent, len(ready)))]

    def _assert_acyclic(self) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise ValueError("task dependency cycle detected")
            if task_id in visited or task_id not in self.tasks:
                return
            visiting.add(task_id)
            for dependency in self.tasks[task_id].dependencies:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for identifier in self.tasks:
            visit(identifier)
