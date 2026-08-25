# Task 5 Report: DXF → FloorShell 转换器

## Status: FAILED

## Commit(s)

(none — the plan defect below prevented a green build, so per the discipline rule "DO NOT silently fix the plan" and "DO NOT commit changes unless explicitly asked … it is VERY IMPORTANT to only commit when explicitly asked", no commit was produced; orchestrator must decide the path forward before any commit lands on `main`.)

| Hash | Message |
|------|---------|
| (none) | (none) |

## Root cause (plan defect)

The brief's Step 3 implementation starts with:

```python
bounds = Bounds(w=0.0, d=0.0)
```

However, `rcs_backend.models.floor_shell.Bounds` is defined as:

```python
class Bounds(BaseModel):
    w: float = Field(gt=0)
    d: float = Field(gt=0)
```

`pydantic_core` rejects `Bounds(w=0.0, d=0.0)` with:

```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Bounds
w    Input should be greater than 0 [type=greater_than, input_value=0.0, ...]
d    Input should be greater than 0 [type=greater_than, input_value=0.0, ...]
```

This raises on the **very first call** to `dxf_to_shell`, before any wall / zone / facility / floor logic runs, so all 5 new tests fail with the same root error.

The brief's `test_empty_doc_yields_empty_shell` further expects `shell.bounds.w == 0`, which is **inconsistent** with `Bounds.w: float = Field(gt=0)`: even if validation were bypassed, the brief's reference value `0` is incompatible with the model constraint `gt=0`.

The plain reading of Task 2's `Bounds` model is "the floor always has positive width and depth". Task 5's brief implicitly assumes an empty shell is allowed to carry `bounds = (0, 0)`. These two assumptions are mutually exclusive.

**Root cause**: plan defect — the brief's `dxf_to_shell` skeleton and `Bounds` model definition conflict. The brief needs either:
1. Relax `Bounds.w` / `Bounds.d` from `Field(gt=0)` to `Field(ge=0)` in `rcs_backend/models/floor_shell.py` (out-of-scope for Task 5); **and** change brief test to `shell.bounds.w == pytest.approx(0.0)` instead of `== 0`.
2. Or, keep the model strict but change `dxf_to_shell` to construct `Bounds` via `Bounds.model_construct(w=0.0, d=0.0)` (or equivalent validation bypass) **and** change the empty-doc assertion expectation to match the model semantics (e.g. `len(shell.walls) == 0 and len(shell.zones) == 0` only).

Either option requires a plan patch. Per the brief's "DO NOT … modify any file outside the brief's file list" rule and the implementer discipline "DO NOT silently fix the plan", the change is left for the orchestrator.

## TDD Evidence

### RED (Step 2, before Step 3 — captured exactly as expected)

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0
plugins: langsmith-0.7.38, asyncio-0.23.5, cov-7.0.0, mock-3.15.1, random-order-1.2.0, timeout-2.4.0, xdist-3.8.0, time-machine-2.19.0, anyio-4.14.2
asyncio: mode=Mode.STRICT
collecting ... collected 0 items / 1 error

=================================== ERRORS ====================================
______________ ERROR collecting tests/unit/test_dxf_to_shell.py _______________
ImportError while importing test module 'D:\projects\robot-logic\rcs\backend\tests\unit\test_dxf_to_shell.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
C:\Users\joezxh\AppData\Roaming\Python\Python311\site-packages\_pytest\python.py:538: in importtestmodule
    mod = import_path(path, mode=importmode, root=config.rootpath)
C:\Users\joezxh\AppData\Roaming\Python\Python311\site-packages\_pytest\pathlib.py:566: in import_path
    importlib.import_module(module_name)
C:\Program Files\Python311\Lib\importlib\__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
<frozen importlib._bootstrap>:1206: in _gcd_import
    ???
<frozen importlib._bootstrap>:1178: in _find_and_load
    ???
<frozen importlib._bootstrap>:1149: in _find_and_load_unlocked
    ???
<frozen importlib._bootstrap>:690: in _load_unlocked
    ???
C:\Users\joezxh\AppData\Roaming\Python\Python311\site-packages\_pytest\assertion\rewrite.py:178: in exec_module
    exec(co, module.__dict__)
tests\unit\test_dxf_to_shell.py:2: in <module>
    from rcs_backend.topology.dxf_parser import DxfDocument, DxfEntity
rcs_backend\topology\__init__.py:8: in <module>
    from rcs_backend.topology.dxf_to_shell import dxf_to_shell
