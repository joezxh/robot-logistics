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

