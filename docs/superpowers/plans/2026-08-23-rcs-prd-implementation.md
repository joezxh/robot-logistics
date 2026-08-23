# RCS PRD 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 PRD 中定义的 RCS 调度核心（订单拆解 / 设备调度 / 任务编排）落地为 `robot-logic/rcs/` 内的可运行模块，对齐 FastAPI 后端与 `HardwareHAL` 抽象。

**Architecture:** 在 `rcs/rcs/` 内新增 `scheduler/`、`dispatcher/`、`dag/`、`topology/` 四个子模块。复用现有 HAL、MQTT、控制器层。Scheduler 消费订单 → 产出 DAG → 调度器计算 utility → 派发到 dispatcher → 通过现有 `dispatch_command()` 路由到设备。

**Tech Stack:** Python 3.11+ / FastAPI / Pydantic 2.x / asyncio / 现有 `rcs/rcs/` HAL & MQTT

## Global Constraints

- **Python 版本**：3.11+（对齐 `Dockerfile`）
- **依赖管理**：使用现有 `rcs/requirements.txt`，新增依赖必须带版本号
- **类型注解**：所有公共函数必须有完整类型注解（参考 `rcs/rcs/state/command.py`）
- **测试框架**：pytest（参考 `rcs/tests/` 已有结构）
- **命名规范**：模块名 snake_case，类名 PascalCase（参考现有代码）
- **不修改**：`rcs/rcs/hal/`、`rcs/rcs/controllers/`、`rcs/rcs/mqtt/`、`shared/`、`simulation/`
- **可修改**：`rcs/rcs/` 顶层新增模块、`rcs/tests/`、`rcs/requirements.txt`

---

## File Structure

**新增文件**：

```
rcs/rcs/
├── dag/
│   ├── __init__.py
│   ├── node.py          # TaskNode dataclass
│   ├── graph.py         # DAG 构建与拓扑排序
│   └── exceptions.py    # DAGError, CycleError
├── topology/
│   ├── __init__.py
│   ├── site_map.py      # SiteMap / SiteNode / SiteEdge
│   └── pathfinder.py    # 路径规划（A*）
├── scheduler/
│   ├── __init__.py
│   ├── policy.py        # EDF + utility function
│   ├── arbiter.py       # 冲突仲裁
│   └── allocator.py     # 设备选择与分配
├── dispatcher/
│   ├── __init__.py
│   ├── executor.py      # DAG 执行循环
│   └── event_bus.py     # 内部事件总线（与现有 events.py 解耦）
├── observability/
│   ├── __init__.py
│   ├── metrics.py       # 指标收集
│   └── slo.py           # SLO 监控
└── orders/
    ├── __init__.py
    ├── models.py        # Order Pydantic 模型
    └── decomposer.py    # 订单 → DAG 拆解器

rcs/tests/
├── unit/
│   ├── test_dag_node.py
│   ├── test_dag_graph.py
│   ├── test_topology_site_map.py
│   ├── test_topology_pathfinder.py
│   ├── test_scheduler_policy.py
│   ├── test_scheduler_arbiter.py
│   ├── test_scheduler_allocator.py
│   ├── test_orders_models.py
│   └── test_orders_decomposer.py
└── integration/
    └── test_end_to_end_order_to_dispatch.py
```

---

## Task 1: 任务 DAG 节点模型

