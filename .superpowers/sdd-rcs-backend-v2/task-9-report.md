# Task 9 Report: Shell 存储服务（in-memory + 可选 SQLite）

## Status: DONE_WITH_CONCERNS

## Commit(s)
| Hash | Message |
|------|---------|
| `582ac98` | `feat(rcs-backend): async shell store (memory + sqlite backends)` |

## TDD Evidence
### RED
```
$ cd rcs/backend && python -m pytest tests/unit/test_shell_store.py -v
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1
rootdir: D:\projects\robot-logic\rcs\backend
configfile: pyproject.toml
collected 0 items / 1 error

=================================== ERRORS ====================================
_______________ ERROR collecting tests/unit/test_shell_store.py _______________
ImportError while importing test module 'tests/unit/test_shell_store.py'.
Traceback (most recent call last):
...
tests\unit\test_shell_store.py:3: in <module>
    from rcs_backend.services.shell_store import (
E   ModuleNotFoundError: No module named 'rcs_backend.services'
=========================== short test summary info ============================
ERROR tests/unit/test_shell_store.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 1.20s ===============================
```

### GREEN
```
$ cd rcs/backend && python -m pytest tests/unit/test_shell_store.py -v
============================= test session starts =============================
collected 4 items

tests/unit/test_shell_store.py::test_memory_store_save_and_get PASSED    [ 25%]
tests/unit/test_shell_store.py::test_memory_store_get_missing_returns_none PASSED [ 50%]
tests/unit/test_shell_store.py::test_memory_store_list_sites PASSED      [ 75%]
tests/unit/test_shell_store.py::test_sqlite_store_persists PASSED        [100%]

============================== 4 passed in 0.22s ==============================
```

### Full suite
```
$ cd rcs/backend && python -m pytest -v
============================= test session starts =============================
collected 55 items

... (51 prior passing) ...
tests/unit/test_shell_store.py::test_memory_store_save_and_get PASSED     [ 58%]
tests/unit/test_shell_store.py::test_memory_store_get_missing_returns_none PASSED [ 60%]
tests/unit/test_shell_store.py::test_memory_store_list_sites PASSED       [ 61%]
tests/unit/test_shell_store.py::test_sqlite_store_persists PASSED         [ 63%]
... (site_grid / templates / validate all pass) ...

================================== FAILURES ===================================
___________________________ test_shell_put_then_get ___________________________
tests\integration\test_topology_api.py:21: in test_shell_put_then_get
    assert r.status_code == 200
E   assert 404 == 200
____________________ test_shell_put_oversized_returns_422 _____________________
tests\integration\test_topology_api.py:32: in test_shell_put_oversized_returns_422
    assert r.status_code == 422
E   assert 404 == 422
_________________________ test_shell_list_after_puts __________________________
tests\integration\test_topology_api.py:42: in test_shell_list_after_puts
    assert r.status_code == 200
E   assert 404 == 200

================== 3 failed, 52 passed, 4 warnings in 2.33s ==================
```

Summary: **4 new (Task 9) + 51 prior committed = 55 total; 52 passed, 3 failed (pre-existing Task 11 integration tests, out of scope)**

## Files Created/Modified

| File | Action | Lines |
|------|--------|-------|
| `rcs/backend/rcs_backend/services/__init__.py` | Create | +3 |
| `rcs/backend/rcs_backend/services/shell_store.py` | Create | +71 |
| `rcs/backend/tests/unit/test_shell_store.py` | Create | +51 |
| **Total** | | **+125 (3 files)** |

Both orchestrator-applied patches applied verbatim:
1. **Test-side patch** (`test_sqlite_store_persists`): added `assert out.metadata.get("site_id") == "site-1"` after the original `assert out is not None` so the test actually verifies the saved payload round-trips (not just non-null).
2. **`time` import hoist** (`shell_store.py`): `import time` placed at module top instead of inside `save_shell()` — better hygiene, same behavior.

## Concerns (if any)

