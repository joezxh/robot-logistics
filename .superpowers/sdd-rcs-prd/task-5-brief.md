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

