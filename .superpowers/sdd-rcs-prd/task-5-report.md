# Task 5 Report: 调度策略（EDF + utility）

## What implemented
Created `rcs/rcs/scheduler/` package with the EDF-style utility function
described in `.superpowers/sdd-rcs-prd/task-5-brief.md`.

- `UtilityWeights` dataclass with defaults `w1=0.5, w2=0.3, w3=0.15, w4=0.05`.
- `compute_utility(node, current_time, weights) -> float` implements:
  `utility = w1*urgency + w2*slo_bonus + w3*affinity_score - w4*overrun_penalty`
  - `urgency`: `-1.0` when `deadline is None`, else `1 / max(time_to_deadline_seconds, 1.0)`.
  - `slo_bonus`: `HARD=1.0, SOFT=0.5, BEST_EFFORT=0.0`.
  - `affinity_score`: `1.0` if `device_id` set, else `0.5`.
  - `overrun_penalty`: `0.0` (placeholder for future overrun tracking).
- Package `__init__.py` re-exports both symbols.

## Test results + TDD evidence
- TDD red: `pytest tests/unit/test_scheduler_policy.py` initially failed with
  `ModuleNotFoundError: No module named 'rcs.scheduler'` (collected 0 items / 1 error).
- TDD green after implementation: 3/3 passing in `test_scheduler_policy.py`.
- Full regression suite
  (`test_dag_node`, `test_dag_graph`, `test_topology_site_map`,
  `test_topology_pathfinder`, `test_scheduler_policy`): **18/18 passing**, no regressions.
- New tests cover:
  - EDF ordering: urgent deadline (10s) ranks above late deadline (600s).
  - SLO weighting: HARD > BEST_EFFORT at equal deadlines.
  - No-deadline: returns negative score (urgency=-1.0 dominates default weights).

## Files changed
- Created `rcs/rcs/scheduler/policy.py` (37 lines).
- Created `rcs/rcs/scheduler/__init__.py` (3 lines).
- Created `rcs/tests/unit/test_scheduler_policy.py` (28 lines).
- Commit `9db684f`: `feat(rcs): add scheduler utility function with SLO weighting`.

## Self-review findings
- **Completeness**: All brief items delivered; package exports match public API.
- **Quality**: Style matches neighboring modules (`dag/node.py`, `topology/`):
  `from __future__ import annotations`, dataclass, Enum-keyed dispatch, relative
  `..dag.node` import as required.
- **Discipline**: Strict TDD (red → green), no scope creep, no narrating comments.
- **Testing**: 3/3 new + 18/18 regression — no impact on prior tasks.
- Note: `overrun_penalty` is intentionally hard-coded to `0.0` as the brief
  defines it as a placeholder; future overrun tracking will plug in here.
