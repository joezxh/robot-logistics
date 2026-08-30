"""REST endpoints for orders (scenario-aware).

Orders are decomposed into a real DAG by the embedded control runtime's
``decompose_order`` (pick → transport → place → confirm per item, with SLO
classes and per-scenario routing). The result is persisted via the order
repository (in-memory or PostgreSQL depending on ``Settings.storage``).
"""
from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rcs.services.control.control_orders_decomposer import decompose_order
from rcs.models.control_orders import Order, OrderItem as CtrlOrderItem
from rcs.services.control.order_repository import repo

router = APIRouter()


class OrderItem(BaseModel):
    ref: str
    quantity: int = Field(gt=0)


class OrderCreateRequest(BaseModel):
    scenario_id: str = "ecommerce"
    items: list[OrderItem]
    priority: int = Field(default=5, ge=1, le=10)
    deadline: Optional[float] = None


class OrderResponse(BaseModel):
    order_id: str
    status: str = "queued"
    scenario_id: Optional[str] = None
    priority: int = 5
    items: list[dict] = []
    dag: list[dict] = []
    created_at: float


@router.post("/orders", response_model=OrderResponse, status_code=202)
async def create_order(req: OrderCreateRequest) -> OrderResponse:
    ctrl_items = [
        CtrlOrderItem(
            sku=i.ref.split(":", 1)[-1],
            quantity=i.quantity,
            weight_kg=max(0.1, i.quantity * 1.0),
        )
        for i in req.items
    ]
    import uuid as _uuid

    ctrl_order = Order(
        order_id=f"ORD-{_uuid.uuid4().hex[:8]}",
        type="outbound",
        items=ctrl_items,
        priority=req.priority,
    )
    dag = decompose_order(ctrl_order)

    tasks = [
        {
            "node_id": node.task_id,
            "task_type": node.type.value,
            "slo_class": node.slo_class.value,
            "depends_on": list(node.dependencies),
        }
        for node in dag._nodes.values()
    ]
    item_dicts = [{"ref": i.ref, "quantity": i.quantity} for i in req.items]

    record = await repo.create(
        scenario_id=req.scenario_id,
        priority=req.priority,
        deadline=req.deadline,
        items=item_dicts,
        tasks=tasks,
    )
    return OrderResponse(
        order_id=record["order_id"],
        status=record["status"],
        scenario_id=record["scenario_id"],
        priority=record["priority"],
        items=record["items"],
        dag=record["tasks"],
        created_at=record["created_at"],
    )


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str) -> OrderResponse:
    record = await repo.get(order_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"order '{order_id}' not found")
    return OrderResponse(
        order_id=record["order_id"],
        status=record["status"],
        scenario_id=record.get("scenario_id"),
        priority=record.get("priority", 5),
        items=record.get("items", []),
        dag=record.get("tasks", []),
        created_at=record["created_at"],
    )


@router.get("/orders")
async def list_orders(status: Optional[str] = None):
    """List orders, optionally filtered by status (queued/running/done/failed)."""
    return await repo.list_orders(status=status)


@router.put("/orders/{order_id}/status")
async def advance_status(order_id: str, body: dict):
    """Advance order lifecycle status (queued -> running -> done/failed/cancelled)."""
    target = body.get("status", "running")
    if not await repo.advance_status(order_id, target):
        raise HTTPException(404, "order not found")
    return {"order_id": order_id, "status": target}


@router.get("/orders/{order_id}/tasks")
async def order_tasks(order_id: str):
    """Return DAG task rows for monitoring (status, deps)."""
    record = await repo.get(order_id)
    if record is None:
        raise HTTPException(404, "order not found")
    return record["tasks"]


@router.put("/orders/{order_id}/tasks/{node_id}/status")
async def set_task_status(order_id: str, node_id: str, body: dict):
    """Update individual DAG task status."""
    target = body.get("status", "done")
    ok = await repo.set_task_status(order_id, node_id, target)
    if not ok:
        raise HTTPException(404, "task not found")
    return {"order_id": order_id, "node_id": node_id, "status": target}
