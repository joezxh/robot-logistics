# Task 7 Report: Order Pydantic Models

## Status: DONE

## Commits

| Hash | Message |
|------|---------|
| `5324dba` | feat(rcs): add Order Pydantic models |

## Test Summary

| Suite | Result |
|-------|--------|
| `pytest tests/unit/test_orders_models.py -v` | **2 passed** |
| Full suite `pytest -v` | **144 passed, 4 failed** |

The 4 failures are pre-existing integration test issues (starlette/httpx version mismatch: `Client.__init__() got an unexpected keyword argument 'app'`). They fail on the main branch regardless of this task's changes.

## What Was Built

### Files Created

- `rcs/rcs/orders/__init__.py` — Package init, re-exports `Order`, `OrderItem`, `OrderType`
- `rcs/rcs/orders/models.py` — Domain models
- `rcs/tests/unit/test_orders_models.py` — 2 unit tests

### Models

| Model | Key Fields |
|-------|-----------|
| `OrderType` | `INBOUND`, `OUTBOUND`, `TRANSFER` (str Enum) |
| `OrderItem` | `sku: str`, `quantity: int (ge=1)`, `weight_kg: float (gt=0.0)` |
| `Order` | `order_id`, `type`, `items: list[OrderItem]`, `source_location`, `target_location`, `priority (1-10, default 5)`, `deadline` |

### Design Notes

- `OrderItem` deliberately has **no `slo_class` field** — Task 8's decomposer uses `SLOClass.SOFT` as default, not a model field.
- All optional fields (`source_location`, `target_location`, `deadline`) default to `None`.
- Pydantic v2 style with `Field(...)` constraints.
- `from __future__ import annotations` for forward references.

## Concerns

None.

## Completeness / Quality / Discipline

- **Completeness**: All spec items implemented. Tests match brief exactly.
- **Quality**: Clean models, proper type hints, valid Pydantic v2 usage.
- **Discipline**: TDD followed — tests written first, failed, then implemented.
