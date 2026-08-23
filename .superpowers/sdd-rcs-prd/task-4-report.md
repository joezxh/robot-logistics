# Task 4 Report: A* 路径规划

**Status:** DONE
**Commit:** `a045389`
**Date:** 2026-08-23

## What Implemented

- `rcs/rcs/topology/pathfinder.py`: `find_path(site_map, start_id, goal_id) -> list[str] | None`
  - A* over `SiteMap` adjacency using `heapq` open set
  - Euclidean 3D heuristic (`((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2 + (pa[2]-pb[2])**2) ** 0.5`)
  - Returns reconstructed node-ID path on success; `None` when no route
- `rcs/rcs/topology/__init__.py`: re-export `find_path` in `__all__`
- `rcs/tests/unit/test_topology_pathfinder.py`: 3 tests per brief

## Test Results + TDD Evidence

### RED (pre-implementation)
- Command: `cd rcs && python -m pytest tests/unit/test_topology_pathfinder.py -v`
- Result: collection error → `ModuleNotFoundError: No module named 'rcs.topology.pathfinder'`
- Confirms test correctly exercises missing module.

### GREEN (post-implementation)
- Command: `cd rcs && python -m pytest tests/unit/test_topology_pathfinder.py -v`
- Result: `3 passed in 0.09s`
  - `test_find_path_direct` PASS
  - `test_find_path_indirect` PASS
  - `test_find_path_no_route` PASS

### Regression check
- Full unit suite: `71 passed in 0.63s` (was 68 before Task 4 — +3 new pathfinder tests, no regressions).

## Files Changed

| File | Change |
|---|---|
| `rcs/rcs/topology/pathfinder.py` | created |
| `rcs/rcs/topology/__init__.py` | modified — re-export `find_path` |
| `rcs/tests/unit/test_topology_pathfinder.py` | created |

Commit: `a045389 feat(rcs): add A* pathfinder for site map` (3 files, +74 / -1).

## Self-Review Findings

### Completeness
- Brief required: direct path test, indirect path test, no-route test. All 3 present.
- Interface signature matches brief exactly: `find_path(site_map, start_id, goal_id) -> list[str] | None`.
- `__init__.py` updated to expose `find_path` at package level.

### Quality
- Implementation matches the brief's reference impl verbatim, including the `start_id not in site_map.all_nodes() and start_id not in {n.node_id for n in site_map.all_nodes()}` membership check. YAGNI applied — no deviation.
- Heuristic is admissible (true Euclidean distance) — guarantees optimality for non-negative edge weights.
- Path reconstruction via `came_from` chain + `list(reversed(...))` — correct.

### Discipline
- Followed brief exactly: `from __future__ import annotations`, `heapq`, 1-level imports.
- TDD cycle observed: tests written first, RED confirmed, implementation written, GREEN confirmed.
- Commit subject matches brief: `feat(rcs): add A* pathfinder for site map`.
- Commit only staged the 3 target files (verified via `git status --short`); pre-existing unrelated modifications and untracked files were left untouched.

### Testing
- 3 new tests, all passing.
- 0 regressions across 71 unit tests.

### Minor observations (non-blocking)
- The first membership guard `start_id not in site_map.all_nodes() and start_id not in {n.node_id for n in site_map.all_nodes()}` is a tautology in the first disjunct (lists don't support `in` for value identity of dataclasses by default), but the second disjunct does the real work. The brief specified this verbatim so no fix applied.
- `site_map.get_neighbors(start_id)` will raise `KeyError` if `start_id` is not in the adjacency dict — but the membership guard above short-circuits before this is reached for valid unknown IDs, so behavior is safe for the tested cases.
- No new types added; no `__init__.py` change beyond what brief requires.

## Next Steps

- Task 5: 调度策略（EDF + utility）