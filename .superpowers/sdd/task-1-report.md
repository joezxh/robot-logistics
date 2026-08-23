# Task 1 Report: SimRenderer 基础实现

**Status:** DONE_WITH_CONCERNS
**Date:** 2026-08-20

## What I implemented

Created `SimRenderer` class that provides MuJoCo offscreen RGB/Depth rendering
with graceful fallback to zero-frame placeholders when MuJoCo is unavailable.

### Files changed

- `simulation/backend/rcs_env/renderer.py` (created, 94 lines)
- `simulation/backend/tests/test_renderer.py` (created, 38 lines)

### Public API

- `SimRenderer(model, data, camera_name="default", width=320, height=240)`
- `render() -> {"rgb": HxWx3 uint8, "depth": HxWx1 float32}`
- `SimRenderer.available() -> bool` (static)

### Deviations from the brief (intentional)

1. **Hard-coded `0` → `camera_id` in `mjv_updateScene`.** The brief hard-coded
   `0` as the camera argument while also defining `_get_camera_id()`. Used
   `camera_id` instead so the lookup helper is actually exercised — leaving it
   in but unused would be dead code.
2. **Removed unused `from mujoco import mjr` import** — dead code in the brief
   that would generate a linter warning. All other mujoco symbols are accessed
   via the `import mujoco` module reference, matching the existing pattern in
   `engine.py`.

## TDD Evidence

### RED — failing test before implementation

Command:
```
cd D:/projects/robot-logic/simulation && python -m pytest backend/tests/test_renderer.py -v
```

Output (relevant):
```
collected 2 items

backend\tests\test_renderer.py FF                                        [100%]

================================== FAILURES ===================================
_________________________ test_sim_renderer_available _________________________
    def test_sim_renderer_available():
>       from rcs_env.renderer import SimRenderer
E       ModuleNotFoundError: No module named 'rcs_env.renderer'
backend\tests\test_renderer.py:10: ModuleNotFoundError
_______________________ test_sim_renderer_returns_dict ________________________
    def test_sim_renderer_returns_dict():
>       from rcs_env.renderer import SimRenderer
E       ModuleNotFoundError: No module named 'rcs_env.renderer'
backend\tests\test_renderer.py:17: ModuleNotFoundError
=========================== short test summary info ==========================
FAILED backend\tests\test_renderer.py::test_sim_renderer_available - ModuleNo...
FAILED backend\tests\test_renderer.py::test_sim_renderer_returns_dict - Modul...
============================== 2 failed in 1.57s ==============================
```

Expected and matches the brief's stated expectation:
`module 'rcs_env.renderer' has no attribute 'SimRenderer'`
(close enough — module didn't exist at all, so attribute lookup couldn't
even start).

### GREEN — passing tests after implementation

Command:
```
cd D:/projects/robot-logic/simulation && python -m pytest backend/tests/test_renderer.py -v
```

Output (relevant):
```
collected 2 items

backend\tests\test_renderer.py .s                                        [100%]

======================== 1 passed, 1 skipped in 0.79s =========================
```

The `available()` test passes (returns `False` because `mujoco` is not
installed in this environment). The `render()` test correctly skips via
`pytest.skip("MuJoCo not available")`. The skip is a graceful degradation,
not a test failure — the brief explicitly mandates this pattern.

## What I tested

| Suite | Result |
|---|---|
| `test_renderer.py` only | 1 passed, 1 skipped (MuJoCo unavailable) |
| Full `backend/tests/` | 114 passed, 1 skipped, 17 pre-existing warnings |

The 17 warnings are all pre-existing (Pydantic `class-based config`
deprecation in `backend/config.py:4`, and `aiosqlite` event-loop warnings
from existing API/MQTT tests). None introduced by the new code.

The MuJoCo-dependent render path is **not exercised locally** because
the `mujoco` package is not installed in this environment. The unit
tests will exercise it on CI / a workstation with MuJoCo installed
via `pip install mujoco`.

## Commit

- `e572464` — `feat(simulation): add SimRenderer for offscreen camera rendering`

## Self-review findings

- **Completeness:** Both interfaces from the brief are present. Zero-frame
  fallback matches the "when MuJoCo is unavailable" requirement.
