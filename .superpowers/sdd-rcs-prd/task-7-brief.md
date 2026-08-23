## Task 7: 订单 Pydantic 模型

**Files:**
- Create: `rcs/rcs/orders/models.py`
- Create: `rcs/rcs/orders/__init__.py`
- Test: `rcs/tests/unit/test_orders_models.py`

**Interfaces:**
- Consumes: 无
- Produces:
  - `OrderItem`（sku, quantity, weight_kg）
  - `Order`（order_id, type, items[], source_location, target_location, priority, deadline）

- [ ] **Step 1: 写失败的测试**

```python
# rcs/tests/unit/test_orders_models.py
from datetime import datetime
from rcs.orders.models import Order, OrderItem, OrderType


def test_order_creation():
    order = Order(
        order_id="O001",
        type=OrderType.INBOUND,
        items=[OrderItem(sku="A", quantity=1, weight_kg=10)],
        target_location="A1",
        priority=5,
        deadline=datetime(2026, 12, 1),
    )
    assert order.order_id == "O001"
    assert len(order.items) == 1


def test_order_type_enum():
    assert OrderType.INBOUND.value == "inbound"
    assert OrderType.OUTBOUND.value == "outbound"
    assert OrderType.TRANSFER.value == "transfer"
```

- [ ] **Step 2: 跑测试确认失败**

```bash
cd rcs && pytest tests/unit/test_orders_models.py -v
```

- [ ] **Step 3: 写实现**

```python
# rcs/rcs/orders/models.py
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
```

```python
# rcs/rcs/orders/__init__.py
from .models import Order, OrderItem, OrderType

__all__ = ["Order", "OrderItem", "OrderType"]
```

- [ ] **Step 4: 跑测试确认通过**

```bash
cd rcs && pytest tests/unit/test_orders_models.py -v
```

- [ ] **Step 5: Commit**

```bash
git add rcs/rcs/orders/ rcs/tests/unit/test_orders_models.py
git commit -m "feat(rcs): add Order Pydantic models"
```

---

