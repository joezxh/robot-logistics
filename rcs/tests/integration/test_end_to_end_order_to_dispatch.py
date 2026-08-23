"""End-to-end integration test: Order → DAG → scheduler → device selection.

Exercises the full pre-dispatch pipeline by walking a real ``Order`` through
``decompose_order``, scoring the ready nodes via ``compute_utility``, and
finally dispatching the first ready task to a candidate device via
``select_device``. No mocks are used anywhere in the chain — every component
is exercised against its real implementation to validate that the seams
between modules (orders / dag / scheduler) hold under a realistic scenario.
"""
from datetime import datetime, timedelta

from rcs.orders import Order, OrderItem, OrderType, decompose_order
from rcs.scheduler import (
    DeviceCandidate,
    UtilityWeights,
    compute_utility,
    select_device,
)


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

    # Propagate the order's deadline onto each decomposed task so the
    # scheduler can reason about urgency; the decomposer (Task 8) does not
    # carry the order deadline into the TaskNodes itself.
    for task_id in tasks:
        node = dag.get_node(task_id)
        node.deadline = order.deadline

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