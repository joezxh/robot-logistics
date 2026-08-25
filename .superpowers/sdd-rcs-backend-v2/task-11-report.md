# Task 11 Report: API router — topology_shell (GET/PUT)

## Status: DONE

## Commit(s)
| Hash | Message |
|------|---------|
| `d2ddc08` | `feat(rcs-backend): topology_shell REST endpoints (GET/PUT) with validation` |

## TDD Evidence

### RED

Captured during implementation (commenting out the `@router.get/put` decorators in `rcs_backend/api/topology_shell.py` to simulate the pre-Task-11 stub state, then re-running pytest):

```
============================= test session starts =============================
collecting ... collected 4 items

tests/integration/test_topology_api.py::test_shell_get_missing_returns_404 PASSED [ 25%]
tests/integration/test_topology_api.py::test_shell_put_then_get FAILED   [ 50%]
tests/integration/test_topology_api.py::test_shell_put_oversized_returns_422 FAILED [ 75%]
tests/integration/test_topology_api.py::test_shell_list_after_puts FAILED [100%]

================================== FAILURES ===================================
___________________________ test_shell_put_then_get ___________________________
tests\integration\test_topology_api.py:21: in test_shell_put_then_get
    assert r.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
____________________ test_shell_put_oversized_returns_422 _____________________
tests\integration\test_topology_api.py:32: in test_shell_put_oversized_returns_422
    assert r.status_code == 422
E   assert 404 == 422
E    +  where 404 = <Response [404 Not Found]>.status_code
_________________________ test_shell_list_after_puts __________________________
tests\integration\test_topology_api.py:42: in test_shell_list_after_puts
    assert r.status_code == 200
E   assert 404 == 200
E    +  where 404 = <Response [404 Not Found]>.status_code
=================== 3 failed, 1 passed, 4 warnings in 1.29s ===================
```

Stub `APIRouter()` returns 404 for unhandled paths. `test_shell_get_missing_returns_404` passes with both stub and real router (real router also returns 404 for missing site), so the RED discriminator is the other 3 tests. Uncommenting the decorators flips them to GREEN.

### GREEN (integration only)

```
collecting ... collected 4 items

tests/integration/test_topology_api.py::test_shell_get_missing_returns_404 PASSED [ 25%]
tests/integration/test_topology_api.py::test_shell_put_then_get PASSED   [ 50%]
tests/integration/test_topology_api.py::test_shell_put_oversized_returns_422 PASSED [ 75%]
tests/integration/test_topology_api.py::test_shell_list_after_puts PASSED [100%]

======================== 4 passed, 4 warnings in 0.25s ========================
```

### Full suite (at Task 11 commit d2ddc08; rerun on current HEAD)

Brief expected: `51 prior + 4 new = 55 passed`. Captured exactly:

```
======================= 55 passed, 4 warnings in 0.98s ========================
```

Test count breakdown:
- 51 pre-existing tests (dxf_parser 6, dxf_to_shell 5, floor_shell_model 5, markings 5, rcs_client 6, shell_store 4, site_grid_model 6, templates 8, validate 6)
- 4 new integration tests in `tests/integration/test_topology_api.py` (test_shell_get_missing_returns_404, test_shell_put_then_get, test_shell_put_oversized_returns_422, test_shell_list_after_puts)

## Files Created/Modified

| File | Lines | Action |
|------|-------|--------|
| `rcs/backend/rcs_backend/api/__init__.py` | 21 (was 22) | Modified — replaced `topology_shell = APIRouter()` stub with `from rcs_backend.api.topology_shell import router as topology_shell` re-export |
| `rcs/backend/rcs_backend/api/topology_shell.py` | 53 | Created — verbatim brief content (3 routes: list, get, put) |
| `rcs/backend/tests/integration/__init__.py` | 0 | Created — empty package marker |
| `rcs/backend/tests/integration/conftest.py` | 7 | Created — sys.path insert for `rcs/backend/` (orchestrator-patched `parent.parent.parent`) |
| `rcs/backend/tests/integration/test_topology_api.py` | 44 | Created — verbatim brief content with orchestrator-patched `-t11` site_id suffixes |

