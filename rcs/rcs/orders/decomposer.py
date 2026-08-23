"""Order -> TaskDAG decomposer.

Decomposes a high-level ``Order`` (with one or more ``OrderItem`` rows) into a
``TaskDAG`` that the scheduler can dispatch.

Pattern per SKU
---------------
For each item we emit the canonical inbound/outbound micro-flow::

    agv-pick -> robot-pick -> agv-transport -> robot-place

That is four nodes per SKU, chained by three edges. The SKU index disambiguates
task IDs across items in the same order so the resulting DAG has no duplicate
``task_id`` values.

SLO class
---------
``OrderItem`` does **not** expose an ``slo_class`` field (see Task 7). All
decomposed tasks therefore default to ``SLOClass.SOFT`` (which is also the
``TaskNode`` dataclass default). Higher layers may override this at dispatch
time if business context demands a tighter SLO.
"""
from __future__ import annotations

from ..dag import SLOClass, TaskDAG, TaskNode, TaskType
from ..dag.exceptions import DAGError
from .models import Order


def decompose_order(order: Order) -> TaskDAG:
    """Decompose ``order`` into a ``TaskDAG`` of executable tasks.

    Each item in ``order.items`` becomes a 4-node linear chain:
    ``agv-pick -> robot-pick -> agv-transport -> robot-place``.

    Raises
    ------
    DAGError
        If ``order.items`` is empty (no work to decompose).
    """
    if not order.items:
        raise DAGError(f"order {order.order_id} has no items")

    dag = TaskDAG()
    source = order.source_location or "staging-01"
    destination = order.target_location or "staging-01"

    for idx, item in enumerate(order.items):
        prefix = f"{order.order_id}-{item.sku}-{idx}"

        agv_pick = TaskNode(
            task_id=f"{prefix}-agv-pick",
            type=TaskType.TRANSPORT,
            device_id="agv-01",
            params={"sku": item.sku, "location": source},
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
            params={"sku": item.sku, "destination": destination},
            slo_class=SLOClass.SOFT,
        )
        robot_place = TaskNode(
            task_id=f"{prefix}-robot-place",
            type=TaskType.PLACE,
            device_id="loader-01",
            params={"sku": item.sku},
            slo_class=SLOClass.SOFT,
        )

        for node in (agv_pick, robot_pick, agv_transport, robot_place):
            dag.add_node(node)
        dag.add_dependency(robot_pick.task_id, agv_pick.task_id)
        dag.add_dependency(agv_transport.task_id, robot_pick.task_id)
        dag.add_dependency(robot_place.task_id, agv_transport.task_id)

    return dag
