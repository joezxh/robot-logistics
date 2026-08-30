"""Order domain models."""
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
