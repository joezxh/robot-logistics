"""TaskDAG: dependency graph with topological sort, cycle detection, and ready-nodes query."""
from __future__ import annotations
from collections import deque

from .node import TaskNode
from .exceptions import DAGError, CycleError, NodeNotFoundError


class TaskDAG:
    def __init__(self) -> None:
        self._nodes: dict[str, TaskNode] = {}
        self._edges: dict[str, set[str]] = {}  # prerequisite -> {dependents}
        self._completed: set[str] = set()

    def add_node(self, node: TaskNode) -> None:
        if node.task_id in self._nodes:
            raise DAGError(f"duplicate task_id: {node.task_id}")
        self._nodes[node.task_id] = node

    def get_node(self, task_id: str) -> TaskNode:
        if task_id not in self._nodes:
            raise NodeNotFoundError(f"unknown task_id: {task_id}")
        return self._nodes[task_id]

    def add_dependency(self, dependent: str, prerequisite: str) -> None:
        if dependent not in self._nodes:
            raise NodeNotFoundError(f"unknown task_id: {dependent}")
        if prerequisite not in self._nodes:
            raise NodeNotFoundError(f"unknown task_id: {prerequisite}")
        bucket = self._edges.setdefault(prerequisite, set())
        bucket.add(dependent)
        if self._has_cycle():
            bucket.discard(dependent)
            if not bucket:
                del self._edges[prerequisite]
            raise CycleError(f"dependency {dependent} -> {prerequisite} creates a cycle")

    def topological_sort(self) -> list[str]:
        in_degree: dict[str, int] = {nid: 0 for nid in self._nodes}
        for src, dsts in self._edges.items():
            for dst in dsts:
                in_degree[dst] += 1
        queue: deque[str] = deque(nid for nid, deg in in_degree.items() if deg == 0)
        order: list[str] = []
        while queue:
            nid = queue.popleft()
            order.append(nid)
            for dst in self._edges.get(nid, ()):
                in_degree[dst] -= 1
                if in_degree[dst] == 0:
                    queue.append(dst)
        if len(order) != len(self._nodes):
            raise CycleError("graph contains a cycle")
        return order

    def get_ready_nodes(self) -> list[TaskNode]:
        """Return nodes whose predecessors are all completed.

        A node with no predecessors (a source) is included only if it is
        actually referenced as a prerequisite by some other node, so that
        isolated nodes do not appear ready.
        """
        ready_ids: set[str] = set()
        for nid in self._nodes:
            if nid in self._completed:
                continue
            predecessors = [src for src, dsts in self._edges.items() if nid in dsts]
            if predecessors and not all(src in self._completed for src in predecessors):
                continue
            if not predecessors and nid not in self._edges:
                continue
            ready_ids.add(nid)
        return [self._nodes[nid] for nid in ready_ids]

    def mark_completed(self, task_id: str) -> None:
        if task_id not in self._nodes:
            raise NodeNotFoundError(f"unknown task_id: {task_id}")
        self._completed.add(task_id)

    def _has_cycle(self) -> bool:
        try:
            self.topological_sort()
            return False
        except CycleError:
            return True