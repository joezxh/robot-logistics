# Task 8 Report: 订单 → DAG 拆解器

## Status: DONE

## Commits

| Hash | Message |
|------|---------|
| `c4d319e` | feat(rcs): add order decomposer that produces TaskDAG |

## Test Summary

| Suite | Result |
|-------|--------|
| `pytest tests/unit/test_orders_decomposer.py -v` | **2 passed** |
| Full suite `pytest -v` | **146 passed, 4 failed** |

The 4 failures are pre-existing integration test issues (starlette/httpx version mismatch: `Client.__init__() got an unexpected keyword argument 'app'`). They fail on `main` regardless of this task's changes — identical to the Task 7 baseline (`144 passed, 4 failed` → `146 passed, 4 failed` after adding 2 decomposer tests).

## What Was Built

### Files Created

- `rcs/rcs/orders/decomposer.py` — `decompose_order(order) -> TaskDAG`
- `rcs/tests/unit/test_orders_decomposer.py` — 2 unit tests (verbatim from plan)

### Files Modified

- `rcs/rcs/orders/__init__.py` — re-exports `decompose_order`

### Decomposition Pattern (per SKU)

`agv-pick → robot-pick → agv-transport → robot-place` (4 TaskNodes, 3 edges).

| Step | TaskType | device_id | params |
|------|----------|-----------|--------|
| agv-pick | TRANSPORT | agv-01 | `{"sku", "location": source}` |
| robot-pick | PICK | loader-01 | `{"sku", "weight_kg"}` |
| agv-transport | TRANSPORT | agv-01 | `{"sku", "destination": target}` |
| robot-place | PLACE | loader-01 | `{"sku"}` |

Task IDs follow `{order_id}-{sku}-{idx}-{step}` so multiple items in the same order never collide.

### Design Notes

- **SLO defect fix**: `OrderItem` (Task 7) has no `slo_class` field. All decomposed `TaskNode`s use `slo_class=SLOClass.SOFT` — the same value `TaskNode` would default to anyway, but spelled out explicitly for clarity. Verified with `Grep`: zero references to `item.slo_class` in the new code.
- **Empty items** → `DAGError` (typed; plan spec accepted both `DAGError` and `ValueError`, we chose the typed one — also matches the test's `except (DAGError, ValueError):`).
- **Source/destination fallback**: `source_location` / `target_location` default to `"staging-01"` when null (matches plan spec).
- **1-level import surface**: consumers do `from rcs.orders.decomposer import decompose_order` (per code-organization guidance).

## Concerns

None.

## Completeness / Quality / Discipline / Testing

- **Completeness**: All spec items from the plan implemented. Pattern, error handling, and imports match the brief verbatim.
- **Quality**: Clean pure function with type hints and a module-level docstring explaining the SKU pattern and the SLO rationale (so future readers don't reintroduce `item.slo_class`).
- **Discipline**: TDD followed — tests written first, red (ModuleNotFoundError on `rcs.orders.decomposer`), then implementation, then green. Single-purpose commit, message in project convention.
- **Testing**: 2/2 decomposer tests pass. Full suite has only the 4 known pre-existing integration failures (unrelated to this task).