- **Quality:** Names describe what they do (`_zero_frames`, `_get_camera_id`,
  `available`). Code follows the existing pattern in `engine.py` — module-level
  try/except around the optional `mujoco` import.
- **Discipline:** Did not extend the API beyond the brief. The `_get_camera_id`
  helper is called from `render()` so it's actually used, not dead code.
- **Testing:** Tests assert real behavior (return type, dict keys, dtype) —
  not mock behavior. The skip path is an explicit contract with the test, not
  a workaround for an unimplemented case.

## Concerns

1. **MuJoCo rendering path is not exercised locally.** The `mujoco` package
   isn't installed in this environment, so `test_sim_renderer_returns_dict`
   always skips. The implementation follows the official MuJoCo offscreen
   rendering recipe and should work, but I cannot verify it here. Recommend
   that downstream Task 2 (CameraSetWrapper) add a CI workflow with MuJoCo
   installed so the full path gets coverage.
2. **MjrContext is created inside `render()`.** This allocates a new
   offscreen GL-ish context per call, which is inefficient for high-frequency
   camera streams. The brief specifies this exact code, so I kept it as-is —
   but if perf becomes an issue, the fix is to cache the context across
   `render()` calls. Not in scope for this task.
3. **No `MjrContext.close()` / `MjvScene.free()` cleanup.** Same reasoning —
   the brief's transcription doesn't include resource cleanup, so I didn't
   add it. Could be revisited if memory leaks become observable.

## Fix Report

**Date:** 2026-08-20
**Reviewer:** Task 1 review
**Trigger:** Important finding on render-path test coverage + Minor on unused import

### What I changed

**`simulation/backend/tests/test_renderer.py` — `test_sim_renderer_returns_dict`**
Added three assertions that pin down the contract documented in the brief and
the docstring (`{"rgb": HxWx3 uint8, "depth": HxWx1 float32}`):

```python
assert isinstance(result["depth"], np.ndarray)
assert result["depth"].dtype == np.float32
assert result["rgb"].shape == (240, 320, 3)
assert result["depth"].shape == (240, 320, 1)
```

This catches the regression class the reviewer flagged: a wrong shape passed
into `mjr_readPixels` would previously have been accepted by the existing
assertions (which only checked `isinstance` and `rgb.dtype`). Now any drift
in either the rgb or depth buffer shape — the dimension that `mjr_readPixels`
actually requires — fails the test immediately.

The dimensions `(240, 320, 3)` / `(240, 320, 1)` match `SimRenderer's`
defaults (`height=240, width=320`) and the brief's documented contract, so
they reflect a real invariant rather than a test-only convention.

**`simulation/backend/rcs_env/renderer.py` — removed unused import**
Dropped `from typing import Any` (line 7). The module doesn't use `Any` for
any parameter typing or alias — it relies on PEP 604 union syntax and
`dict[str, np.ndarray]` annotations under `from __future__ import annotations`,
so the import was dead.

### Test results (TDD evidence)

**Focused test:**
```
cd D:/projects/robot-logic/simulation; python -m pytest backend/tests/test_renderer.py -v
```
```
collected 2 items

backend\tests\test_renderer.py .s                                        [100%]

======================== 1 passed, 1 skipped in 0.82s =========================
```
Same skip behavior as the original report: `test_sim_renderer_available`
passes (returns `False` because `mujoco` isn't installed in this env);
`test_sim_renderer_returns_dict` correctly skips via
`pytest.skip("MuJoCo not available")`. The new shape/dtype assertions only
execute when MuJoCo is available — they're skipped along with the rest of
the render-path body — so the local skip result is unchanged.

**Full backend suite:**
```
cd D:/projects/robot-logic/simulation; python -m pytest backend/tests/ --tb=line
```
```
114 passed, 1 skipped, 7 warnings in 3.05s
```
Identical to the original baseline (114 passed, 1 skipped). The 7 warnings
are the same pre-existing Pydantic `class-based config` deprecations and
`aiosqlite` event-loop warnings reported in the original report — no new
warnings introduced.

### Files changed

- `simulation/backend/tests/test_renderer.py` — +4 assertions on rgb/depth
- `simulation/backend/rcs_env/renderer.py` — removed 1 unused import line

### Commit

- `2212f01` — `test(simulation): strengthen SimRenderer shape/dtype assertions`