**Files:**
- Create: `rcs/rcs/dag/node.py`
- Create: `rcs/rcs/dag/exceptions.py`
- Create: `rcs/rcs/dag/__init__.py`
- Test: `rcs/tests/unit/test_dag_node.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `TaskNode` dataclass（task_id, type, device_id, params, dependencies, deadline, slo_class）
  - `TaskType` enum（transport, pick, place, wait, sync）
  - `SLOClass` enum（hard, soft, best-effort）
  - `DAGError`, `CycleError` exceptions

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_dag_node.py
from datetime import datetime, timedelta
from rcs.dag.node import TaskNode, TaskType, SLOClass
from rcs.dag.exceptions import DAGError


def test_task_node_creation_minimal():
    node = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    assert node.task_id == "t1"
    assert node.type == TaskType.TRANSPORT
    assert node.device_id is None
    assert node.dependencies == []
    assert node.deadline is None
    assert node.slo_class == SLOClass.SOFT


def test_task_node_creation_full():
    deadline = datetime(2026, 12, 1, 12, 0, 0)
    node = TaskNode(
        task_id="t2",
        type=TaskType.PICK,
        device_id="loader-01",
        params={"sku": "A"},
        dependencies=["t1"],
        deadline=deadline,
        slo_class=SLOClass.HARD,
    )
    assert node.device_id == "loader-01"
    assert node.params == {"sku": "A"}
    assert node.dependencies == ["t1"]
    assert node.deadline == deadline
    assert node.slo_class == SLOClass.HARD


def test_dag_error_raised():
    err = DAGError("test message")
    assert str(err) == "test message"
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_dag_node.py -v
```

预期：FAIL（`ModuleNotFoundError: No module named 'rcs.dag'`）

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/dag/exceptions.py
class DAGError(Exception):
    pass


class CycleError(DAGError):
    """DAG contains a cycle."""
    pass


class NodeNotFoundError(DAGError):
    pass
```

```python
# rcs/rcs/dag/node.py
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
```

```python
# rcs/rcs/dag/__init__.py
from .node import TaskNode, TaskType, SLOClass
from .exceptions import DAGError, CycleError, NodeNotFoundError

