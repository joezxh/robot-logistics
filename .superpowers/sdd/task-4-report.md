# Task 4 Report — pytest for presets/runtime/api

## Status
DONE

## Commit
- **Hash (7 位)**: `1a49897`
- **Message**: `test(scenes): add preset/runtime/api tests`
- **Author**: `cursor <cursor@local>`
- **Files** (3 added, 176 insertions):
  - `simulation/backend/tests/test_scene_presets.py` (5 tests, 35 lines)
  - `simulation/backend/tests/test_runtime_load_scene.py` (7 tests, 69 lines)
  - `simulation/backend/tests/test_scenes_api.py` (7 tests, 72 lines)

Note: Brief stated `HEAD = 2d23310` but the working tree at task start was actually at
`74196a3` (docs/spec commit) on `main`. Commit `1a49897` is the only new commit in
this task. (Brief's `2d23310` reference is stale.)

## Step 4 — Run new tests

Command (PYTHONPATH set because PowerShell cannot invoke bare `pytest`, used
`python -m pytest`):

```
cd /d d:\projects\robot-logic\simulation && set PYTHONPATH=. && \
  python -m pytest backend/tests/test_scene_presets.py \
                     backend/tests/test_runtime_load_scene.py \
                     backend/tests/test_scenes_api.py -v
```

Output (verbatim from pytest):

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0 -- C:\Program Files\Python311\python.exe
cachedir: .pytest_cache
Test order randomisation NOT enabled. Enable with --random-order or --random-order-bucket=<bucket_type>
rootdir: d:\projects\robot-logic\simulation\backend
configfile: pytest.ini
plugins: anyio-4.14.0, langsmith-0.7.38, asyncio-0.23.5, cov-7.0.0, mock-3.15.1, random-order-1.2.0, timeout-2.4.0, xdist-3.8.0, time-machine-2.19.0
asyncio: mode=Mode.AUTO
collecting ... collected 19 items

backend\tests\test_scene_presets.py::test_three_scenes_present PASSED    [  5%]
backend\tests\test_scene_presets.py::test_each_preset_has_required_fields PASSED [ 10%]
backend\tests\test_scene_presets.py::test_each_preset_has_minimum_one_site_device_task PASSED [ 15%]
backend\tests\test_scene_presets.py::test_get_scene_raises_for_unknown PASSED [ 21%]
backend\tests\test_scene_presets.py::test_pallet_has_pallet_forklift_devices PASSED [ 26%]
backend\tests\test_runtime_load_scene.py::test_reset_clears_devices_tasks_logs PASSED [ 31%]
backend\tests\test_runtime_load_scene.py::test_load_scene_pallet_registers_expected_devices PASSED [ 36%]
backend\tests\test_runtime_load_scene.py::test_load_scene_box_loads_correctly PASSED [ 42%]
backend\tests\test_runtime_load_scene.py::test_load_scene_bag_loads_correctly PASSED [ 47%]
backend\tests\test_runtime_load_scene.py::test_load_scene_unknown_raises_keyerror PASSED [ 52%]
backend\tests\test_runtime_load_scene.py::test_load_scene_clears_previous_state PASSED [ 57%]
backend\tests\test_runtime_load_scene.py::test_scene_kpi_returns_dict PASSED [ 63%]
backend\tests\test_scenes_api.py::test_list_scenes_returns_three PASSED  [ 68%]
backend\tests\test_scenes_api.py::test_load_scene_pallet_succeeds PASSED [ 73%]
backend\tests\test_scenes_api.py::test_load_scene_unknown_returns_404 PASSED [ 78%]
backend\tests\test_scenes_api.py::test_current_scene_404_when_none_loaded PASSED [ 84%]
backend\tests\test_scenes_api.py::test_current_scene_returns_preset_when_loaded PASSED [ 89%]
backend\tests\test_scenes_api.py::test_scene_kpi_returns_snapshot PASSED [ 94%]
backend\tests\test_scenes_api.py::test_device_create_accepts_pallet_forklift_type PASSED [100%]

============================= 19 passed in 1.44s ==============================
```

Summary: **19 passed in 1.44s** (5 + 7 + 7).

## Step 5 — Run existing tests for regression

Command:

```
cd /d d:\projects\robot-logic\simulation && set PYTHONPATH=. && \
  python -m pytest backend/tests/test_api.py -v
```

Output (verbatim):

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-8.0.1, pluggy-1.6.0 -- C:\Program Files\Python311\python.exe
cachedir: .pytest_cache
rootdir: d:\projects\robot-logic\simulation\backend
configfile: pytest.ini
plugins: anyio-4.14.0, langsmith-0.7.38, asyncio-0.23.5, cov-7.0.0, mock-3.15.1, random-order-1.2.0, timeout-2.4.0, xdist-3.8.0, time-machine-2.19.0
asyncio: mode=Mode.AUTO
collecting ... collected 19 items

backend\tests\test_api.py::test_root PASSED                              [  5%]
backend\tests\test_api.py::test_devices_lists_seed PASSED                [ 10%]
backend\tests\test_api.py::test_create_task_happy_path PASSED            [ 15%]
backend\tests\test_api.py::test_create_task_rejects_unknown_device PASSED [ 21%]
backend\tests\test_api.py::test_logs_returns_array PASSED                [ 26%]
backend\tests\test_api.py::test_metrics_prometheus_text PASSED           [ 31%]
backend\tests\test_api.py::test_alerts_returns_shape PASSED              [ 36%]
backend\tests\test_api.py::test_rollback_unknown_task_404 PASSED         [ 42%]
backend\tests\test_api.py::test_bulk_rollback_validates_devices PASSED   [ 47%]
backend\tests\test_api.py::test_bulk_rollback_success PASSED             [ 52%]
backend\tests\test_api.py::test_stats_endpoint_returns_breakdown PASSED  [ 57%]
backend\tests\test_api.py::test_control_round_trip PASSED                [ 63%]
backend\tests\test_api.py::test_list_sites_seeded PASSED                 [ 68%]
backend\tests\test_api.py::test_create_and_delete_site PASSED            [ 73%]
backend\tests\test_api.py::test_create_duplicate_site_conflict PASSED    [ 78%]
backend\tests\test_api.py::test_patch_site PASSED                        [ 84%]
backend\tests\test_api.py::test_register_and_delete_custom_device PASSED [ 89%]
backend\tests\test_api.py::test_register_duplicate_conflict PASSED       [ 94%]
backend\tests\test_api.py::test_patch_device PASSED                      [100%]

============================= 19 passed in 1.69s ==============================
```

Summary: **19 passed in 1.69s** (no regression).

## Acceptance Checklist

- [x] `test_scene_presets.py` created — 5 tests, all PASSED
- [x] `test_runtime_load_scene.py` created — 7 tests, all PASSED
- [x] `test_scenes_api.py` created — 7 tests (with autouse fixture), all PASSED
- [x] Existing `test_api.py` — 19 tests still PASSED (no regression)
- [x] Only 3 test files committed (`git show --stat HEAD` confirms)

## Concerns / Notes

1. **PowerShell quoting**: `pytest` is not on PATH and PowerShell cannot parse
   `&&` / parentheses in commit message / Python `-c` strings. Resolved by
   using `cmd.exe /c "..."` for shell ops and a `python` script file for the
   `git commit --amend` step (the first commit picked up a stale prepared
   message; amended to the brief's verbatim message via Python wrapper).
2. **PYTHONPATH**: brief hinted to set `PYTHONPATH=.` if imports fail. The
   `simulation/backend/pytest.ini` is `configfile`, but `backend` is still not
   on sys.path automatically when running from `simulation/`. Setting
   `PYTHONPATH=.` lets `from backend.…` resolve correctly. Existing `tests/`
   conftest also does `sys.path.insert(0, REPO_ROOT)` for safety.
3. **HEAD drift**: brief referenced `2d23310` but actual starting HEAD was
   `74196a3` (the spec commit on `main`). The only commit added by this task
   is `1a49897`; no other source files were touched.
4. **`test_scenes_api.py` uses `TestClient(app)` directly** (not the `client`
   fixture in `conftest.py`) — matches the brief verbatim. The fixture is
   autouse-resetting `runtime` after each test, so cross-test isolation holds.
5. **Test naming typo**: brief correctly used `test_list_scenes_returns_three`
   (no typo) — followed exactly.
