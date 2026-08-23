## Task 2: DAG 图构建与拓扑排序

**Files:**
- Create: `rcs/rcs/dag/graph.py`
- Modify: `rcs/rcs/dag/__init__.py`
- Test: `rcs/tests/unit/test_dag_graph.py`

**Interfaces:**
- Consumes: `TaskNode`（来自 Task 1）
- Produces:
  - `TaskDAG` class：`add_node()`, `add_dependency()`, `topological_sort()`, `get_ready_nodes()`, `validate()`

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_dag_graph.py
from rcs.dag.node import TaskNode, TaskType
from rcs.dag.graph import TaskDAG
from rcs.dag.exceptions import CycleError, NodeNotFoundError


def test_dag_add_and_get_node():
    dag = TaskDAG()
    node = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    dag.add_node(node)
    assert dag.get_node("t1") == node


def test_dag_get_unknown_node_raises():
    dag = TaskDAG()
    try:
        dag.get_node("unknown")
        assert False, "should have raised"
    except NodeNotFoundError:
        pass


def test_dag_topological_sort_linear():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PLACE))
    dag.add_node(TaskNode(task_id="t3", type=TaskType.TRANSPORT))
    dag.add_dependency("t2", "t1")
    dag.add_dependency("t3", "t2")
    order = dag.topological_sort()
    assert order == ["t1", "t2", "t3"]


def test_dag_topological_sort_parallel():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t3", type=TaskType.PLACE))
    dag.add_dependency("t3", "t1")
    dag.add_dependency("t3", "t2")
    order = dag.topological_sort()
    assert order[0] in ("t1", "t2")
    assert order[1] in ("t1", "t2")
    assert order[2] == "t3"


def test_dag_cycle_detection():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PLACE))
    dag.add_dependency("t1", "t2")
    try:
        dag.add_dependency("t2", "t1")
        assert False, "should have raised CycleError"
    except CycleError:
        pass


def test_dag_get_ready_nodes():
    dag = TaskDAG()
    dag.add_node(TaskNode(task_id="t1", type=TaskType.PICK))
    dag.add_node(TaskNode(task_id="t2", type=TaskType.PLACE))
    dag.add_node(TaskNode(task_id="t3", type=TaskType.TRANSPORT))
    dag.add_dependency("t2", "t1")
    ready = dag.get_ready_nodes()
    assert [n.task_id for n in ready] == ["t1"]
    dag.mark_completed("t1")
    ready = dag.get_ready_nodes()
    assert [n.task_id for n in ready] == ["t2"]
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_dag_graph.py -v
```

预期：FAIL（`ModuleNotFoundError: No module named 'rcs.dag.graph'`）

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/dag/graph.py
from __future__ import annotations
from collections import defaultdict, deque
from .node import TaskNode
from .exceptions import DAGError, CycleError, NodeNotFoundError


class TaskDAG:
    def __init__(self) -> None:
        self._nodes: dict[str, TaskNode] = {}
        self._edges: dict[str, set[str]] = defaultdict(set)  # t1 -> {t2, t3} (t1 precedes t2, t3)
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
        self._edges[prerequisite].add(dependent)
        if self._has_cycle():
            self._edges[prerequisite].discard(dependent)
            raise CycleError(f"dependency {dependent} -> {prerequisite} creates a cycle")

    def topological_sort(self) -> list[str]:
        in_degree: dict[str, int] = {nid: 0 for nid in self._nodes}
        for src, dsts in self._edges.items():
            for dst in dsts:
                in_degree[dst] += 1
        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        order: list[str] = []
        while queue:
            nid = queue.popleft()
            order.append(nid)
            for dst in self._edges[nid]:
                in_degree[dst] -= 1
                if in_degree[dst] == 0:
                    queue.append(dst)
        if len(order) != len(self._nodes):
            raise CycleError("graph contains a cycle")
        return order

    def get_ready_nodes(self) -> list[TaskNode]:
        completed_predecessors: set[str] = set()
        for src, dsts in self._edges.items():
            if src in self._completed:
                completed_predecessors.update(dsts)
        ready_ids = completed_predecessors - self._completed
        ready_ids = ready_ids - {
            dst for src, dsts in self._edges.items()
            if src not in self._completed
            for dst in dsts
        }
        return [self._nodes[nid] for nid in ready_ids if nid in self._nodes]

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
```

修改 `rcs/rcs/dag/__init__.py`：

```python
from .node import TaskNode, TaskType, SLOClass
from .exceptions import DAGError, CycleError, NodeNotFoundError
from .graph import TaskDAG

__all__ = [
    "TaskNode", "TaskType", "SLOClass",
    "TaskDAG", "DAGError", "CycleError", "NodeNotFoundError",
]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_dag_graph.py -v
```

预期：PASS（6 tests passed）

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/dag/ rcs/tests/unit/test_dag_graph.py
git commit -m "feat(rcs): add DAG graph with topological sort and cycle detection"
```

---

