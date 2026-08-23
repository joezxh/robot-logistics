"""Tests for order -> TaskDAG decomposer."""
from __future__ import annotations

from rcs.orders.models import Order, OrderItem, OrderType
from rcs.orders.decomposer import decompose_order
from rcs.dag import TaskDAG, TaskType as TT
from rcs.dag.exceptions import DAGError


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