1. **Full-suite count deviation from brief** — brief Step 6 expected "45 passed (41 prior + 4 new)". Actual: **52 passed, 3 failed, 55 collected**. The 3 failures are all in `tests/integration/test_topology_api.py` and are caused by an **out-of-scope** issue (Task 11's territory):
   - `tests/integration/test_topology_api.py` hits `PUT/GET /api/rcs/topology/shell/*` and expects 200/422/200, but the `topology_shell` router is still a stub `APIRouter()` in `rcs_backend/api/__init__.py` (Task 1 placeholder). All 3 tests get 404 instead.
   - These integration tests are untracked in the working tree (along with `rcs/backend/rcs_backend/api/topology_shell.py` which would resolve the issue) and are clearly Task 11's deliverable, not Task 9's. I did NOT touch them.
   - Task 11's brief includes a preamble that says "Pre-step: replace your stub in `rcs_backend/api/__init__.py`" — Task 11 will resolve these failures.

2. **Brief's "41 prior" baseline no longer matches repo state** — between plan write and Task 9 dispatch, two commits landed (`c9c54be` Task 7 markings + `d2ff2b5` Task 10 rcs_client), plus two tasks (Task 10 + partial Task 11) added untracked files. So:
   - Brief assumption: 41 tests already committed
   - Reality at dispatch: 47 tests committed (41 prior + 5 Task 7 + 6 Task 10 with all passing) + 4 untracked Task 11 integration tests failing + 4 my new Task 9 tests = 55 total.
   - Orchestrator may want to update the brief's expected baseline counts in future subagent dispatches.

3. **Brief's expected `pwd` and pytest invocation** — used `cd D:\projects\robot-logic\rcs\backend ; python -m pytest …` (PowerShell semicolon, not `&&`). Verified working.

4. **Pre-existing `docs/superpowers/plans/...-implementation.md` modification** observed in working tree (not staged, not committed) — contains a CRLF/LF warning from git. **Did not touch** (out of scope).

5. **`.superpowers/sdd-rcs-backend-v2/` scratch directory** untracked. Not staged. Not part of my brief.

6. **CRLF line-ending warnings** from git on every `git add`/`status` of my files — git wants to normalize to LF. This is repo-wide config (`core.autocrlf` setting). Did not impact commit success. Files committed with LF per git's normalization.

7. **Mid-task transient state** — during the run, an external process (likely a parallel agent) committed `c9c54be` (Task 7) and `d2ff2b5` (Task 10), and at one point deleted my staged Task 9 files from disk (the staged git entries remained). I detected this via `git status -s` showing "no changes added to commit" despite `git ls-files --stage` showing my entries, then re-wrote the 3 files from scratch (same content) and re-staged/re-committed cleanly. The final commit `582ac98` contains the correct 3 files.

## Self-Review

- **Completeness**: All 7 brief steps executed. RED captured, GREEN captured, full-suite captured, single commit on main produced, report written. Both orchestrator-applied patches applied verbatim (1 test-side metadata check, 1 `time` import hoist).
- **Quality**:
  - All public functions/methods have type hints (Protocol methods, class methods, `__init__`).
  - Uses `aiosqlite` per `pyproject.toml` dep (no new deps).
  - SQLite schema uses `INSERT OR REPLACE` for idempotent save + `site_id TEXT PRIMARY KEY` for uniqueness.
  - Pydantic v2 methods (`model_dump_json`, `model_validate_json`) used for SQLite payload serialization — no manual `json.dumps`/`json.loads`.
  - Memory store is a clean dict wrapper; no global state, no leaky abstractions.
- **Discipline** (no out-of-scope files touched):
  - ✅ Created exactly: `rcs_backend/services/__init__.py`, `rcs_backend/services/shell_store.py`, `tests/unit/test_shell_store.py`.
  - ✅ Did NOT touch `rcs_backend/__init__.py`, `rcs_backend/main.py`, `rcs_backend/models/*`, `rcs_backend/config.py`, `rcs_backend/topology/*`, `tests/conftest.py`, `rcs_backend/api/*`.
  - ✅ Commit only added my 3 files (verified via `git show 582ac98 --stat`).
- **Testing**:
  - 4 new tests pass on isolation (`tests/unit/test_shell_store.py`).
  - Full suite: 52 passed, 3 failed (failures are Task 11's pre-existing untracked integration tests, not mine).
  - No regressions in any previously-passing test (Task 1–8 + Task 10 all green).