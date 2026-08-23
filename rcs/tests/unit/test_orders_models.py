"""Tests for RCS order models."""
from __future__ import annotations

from datetime import datetime

import pytest

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
