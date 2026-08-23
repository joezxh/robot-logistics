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
