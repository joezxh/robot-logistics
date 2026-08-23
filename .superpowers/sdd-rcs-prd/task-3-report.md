# Task 3 Report: 站点地图数据结构

**Status:** DONE

## What Implemented

- `rcs/rcs/topology/site_map.py` — site map data structures:
  - `NodeType(str, Enum)` with the six values from the brief: `PICK`, `PLACE`, `STAGING`, `CHARGING`, `LOADING`, `UNLOADING`
  - `@dataclass SiteNode` with `node_id`, `position: tuple[float, float, float]`, `type`, `capacity: int = 1`, `metadata: dict = field(default_factory=dict)`
  - `@dataclass SiteEdge` with `from_node`, `to_node`, `distance`, `speed_limit: float = 1.0`, `bidirectional: bool = True`
  - `class SiteMap` with `add_node(node)`, `get_node(node_id)`, `add_edge(edge)`, `get_neighbors(node_id)`, `all_nodes()`:
    - `add_node` raises `ValueError` on duplicate `node_id`
    - `get_node` / `get_neighbors` raise `KeyError` on unknown `node_id`
    - `add_edge` validates both endpoints; for a `bidirectional` edge, automatically appends the reverse edge with `bidirectional=False` so `get_neighbors` is symmetric
- `rcs/rcs/topology/__init__.py` — re-exports `SiteMap`, `SiteNode`, `SiteEdge`, `NodeType`
- `rcs/tests/unit/test_topology_site_map.py` — 3 tests, verbatim from the brief

## Test Results

### RED (before implementation)

```
$ cd rcs && python -m pytest tests/unit/test_topology_site_map.py -v
============================= test session starts =============================
collected 0 items / 1 error

=================================== ERRORS ====================================
____________ ERROR collecting tests/unit/test_topology_site_map.py ____________
ImportError while importing test module '...test_topology_site_map.py'.
...
tests\unit\test_topology_site_map.py:1: in <module>
    from rcs.topology.site_map import SiteMap, SiteNode, SiteEdge, NodeType
E   ModuleNotFoundError: No module named 'rcs.topology'
============================== 1 error in 0.88s ===============================
```

### GREEN (after implementation)

```
$ cd rcs && python -m pytest tests/unit/test_topology_site_map.py -v
============================= test session starts =============================
collected 3 items

tests\unit\test_topology_site_map.py ...                                 [100%]

============================== 3 passed in 0.07s ==============================
```

Full `tests/unit` regression check: **68 passed in 0.58s** (up from 65, due to the 3 new tests; no other tests changed, no regressions).

## TDD Evidence

- RED: `ModuleNotFoundError: No module named 'rcs.topology'` (test collection error)
- GREEN: `3 passed in 0.07s`

## Files Changed

- `rcs/rcs/topology/__init__.py` (new, 4 lines)
- `rcs/rcs/topology/site_map.py` (new, 60 lines)
- `rcs/tests/unit/test_topology_site_map.py` (new, 31 lines)

## Self-Review Findings

- **Completeness:** All three dataclasses + enum and all five `SiteMap` methods present, with the exact field names, defaults, and value semantics specified in the brief.
- **Quality:** Names match behavior; clean dataclass + plain-class split; one responsibility per file. Reverse edge stored with `bidirectional=False` so re-adding the same forward edge doesn't compound into a 4-edge cycle.
- **Discipline (YAGNI):** No extra methods beyond spec (no `validate()`, no `remove_*`, no `has_node`). Imports restricted to stdlib `dataclasses` and `enum`.
- **Style:** Matches `rcs/rcs/state/command.py` (`from __future__ import annotations`, dataclass with `field(default_factory=dict)`, `class X(str, Enum)`).
- **File length:** `site_map.py` is 60 lines, well below the 150-line soft cap.
- **Tests:** All 3 tests verify real behavior — no mocks, no monkeypatching, no fixtures beyond the bare instances. Pristine output, no warnings.
- **No regressions:** Full `tests/unit` suite = 68 passed.

## Commit

- `7bd07a3` — feat(rcs): add site map with node/edge structures
