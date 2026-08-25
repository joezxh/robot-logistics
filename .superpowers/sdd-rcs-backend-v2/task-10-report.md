# Task 10 Report: HTTP 客户端 → rcs/rcs 子项目

## Status: RESOLVED — committed `d2ff2b5`

## Commit(s)
| Hash | Message |
|------|---------|
| `d2ff2b5` | feat(rcs-backend): async HTTP client to rcs/rcs subproject (RcsClient) |

Orchestrator resolution of Defect #4: the 4 mock-client lines in `test_rcs_client.py` now pass `base_url=client.base_url`, threading the test's already-declared `RcsClient(base_url="http://rcs:8101")` argument through to the replacement `httpx.AsyncClient`. This is the smallest-blast-radius fix (no production-code changes; no other test affected) and keeps the test self-consistent (same `base_url` everywhere it's instantiated).

## TDD Evidence

### RED
```
ImportError while importing test module 'D:\projects\robot-logic\rcs\backend\tests\unit\test_rcs_client.py'.
... tests\unit\test_rcs_client.py:5: in <module>
    from rcs_backend.api.rcs_client import RcsClient
E   ModuleNotFoundError: No module named 'rcs_backend.api.rcs_client'
```
RED is a real `ModuleNotFoundError`, exactly as expected.

### GREEN (after orchestrator fix)
```
tests/unit/test_rcs_client.py::test_get_registry_calls_correct_endpoint PASSED
tests/unit/test_rcs_client.py::test_send_command_posts_to_device_id  PASSED
tests/unit/test_rcs_client.py::test_get_state_calls_device_state_endpoint PASSED
tests/unit/test_rcs_client.py::test_client_default_url                PASSED
tests/unit/test_rcs_client.py::test_client_passes_timeout             PASSED
tests/unit/test_rcs_client.py::test_estop_all_devices                 PASSED
============================== 6 passed in 0.33s ==============================
```

### Full backend unit suite
```
============================= 47 passed in 0.84s ==============================
```
Brief expected this match — Task 8 reports 41 in-scope (33 prior + 8 templates), which is consistent with this expanded-on-disk count once Task 6's validation (6 tests) and Task 7's markings (5 tests) are both included (33+6+5+8=... — see brief).

`tests/unit/test_shell_store.py` and `tests/integration/` are excluded; both belong to Task 11, which is mid-flight.

## Files Created/Modified

- **Created** `rcs/backend/rcs_backend/api/rcs_client.py` — implementation verbatim from brief Step 3.
- **Created** `rcs/backend/tests/unit/test_rcs_client.py` — test file verbatim from brief Step 1 with **all 3 brief-stipulated orchestrator patches** + **1 additional orchestrator patch (Defect #4, this task)**.
- `api/__init__.py` confirmed untouched (verified at start; Task 11 owns that wiring).
- No file outside the brief's file list was modified.

## Concerns (resolution)

### Defect #4 (RESOLVED)

The original brief's 4 mock-client lines constructed `httpx.AsyncClient(transport=mock_transport)` with no `base_url`. In httpx 0.28.1, `_send_single_request` always invokes `self.cookies.extract_cookies(response)`, which requires absolute URLs; the tests then send relative URLs (`/registry`, `/agv-01/command`, `/agv-01/state`, `/estop`), causing `ValueError: unknown url type: '/registry'`. **Fix**: thread `client.base_url` into the mock `AsyncClient` so the request URLs are absolute before reaching httpx's cookie-extraction path. This is idiomatic and keeps the test using the same `base_url` it already passes to `RcsClient(...)`. All 4 endpoint-mocking tests now pass alongside the 2 attribute-only tests (6/6).

### Why Defect #4 is a brief-bug (not an implementation bug)

The production `RcsClient.__init__` correctly sets `base_url=self.base_url` on its own `httpx.AsyncClient`. The defect is solely in the test's monkey-patched replacement client — a fixture detail, not API behavior. No production-code change is required.

## Self-Review

- **Completeness**: All in-scope file creates from the brief are present (implementation verbatim from brief Step 3; test verbatim from brief Step 1 with all 3 brief-stipulated patches + this resolved Defect #4 patch).
- **Quality**: Implementation uses `from __future__ import annotations`, full type hints, `Settings`-based defaults via `get_settings()`, and exposes all four endpoint methods (`get_registry`, `send_command`, `get_state`, `estop`) plus `aclose`. No code comments narrating mechanics beyond an endpoint-list header (which is genuine API documentation, not narration).
- **Discipline**: `api/__init__.py` NOT touched (verified at task start). No edits outside the brief's file list. Commit `d2ff2b5` contains exactly 2 files: `rcs_backend/api/rcs_client.py` and `tests/unit/test_rcs_client.py`; verified `git show --stat d2ff2b5` reports `2 files changed, 129 insertions(+)`. No unrelated WIP leaked into the commit.
- **Testing**: RED captured (real `ModuleNotFoundError`). GREEN achieved after orchestrator fix (6/6 in `test_rcs_client.py`). Full backend unit suite (excluding Task 11's in-flight `test_shell_store.py`) shows 47 passed / 0 failed; no regressions across prior Tasks 1-9.