E   ModuleNotFoundError: No module named 'rcs_backend.topology.dxf_to_shell'
=========================== short test summary info ============================
ERROR tests/unit/test_dxf_to_shell.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 0.84s ===============================
```

This matches brief Step 2 expectation exactly.

### GREEN-attempt (Step 4 — did NOT pass; reported here for transparency)

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0 -- C:\Program Files\Python311\python.exe
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
plugins: langsmith-0.7.38, asyncio-0.23.5, cov-7.0.0, mock-3.15.1, random-order-1.2.0, timeout-2.4.0, xdist-3.8.0, time-machine-2.19.0, anyio-4.14.2
asyncio: mode=Mode.STRICT
collecting ... collected 5 items

tests/unit/test_dxf_to_shell.py::test_walls_layer_becomes_wall_segments FAILED [ 20%]
tests/unit/test_dxf_to_shell.py::test_zones_layer_becomes_zones_with_ref FAILED [ 40%]
tests/unit/test_dxf_to_shell.py::test_facilities_layer_becomes_facilities FAILED [ 60%]
tests/unit/test_dxf_to_shell.py::test_floor_layer_sets_bounds FAILED     [ 80%]
tests/unit/test_dxf_to_shell.py::test_empty_doc_yields_empty_shell FAILED [100%]

================================== FAILURES ===================================
___________________ test_walls_layer_becomes_wall_segments ____________________
tests\unit\test_dxf_to_shell.py:16: in test_walls_layer_becomes_wall_segments
    shell = dxf_to_shell(doc)
rcs_backend\topology\dxf_to_shell.py:15: in dxf_to_shell
    bounds = Bounds(w=0.0, d=0.0)
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Bounds
E   w
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
E   d
E     Input should be greater than 0 [type=greater_than, input_value=greater_than, input_value=0.0, input_type=float]
___________________ test_zones_layer_becomes_zones_with_ref ___________________
tests\unit\test_dxf_to_shell.py:27: in test_zones_layer_becomes_zones_with_ref
    shell = dxf_to_shell(doc)
rcs_backend\topology\dxf_to_shell.py:15: in dxf_to_shell
    bounds = Bounds(w=0.0, d=0.0)
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Bounds
E   w
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
E   d
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
__________________ test_facilities_layer_becomes_facilities __________________
tests\unit\test_dxf_to_shell.py:39: in test_facilities_layer_becomes_facilities
    shell = dxf_to_shell(doc)
rcs_backend\topology\dxf_to_shell.py:15: in dxf_to_shell
    bounds = Bounds(w=0.0, d=0.0)
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Bounds
E   w
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
E   d
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
________________________ test_floor_layer_sets_bounds _________________________
tests\unit\test_dxf_to_shell.py:48: in test_floor_layer_sets_bounds
    shell = dxf_to_shell(doc)
rcs_backend\topology\dxf_to_shell.py:15: in dxf_to_shell
    bounds = Bounds(w=0.0, d=0.0)
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Bounds
E   w
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
E   d
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
______________________ test_empty_doc_yields_empty_shell ______________________
tests\unit\test_dxf_to_shell.py:54: in test_empty_doc_yields_empty_shell
    shell = dxf_to_shell(_doc([]))
rcs_backend\topology\dxf_to_shell.py:15: in dxf_to_shell
    bounds = Bounds(w=0.0, d=0.0)
E   pydantic_core._pydantic_core.ValidationError: 2 validation errors for Bounds
E   w
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
E   d
E     Input should be greater than 0 [type=greater_than, input_value=0.0, input_type=float]
=========================== short test summary info ============================
FAILED tests/unit/test_dxf_to_shell.py::test_walls_layer_becomes_wall_segments
FAILED tests/unit/test_dxf_to_shell.py::test_zones_layer_becomes_zones_with_ref
FAILED tests/unit/test_dxf_to_shell.py::test_facilities_layer_becomes_facilities
FAILED tests/unit/test_dxf_to_shell.py::test_floor_layer_sets_bounds - pydant...
FAILED tests/unit/test_dxf_to_shell.py::test_empty_doc_yields_empty_shell - p...
============================== 5 failed in 0.77s ===============================
```

### Full suite (Step 5 — partial; same green-attempt run with the new file present)

```
======================== 5 failed, 17 passed in 0.88s =========================
```

The 17 previously-passing tests still pass; only the 5 new tests in `test_dxf_to_shell.py` fail, every one with the same `Bounds(w=0.0, d=0.0)` validation error.

