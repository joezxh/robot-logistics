# Task 3 Reviewer Report

## Status: APPROVED

## Spec Compliance: ✅

- [x] `DeviceCreateRequest.device_type` regex includes `pallet_forklift` — verified at `simulation/backend/main.py:95-98` (`pattern="^(container_robot|loading_robot|agv|stacker|pallet_forklift)$"`).
- [x] 4 endpoints registered in the correct order after `delete_site`: `GET /api/scenes` (L252), `POST /api/scenes/load/{name}` (L262), `GET /api/scenes/current` (L272), `GET /api/scenes/{name}/kpi` (L281).
- [x] `GET /api/scenes` returns `{"available": [...], "current": null | "..."}` — report shows `{"available":["pallet","box","bag"],"current":null}`.
- [x] `POST /api/scenes/load/pallet` returns `{"scene": "pallet", "devices": [...], "sites": [...]}` — verified, payload contains `"scene":"pallet"` plus devices/sites.
- [x] `POST /api/scenes/load/nope` returns 404 — verified `unknown scene status: 404 {"detail":"\"unknown scene: 'nope'; available: ['pallet', 'box', 'bag']\""}`.
- [x] `GET /api/scenes/current` returns 404 when no scene active; returns `ScenePreset` after load — verified (`current(empty): 404 ... current(loaded) name: pallet`).
- [x] `GET /api/scenes/pallet/kpi` returns KPI dict containing `throughput_per_hour` / `success_rate` / `scene` — verified `{"scene":"pallet","throughput_per_hour":42,"success_rate":0.0,"active_tasks":0,...}`.
- [x] `GET /api/scenes/nope/kpi` returns 404 — verified.
- [x] `POST /api/devices/register` accepts `device_type="pallet_forklift"` → 200 — verified `status: 200 body: {"device_id":"test-fk","device_type":"pallet_forklift",...}`.
- [x] All 19 existing tests pass — independently re-ran `python -m pytest backend/tests/test_api.py -v` → `19 passed in 2.48s`.

Commit `2d23310` touches only `simulation/backend/main.py` (+44 / −1), confirmed by `git show --stat`.

## Code Quality: ✅

- Implementation matches the brief literal code block 1:1 (only difference: the brief used `dependencies=[]` for the GET endpoints which is the idiomatic FastAPI default — harmless).
- Error handling mirrors `Runtime.load_scene` semantics via `try/except KeyError → HTTPException(404)`, consistent with existing `delete_site` / `rollback` patterns.
- `dependencies=[Depends(rate_limit_dep)]` is applied to the only mutating endpoint (`POST /api/scenes/load/{name}`), matching the existing `/api/devices/register` convention.
- Lazy `from backend.services.scene_presets import ...` inside each handler avoids module-load cycles, consistent with how `register_device` already imports `Device` locally.
- No new Pydantic models introduced (per "Global Constraints"); all responses are plain dicts.
- Path ordering note: `/api/scenes/{name}/kpi` is correctly placed *after* `/api/scenes/current` so FastAPI's path matcher resolves the literal first — matches the literal order in the brief.
- Style is consistent with surrounding code (4-space indent, type hints, docstrings).

## Findings

- Critical: 0
- Important: 0
- Minor: 1

### Minor-1: `str(exc)` quote doubling in 404 response body

When `Runtime.load_scene` raises `KeyError("unknown scene: 'nope'; available: ['pallet', 'box', 'bag']")`, FastAPI serializes the exception object via `str(exc)` which keeps the inner quotes, producing a JSON body like `{"detail":"\"unknown scene: 'nope'; available: ['pallet', 'box', 'bag']\""}` — the outer double quotes are escaped because the detail field is itself a string. This is cosmetically odd but functionally correct (clients can `JSON.parse` it). It would be marginally cleaner to strip the outer quotes (`detail=str(exc).strip("'\"")`) or pre-format the message, but this is a cosmetic concern in an error-path response and does not affect any acceptance criterion. No action required.

## Concerns Assessment

- **Concern 1 (RCS package)**: The `RCS_EMBEDDED=0` workaround is acceptable — the runtime config block at `main.py:27-40` documents this switch and the test suite already sets it via `pytest.ini`. The implemented code paths are RCS-agnostic and behave identically in both modes. Not a blocker.
- **Concern 2 (load_scene wipes prior runtime state)**: Confirmed by design (`Runtime.reset` + `Runtime.load_scene` from Task 2). The endpoint's docstring "`Reset runtime and apply the named scene preset.`" accurately describes this behavior, so the contract is not hidden. Not a blocker; documented in report.
- **Concern 3 (success_rate stub)**: `_scene_kpi` returns `success_rate=0.0` immediately after load because tasks are still pending. This is a pre-existing stub from Task 2's `Runtime` implementation, not regressed by this task. The KPI dictionary still carries `throughput_per_hour` / `success_rate` / `scene` keys as required by the acceptance checklist. Not a blocker.

## Verdict

**APPROVED** — All 10 acceptance criteria are met with verified outputs; the diff is the minimal one-file change required by the brief (`+44 / −1`); the existing 19-test suite still passes (independently re-run); code quality is consistent with surrounding style; only one cosmetic minor finding on the 404 error message format, which is non-blocking.
