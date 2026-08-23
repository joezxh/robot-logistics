"""REST endpoints for orders (scenario-aware)."""
from __future__ import annotations
import uuid
import time
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

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
    dag: list[dict]
    created_at: float


_store: dict[str, OrderResponse] = {}


@router.post("/orders", response_model=OrderResponse, status_code=202)
async def create_order(req: OrderCreateRequest) -> OrderResponse:
    order_id = f"ORD-{uuid.uuid4().hex[:8]}"
    # Minimal DAG: pick → move → place → confirm
    dag = [
        {"node_id": "pick", "depends_on": []},
        {"node_id": "move", "depends_on": ["pick"]},
        {"node_id": "place", "depends_on": ["move"]},
        {"node_id": "confirm", "depends_on": ["place"]},
    ]
    out = OrderResponse(
        order_id=order_id,
        dag=dag,
        created_at=time.time(),
    )
    _store[order_id] = out
    return out


@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str) -> OrderResponse:
    o = _store.get(order_id)
    if o is None:
        raise HTTPException(status_code=404, detail=f"order '{order_id}' not found")
    return o