After this report was started, all in-scope files added by the subagent were reverted (`topology/__init__.py` restored via `git checkout`, `dxf_to_shell.py` and `test_dxf_to_shell.py` deleted) so the working tree is clean except for the pre-existing plan-doc modifications the orchestrator already tolerates (per `progress.md` Task 4 note: "Subagent respected scope; acknowledged pre-existing plan doc mods"). The on-disk state matches the last green commit (`2c63902`) plus the `task-5-report.md` and `task-5-green-attempt.txt` artifacts in `.superpowers/sdd-rcs-backend-v2/`.

## Files Created/Modified (line counts)

| File | Lines | Action | Status |
|------|-------|--------|--------|
| `rcs/backend/rcs_backend/topology/__init__.py` | 31 (→32 after Step 0 edit) | Modified (Step 0: replace `dxf_to_shell` placeholder with real import) | **Reverted** to committed state — no longer modified |
| `rcs/backend/rcs_backend/topology/dxf_to_shell.py` | ~80 | Created (Step 3: brief-verbatim code) | **Deleted** after GREEN failed |
| `rcs/backend/tests/unit/test_dxf_to_shell.py` | 60 | Created (Step 1: brief-verbatim test) | **Deleted** after GREEN failed |
| `.superpowers/sdd-rcs-backend-v2/task-5-report.md` | this file | Created | Retained |
| `.superpowers/sdd-rcs-backend-v2/task-5-green-attempt.txt` | full pytest output | Captured | Retained (companion artifact) |

The brief's Step 0 placeholder replacement (`from rcs_backend.topology.dxf_to_shell import dxf_to_shell`) **was successfully applied** during the attempt; the implementation module was deleted along with everything else, so the placeholder is back in place on `main` to match the pre-Task-5 contract for downstream tasks.

## Concerns

1. **Plan defect (blocking)**: `Bounds(w=0.0, d=0.0)` (brief's `dxf_to_shell` skeleton) is rejected by `Bounds(w: float = Field(gt=0))` (`rcs_backend/models/floor_shell.py`). The same conflict means brief test `test_empty_doc_yields_empty_shell`'s assertion `shell.bounds.w == 0` is unsatisfiable under the strict model. This cannot be resolved within Task 5's file scope.

2. **Suggested follow-up (orchestrator decision required)**:
   - **Option A (smallest, model-side)**: change `Bounds.w` and `Bounds.d` from `Field(gt=0)` to `Field(ge=0)` in `rcs_backend/models/floor_shell.py` (out-of-scope for Task 5 — requires either widening Task 5's scope or a separate micro-patch). Then update brief test to use `pytest.approx(0.0)` instead of `0`.
   - **Option B (implementation-side, in-scope)**: change brief's `dxf_to_shell` to build an empty `Bounds` via `Bounds.model_construct(w=0.0, d=0.0)` (Pydantic validation bypass) and update brief test to assert only `walls == []` and `zones == []` (drop the bounds assertion, since under the strict model an empty shell cannot carry a valid `Bounds`).
   - Either way, the plan's Task 5 brief needs to be reissued. The implementer must not silently rewrite the plan.

3. **No silent fix applied**: per implementer discipline ("DO NOT silently fix the plan"), no out-of-scope edit to `models/floor_shell.py`, no test changes beyond verbatim, no `model_construct` workaround in `dxf_to_shell.py`.

## Self-Review

- **Completeness**: All steps executed in order through Step 4. Step 5 partial run captured (shows 17 prior + 5 new failed = 22 total collected, 17 passed, 5 failed). Step 6 commit intentionally skipped because GREEN was not achieved; the brief's discipline rules forbid committing broken code on `main`.
- **Quality**: The verbatim brief code was used exactly as supplied for `dxf_to_shell.py` and `test_dxf_to_shell.py`. The only deviation was reverting those files back out after GREEN failed, to keep `main` clean.
- **Discipline**: Explicitly confirmed no out-of-scope files were modified at any point during this task. The pre-existing modification to `docs/superpowers/plans/2026-08-23-rcs-backend-v2-implementation.md` is not mine (visible in git status prior to my work, per `progress.md` Task 4 note). After reverting, the only on-disk changes in this task are the two artifacts in `.superpowers/sdd-rcs-backend-v2/`.
- **Testing**: RED was captured exactly as the brief expected (`ModuleNotFoundError: No module named 'rcs_backend.topology.dxf_to_shell'`). GREEN attempt produced 5 failures, all from the same root cause (brief's `Bounds(w=0.0, d=0.0)` skeleton vs. model's `Field(gt=0)`). Pre-existing 17-test suite is unaffected. Both pytest invocations were from `cd rcs/backend && python -m pytest tests/unit/test_dxf_to_shell.py -v` and `cd rcs/backend && python -m pytest -v` as specified.
