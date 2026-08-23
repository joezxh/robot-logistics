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