__all__ = ["TaskNode", "TaskType", "SLOClass", "DAGError", "CycleError", "NodeNotFoundError"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_dag_node.py -v
```

预期：PASS（3 tests passed）

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/dag/ rcs/tests/unit/test_dag_node.py
git commit -m "feat(rcs): add DAG node model with TaskType/SLOClass enums"
```

---

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

## Task 3: 站点地图数据结构

**Files:**
- Create: `rcs/rcs/topology/site_map.py`
- Create: `rcs/rcs/topology/__init__.py`
- Test: `rcs/tests/unit/test_topology_site_map.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `SiteNode` dataclass（node_id, position, type, capacity）
  - `SiteEdge` dataclass（from_node, to_node, distance, speed_limit）
  - `SiteMap` class：`add_node()`, `add_edge()`, `get_neighbors()`, `get_node()`

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_topology_site_map.py
from rcs.topology.site_map import SiteMap, SiteNode, SiteEdge, NodeType


def test_site_map_add_and_get_node():
    sm = SiteMap()
    node = SiteNode(node_id="A1", position=(0.0, 0.0, 0.0), type=NodeType.PICK, capacity=10)
    sm.add_node(node)
    assert sm.get_node("A1") == node


def test_site_map_add_edge_and_neighbors():
    sm = SiteMap()
    sm.add_node(SiteNode(node_id="A1", position=(0.0, 0.0, 0.0), type=NodeType.PICK))
    sm.add_node(SiteNode(node_id="A2", position=(1.0, 0.0, 0.0), type=NodeType.PICK))
    sm.add_edge(SiteEdge(from_node="A1", to_node="A2", distance=1.0, speed_limit=1.5))
    neighbors = sm.get_neighbors("A1")
    assert len(neighbors) == 1
    assert neighbors[0].to_node == "A2"


def test_site_map_duplicate_node_raises():
    sm = SiteMap()
    sm.add_node(SiteNode(node_id="A1", position=(0.0, 0.0, 0.0), type=NodeType.PICK))
    try:
        sm.add_node(SiteNode(node_id="A1", position=(1.0, 0.0, 0.0), type=NodeType.PLACE))
        assert False, "should have raised"
    except ValueError:
        pass
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_topology_site_map.py -v
```

预期：FAIL（`ModuleNotFoundError`）

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/topology/site_map.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class NodeType(str, Enum):
    PICK = "pick"
    PLACE = "place"
    STAGING = "staging"
    CHARGING = "charging"
    LOADING = "loading"
    UNLOADING = "unloading"


@dataclass
class SiteNode:
    node_id: str
    position: tuple[float, float, float]
    type: NodeType
    capacity: int = 1
    metadata: dict = field(default_factory=dict)


@dataclass
class SiteEdge:
    from_node: str
    to_node: str
    distance: float
    speed_limit: float = 1.0
    bidirectional: bool = True


class SiteMap:
    def __init__(self) -> None:
        self._nodes: dict[str, SiteNode] = {}
        self._adjacency: dict[str, list[SiteEdge]] = {}

    def add_node(self, node: SiteNode) -> None:
        if node.node_id in self._nodes:
            raise ValueError(f"duplicate node_id: {node.node_id}")
        self._nodes[node.node_id] = node
        self._adjacency.setdefault(node.node_id, [])

    def get_node(self, node_id: str) -> SiteNode:
        if node_id not in self._nodes:
            raise KeyError(f"unknown node_id: {node_id}")
        return self._nodes[node_id]

    def add_edge(self, edge: SiteEdge) -> None:
        if edge.from_node not in self._nodes:
            raise KeyError(f"unknown node_id: {edge.from_node}")
        if edge.to_node not in self._nodes:
            raise KeyError(f"unknown node_id: {edge.to_node}")
        self._adjacency[edge.from_node].append(edge)
        if edge.bidirectional:
            self._adjacency[edge.to_node].append(
                SiteEdge(edge.to_node, edge.from_node, edge.distance, edge.speed_limit, False)
            )

    def get_neighbors(self, node_id: str) -> list[SiteEdge]:
        if node_id not in self._adjacency:
            raise KeyError(f"unknown node_id: {node_id}")
        return self._adjacency[node_id]

    def all_nodes(self) -> list[SiteNode]:
        return list(self._nodes.values())
```

```python
# rcs/rcs/topology/__init__.py
from .site_map import SiteMap, SiteNode, SiteEdge, NodeType

__all__ = ["SiteMap", "SiteNode", "SiteEdge", "NodeType"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_topology_site_map.py -v
```

预期：PASS（3 tests passed）

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/topology/ rcs/tests/unit/test_topology_site_map.py
git commit -m "feat(rcs): add site map with node/edge structures"
```

---

## Task 4: A* 路径规划

**Files:**
- Create: `rcs/rcs/topology/pathfinder.py`
- Modify: `rcs/rcs/topology/__init__.py`
- Test: `rcs/tests/unit/test_topology_pathfinder.py`

**Interfaces:**
- Consumes: `SiteMap`（来自 Task 3）
- Produces:
  - `find_path(site_map, start_id, goal_id) -> list[str] | None`：返回节点 ID 序列

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_topology_pathfinder.py
from rcs.topology.site_map import SiteMap, SiteNode, SiteEdge, NodeType
from rcs.topology.pathfinder import find_path


def _build_grid():
    sm = SiteMap()
    sm.add_node(SiteNode("A", (0.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("B", (1.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("C", (2.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("D", (1.0, 1.0, 0.0), NodeType.STAGING))
    sm.add_edge(SiteEdge("A", "B", 1.0))
    sm.add_edge(SiteEdge("B", "C", 1.0))
    sm.add_edge(SiteEdge("A", "D", 1.5))
    sm.add_edge(SiteEdge("D", "C", 1.5))
    return sm


def test_find_path_direct():
    sm = _build_grid()
    path = find_path(sm, "A", "B")
    assert path == ["A", "B"]


def test_find_path_indirect():
    sm = _build_grid()
    path = find_path(sm, "A", "C")
    assert path is not None
    assert path[0] == "A"
    assert path[-1] == "C"
    assert len(path) == 3  # A->B->C


def test_find_path_no_route():
    sm = SiteMap()
    sm.add_node(SiteNode("X", (0.0, 0.0, 0.0), NodeType.STAGING))
    sm.add_node(SiteNode("Y", (5.0, 5.0, 0.0), NodeType.STAGING))
    assert find_path(sm, "X", "Y") is None
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_topology_pathfinder.py -v
```

预期：FAIL（`ModuleNotFoundError`）

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/topology/pathfinder.py
from __future__ import annotations
import heapq
from .site_map import SiteMap


def _heuristic(sm: SiteMap, a: str, b: str) -> float:
    pa = sm.get_node(a).position
    pb = sm.get_node(b).position
    return ((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2 + (pa[2] - pb[2]) ** 2) ** 0.5


def find_path(site_map: SiteMap, start_id: str, goal_id: str) -> list[str] | None:
    if start_id not in site_map.all_nodes() and start_id not in {n.node_id for n in site_map.all_nodes()}:
        return None
    if goal_id not in {n.node_id for n in site_map.all_nodes()}:
        return None
    open_heap: list[tuple[float, str]] = [(0.0, start_id)]
    came_from: dict[str, str] = {}
    g_score: dict[str, float] = {start_id: 0.0}
    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current == goal_id:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return list(reversed(path))
        for edge in site_map.get_neighbors(current):
            tentative = g_score[current] + edge.distance
            if tentative < g_score.get(edge.to_node, float("inf")):
                came_from[edge.to_node] = current
                g_score[edge.to_node] = tentative
                f_score = tentative + _heuristic(site_map, edge.to_node, goal_id)
                heapq.heappush(open_heap, (f_score, edge.to_node))
    return None
```

修改 `rcs/rcs/topology/__init__.py`：

```python
from .site_map import SiteMap, SiteNode, SiteEdge, NodeType
from .pathfinder import find_path

__all__ = ["SiteMap", "SiteNode", "SiteEdge", "NodeType", "find_path"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_topology_pathfinder.py -v
```

预期：PASS（3 tests passed）

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/topology/ rcs/tests/unit/test_topology_pathfinder.py
git commit -m "feat(rcs): add A* pathfinder for site map"
```

---

## Task 5: 调度策略（EDF + Utility）

**Files:**
- Create: `rcs/rcs/scheduler/policy.py`
- Create: `rcs/rcs/scheduler/__init__.py`
- Test: `rcs/tests/unit/test_scheduler_policy.py`

**Interfaces:**
- Consumes: `TaskNode`（来自 Task 1）
- Produces:
  - `UtilityWeights` dataclass（w1, w2, w3, w4）
  - `compute_utility(node, current_time, weights) -> float`

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_scheduler_policy.py
from datetime import datetime, timedelta
from rcs.dag.node import TaskNode, TaskType, SLOClass
from rcs.scheduler.policy import compute_utility, UtilityWeights


def test_compute_utility_urgent_task_higher():
    now = datetime(2026, 1, 1, 12, 0, 0)
    soon = TaskNode(task_id="t1", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=10))
    late = TaskNode(task_id="t2", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=600))
    weights = UtilityWeights()
    assert compute_utility(soon, now, weights) > compute_utility(late, now, weights)


def test_compute_utility_hard_slo_higher():
    now = datetime(2026, 1, 1, 12, 0, 0)
    hard = TaskNode(task_id="t1", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=60), slo_class=SLOClass.HARD)
    best = TaskNode(task_id="t2", type=TaskType.TRANSPORT, deadline=now + timedelta(seconds=60), slo_class=SLOClass.BEST_EFFORT)
    weights = UtilityWeights()
    assert compute_utility(hard, now, weights) > compute_utility(best, now, weights)


def test_compute_utility_no_deadline_returns_lowest():
    now = datetime(2026, 1, 1, 12, 0, 0)
    node = TaskNode(task_id="t1", type=TaskType.TRANSPORT, deadline=None)
    weights = UtilityWeights()
    score = compute_utility(node, now, weights)
    assert score < 0.0
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_scheduler_policy.py -v
```

预期：FAIL

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/scheduler/policy.py
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from ..dag.node import TaskNode, SLOClass


@dataclass
class UtilityWeights:
    w1: float = 0.5  # urgency (deadline proximity)
    w2: float = 0.3  # critical path bonus
    w3: float = 0.15  # device affinity
    w4: float = 0.05  # overrun penalty


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
```

```python
# rcs/rcs/scheduler/__init__.py
from .policy import compute_utility, UtilityWeights

__all__ = ["compute_utility", "UtilityWeights"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_scheduler_policy.py -v
```

预期：PASS

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/scheduler/ rcs/tests/unit/test_scheduler_policy.py
git commit -m "feat(rcs): add scheduler utility function with SLO weighting"
```

---

## Task 6: 设备分配器

**Files:**
- Create: `rcs/rcs/scheduler/allocator.py`
- Modify: `rcs/rcs/scheduler/__init__.py`
- Test: `rcs/tests/unit/test_scheduler_allocator.py`

**Interfaces:**
- Consumes: `TaskNode`, 候选设备列表（含类型、负载、当前利用率）
- Produces:
  - `DeviceCandidate` dataclass（device_id, type, load_capacity, current_utilization）
  - `select_device(task, candidates) -> DeviceCandidate | None`

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_scheduler_allocator.py
from rcs.dag.node import TaskNode, TaskType
from rcs.scheduler.allocator import DeviceCandidate, select_device


def test_select_device_prefers_closest():
    task = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    candidates = [
        DeviceCandidate(device_id="agv-01", type="diff_drive", load_capacity=100, current_utilization=0.5),
        DeviceCandidate(device_id="agv-02", type="diff_drive", load_capacity=100, current_utilization=0.1),
    ]
    selected = select_device(task, candidates)
    assert selected.device_id == "agv-02"


def test_select_device_no_candidate_returns_none():
    task = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    assert select_device(task, []) is None


def test_select_device_skips_overloaded():
    task = TaskNode(task_id="t1", type=TaskType.TRANSPORT)
    candidates = [
        DeviceCandidate(device_id="busy", type="diff_drive", load_capacity=100, current_utilization=0.95),
        DeviceCandidate(device_id="free", type="diff_drive", load_capacity=100, current_utilization=0.1),
    ]
    selected = select_device(task, candidates, max_utilization=0.9)
    assert selected.device_id == "free"
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_scheduler_allocator.py -v
```

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/scheduler/allocator.py
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
```

修改 `rcs/rcs/scheduler/__init__.py`：

```python
from .policy import compute_utility, UtilityWeights
from .allocator import DeviceCandidate, select_device

__all__ = ["compute_utility", "UtilityWeights", "DeviceCandidate", "select_device"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_scheduler_allocator.py -v
```

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/scheduler/ rcs/tests/unit/test_scheduler_allocator.py
git commit -m "feat(rcs): add device allocator with utilization scoring"
```

---

## Task 7: 订单 Pydantic 模型

**Files:**
- Create: `rcs/rcs/orders/models.py`
- Create: `rcs/rcs/orders/__init__.py`
- Test: `rcs/tests/unit/test_orders_models.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `OrderItem`（sku, quantity, weight_kg）
  - `Order`（order_id, type, items[], source_location, target_location, priority, deadline）

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_orders_models.py
from datetime import datetime
from rcs.orders.models import Order, OrderItem, OrderType


def test_order_creation():
    order = Order(
        order_id="O001",
        type=OrderType.INBOUND,
        items=[OrderItem(sku="A", quantity=1, weight_kg=10)],
        target_location="A1",
        priority=5,
        deadline=datetime(2026, 12, 1),
    )
    assert order.order_id == "O001"
    assert len(order.items) == 1


def test_order_type_enum():
    assert OrderType.INBOUND.value == "inbound"
    assert OrderType.OUTBOUND.value == "outbound"
    assert OrderType.TRANSFER.value == "transfer"
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_orders_models.py -v
```

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/orders/models.py
from __future__ import annotations
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class OrderType(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    TRANSFER = "transfer"


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(ge=1)
    weight_kg: float = Field(gt=0.0)


class Order(BaseModel):
    order_id: str
    type: OrderType
    items: list[OrderItem]
    source_location: str | None = None
    target_location: str | None = None
    priority: int = Field(default=5, ge=1, le=10)
    deadline: datetime | None = None
```

```python
# rcs/rcs/orders/__init__.py
from .models import Order, OrderItem, OrderType

__all__ = ["Order", "OrderItem", "OrderType"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_orders_models.py -v
```

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/orders/ rcs/tests/unit/test_orders_models.py
git commit -m "feat(rcs): add Order Pydantic models"
```

---

## Task 8: 订单 → DAG 拆解器

**Files:**
- Create: `rcs/rcs/orders/decomposer.py`
- Modify: `rcs/rcs/orders/__init__.py`
- Test: `rcs/tests/unit/test_orders_decomposer.py`

**Interfaces:**
- Consumes: `Order`（来自 Task 7）
- Produces:
  - `decompose_order(order) -> TaskDAG`：将订单拆解为 DAG

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_orders_decomposer.py
from rcs.orders.models import Order, OrderItem, OrderType
from rcs.orders.decomposer import decompose_order
from rcs.dag import TaskDAG, TaskType as TT


def test_decompose_inbound_single_sku():
    order = Order(
        order_id="O001",
        type=OrderType.INBOUND,
        items=[OrderItem(sku="A", quantity=1, weight_kg=10)],
        source_location="staging-01",
        target_location="A1",
    )
    dag = decompose_order(order)
    tasks = dag.topological_sort()
    assert len(tasks) >= 4  # agv-pick, robot-pick, agv-transport, robot-place


def test_decompose_invalid_order_raises():
    from rcs.dag.exceptions import DAGError
    order = Order(
        order_id="O002",
        type=OrderType.OUTBOUND,
        items=[],
        source_location="A1",
        target_location="staging-01",
    )
    try:
        decompose_order(order)
        assert False, "should have raised"
    except (DAGError, ValueError):
        pass
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_orders_decomposer.py -v
```

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/orders/decomposer.py
from __future__ import annotations
from ..dag import TaskDAG, TaskNode, TaskType, SLOClass
from ..dag.exceptions import DAGError
from .models import Order, OrderType


def decompose_order(order: Order) -> TaskDAG:
    if not order.items:
        raise DAGError(f"order {order.order_id} has no items")

    dag = TaskDAG()
    for idx, item in enumerate(order.items):
        prefix = f"{order.order_id}-{item.sku}-{idx}"

        agv_pick = TaskNode(
            task_id=f"{prefix}-agv-pick",
            type=TaskType.TRANSPORT,
            device_id="agv-01",
            params={"sku": item.sku, "location": order.source_location or "staging-01"},
            slo_class=SLOClass.SOFT,
        )
        robot_pick = TaskNode(
            task_id=f"{prefix}-robot-pick",
            type=TaskType.PICK,
            device_id="loader-01",
            params={"sku": item.sku, "weight_kg": item.weight_kg},
            slo_class=SLOClass.SOFT,
        )
        agv_transport = TaskNode(
            task_id=f"{prefix}-agv-transport",
            type=TaskType.TRANSPORT,
            device_id="agv-01",
            params={"sku": item.sku, "destination": order.target_location or "staging-01"},
            slo_class=SLOClass.SOFT,
        )
        robot_place = TaskNode(
            task_id=f"{prefix}-robot-place",
            type=TaskType.PLACE,
            device_id="loader-01",
            params={"sku": item.sku},
            slo_class=SLOClass.SOFT,
        )

        for node in [agv_pick, robot_pick, agv_transport, robot_place]:
            dag.add_node(node)
        dag.add_dependency(robot_pick.task_id, agv_pick.task_id)
        dag.add_dependency(agv_transport.task_id, robot_pick.task_id)
        dag.add_dependency(robot_place.task_id, agv_transport.task_id)

    return dag
```

> **注意**：所有拆解出的 TaskNode 默认使用 `SLOClass.SOFT`（与 `TaskNode` dataclass 默认值一致）。`OrderItem` 不暴露 `slo_class` 字段，由后续集成层根据业务上下文注入。

修改 `rcs/rcs/orders/__init__.py`：

```python
from .models import Order, OrderItem, OrderType
from .decomposer import decompose_order

__all__ = ["Order", "OrderItem", "OrderType", "decompose_order"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_orders_decomposer.py -v
```

预期：可能因 `slo_class` 字段调整需要修改测试或移除该参数。

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/orders/ rcs/tests/unit/test_orders_decomposer.py
git commit -m "feat(rcs): add order decomposer that produces TaskDAG"
```

---

## Task 9: 集成测试（订单 → DAG → 调度 → 派发）

**Files:**
- Create: `rcs/tests/integration/test_end_to_end_order_to_dispatch.py`

**Interfaces:**
- Consumes: 全部前序任务的产物
- Produces: 集成测试（mock 现有 dispatch_command）

- [ ] **Step 1: 写集成测试**

```python
# rcs/tests/integration/test_end_to_end_order_to_dispatch.py
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from rcs.orders import Order, OrderItem, OrderType, decompose_order
from rcs.scheduler import compute_utility, UtilityWeights, select_device, DeviceCandidate


def test_end_to_end_order_to_dag_to_selection():
    order = Order(
        order_id="O-INTEGRATION-001",
        type=OrderType.INBOUND,
        items=[OrderItem(sku="A", quantity=2, weight_kg=15)],
        source_location="staging-01",
        target_location="A1",
        priority=8,
        deadline=datetime.now() + timedelta(minutes=5),
    )

    dag = decompose_order(order)
    tasks = dag.topological_sort()
    assert len(tasks) >= 4

    weights = UtilityWeights()
    now = datetime.now()
    scored = [(t.task_id, compute_utility(t, now, weights)) for t in dag.get_ready_nodes()]
    assert len(scored) > 0
    assert all(score > 0 for _, score in scored)

    candidates = [
        DeviceCandidate(device_id="agv-01", type="diff_drive", load_capacity=100, current_utilization=0.3),
        DeviceCandidate(device_id="agv-02", type="diff_drive", load_capacity=100, current_utilization=0.5),
    ]
    selected = select_device(dag.get_node(tasks[0]), candidates)
    assert selected is not None
    assert selected.device_id == "agv-01"
```

- [ ] **Step 2: 跑测试确认通过**

```bash
cd rcs && pytest tests/integration/test_end_to_end_order_to_dispatch.py -v
```

预期：PASS（确认所有前序模块协同工作）

- [ ] **Step 3: 跑全量测试**

```bash
cd rcs && pytest -v
```

预期：所有已有测试 + 新增测试全部通过

- [ ] **Step 4: Commit**

```bash
git add rcs/tests/integration/test_end_to_end_order_to_dispatch.py
git commit -m "test(rcs): add end-to-end integration test for order→DAG→scheduler flow"
```

---

## Self-Review Checklist

✅ 8 个明确任务，每个独立可测试
✅ 全部为 2-5 分钟步长（写测试 → 跑 → 实现 → 验证 → commit）
✅ 不破坏 Global Constraints（不动 HAL / controllers / mqtt）
✅ 接口契约逐任务声明（`Consumes` / `Produces`）
✅ Task 9 集成测试覆盖全链路
✅ DRY / YAGNI / TDD / 频繁 commit

**已知局限**：
- Task 8 `decomposer` 假设固定设备 ID（`agv-01` / `loader-01`），真实环境应通过设备台账查询
- Task 6 设备选择未考虑类型匹配（任意 device 类型可被选），后续在 `DeviceCandidate.type` 增加匹配校验

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-23-rcs-prd-implementation.md`. Two execution options:

1. **Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?