Per-step brief compliance:
- **Step 1**: `api/__init__.py` — verbatim brief content applied. Docstring text matches brief exactly (replaces the original Task 1 docstring with the brief's "Task 1 stubs all six router names. Tasks 11-16 each edit THIS file…"). The other 5 stubs (`topology_grid`, `topology_import`, `topology_export`, `topology_templates`, `orders`) remain as `APIRouter()` for Tasks 12-16 to replace.
- **Step 2**: `api/topology_shell.py` — verbatim brief content. Module-level `_store = MemoryShellStore()` singleton (as brief specified); `_get_store()` dependency factory.
- **Step 3**: `tests/integration/__init__.py` — empty file.
- **Step 4**: `tests/integration/conftest.py` — orchestrator-patched `_ROOT = Path(__file__).parent.parent.parent` (brief's `.parent.parent` would have pointed to `tests/` instead of `rcs/backend/`, breaking imports).
- **Step 5**: `tests/integration/test_topology_api.py` — verbatim brief content with orchestrator-patched `-t11` site_id suffixes (`nope-t11`, `site-A-t11`, `site-B-t11`, `x-t11`, `y-t11`, `z-t11`).

## Concerns

1. **Module-level `_store` singleton** (already noted in brief). State leaks between tests. Benign in Task 11 because all 4 tests use unique `site_id` values. **Tasks 12-16 should be aware** — if they share the same store via the `_get_store()` dependency, cross-test pollution is possible. Brief's own docstring on `tests/integration/conftest.py` flags this for Tasks 12-16.

2. **Environment defect encountered and worked around** (documented for orchestrator awareness, NOT a Task 11 code issue):
   - The local environment had `httpx==0.28.1` installed globally, but `starlette==0.27.0` (shipped with fastapi 0.104.0) calls `super().__init__(app=self.app, ...)` which was removed in httpx 0.28. This made `TestClient(create_app())` fail at fixture setup with `TypeError: Client.__init__() got an unexpected keyword argument 'app'`.
   - Workaround: downgraded global httpx to `httpx==0.27.2` (`pip install httpx==0.27.2`). This is an environment-level fix (no project file was modified).
   - Side effect: the same httpx downgrade fixed 4 pre-existing failing tests in `tests/unit/test_rcs_client.py` (Task 10 work) that had been failing for the same reason. So the full suite now reports `55 passed` exactly as the brief expected, instead of the prior `47 passed + 4 failed`.

3. **Pre-existing Task 9 dependency**: brief's Step 2 imports `from rcs_backend.services.shell_store import MemoryShellStore`, but `rcs_backend/services/` was created by Task 9. At Task 11's dispatch time, Task 9's files existed on disk as untracked work-in-progress but were not yet committed. By the time Task 11's commit landed, the orchestrator had committed Task 9 (`582ac98`) and the import resolved cleanly. Flag for any future task with similar cross-task file dependencies: confirm the upstream task is committed before dispatch.

4. **Brief-verbatim `_store` singleton vs. future-task compatibility**: Task 13+ working tree later replaced `_store = MemoryShellStore()` with `default_memory_store()` factory function (visible in `git log` history between Task 11 and HEAD). This is the orchestrator's preferred cleanup and does not affect the Task 11 commit.

## Self-Review

- **Completeness**: All 8 brief steps executed. Step 1-5 files created/modified exactly as brief specifies (with orchestrator's 3 patches applied verbatim). Step 6 (integration GREEN, 4 passed) captured. Step 7 (full suite, 55 passed) captured. Step 8 (commit on `main`) completed — commit hash `d2ddc08`.
- **Quality**: All 5 in-scope files use brief-verbatim content. Type hints present on all public functions per Global Constraints. Module-level singleton `_store` follows brief's exact pattern.
- **Discipline**:
  - Confirmed only the 5 brief-listed files were touched.
  - **Did NOT modify**: `main.py`, `conftest.py` (root), `rcs_backend/__init__.py`, `rcs_backend/models/*`, `rcs_backend/config.py`, `rcs_backend/services/*`, `rcs_backend/topology/*`, or `api/rcs_client.py` (Task 10's).
  - Did NOT silently fix any plan defect. The only environment intervention (httpx downgrade) was a pip-install at the global env level, not a project file change.
- **Testing**: RED captured (3 failures + 1 incidental pass with stub); GREEN captured (4/4 pass with real router); full suite 55 passed matches brief's expectation exactly.
