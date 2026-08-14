# Task 3 Report — /api/scenes/* endpoints

## Status
**DONE**

## Commit
`2d23310` (7 chars) — `simulation/backend/main.py` only (+44 / −1).

## Changes (one file: `simulation/backend/main.py`)

### Step 1: `DeviceCreateRequest.device_type` regex extended

```95:98:simulation/backend/main.py
    device_type: str = Field(
        ...,
        pattern="^(container_robot|loading_robot|agv|stacker|pallet_forklift)$",
    )
```

### Step 2: 4 scene endpoints inserted after `delete_site`

```252:289:simulation/backend/main.py
@app.get("/api/scenes", dependencies=[])
async def list_scenes():
    """List available scene presets plus currently active scene name."""
    from backend.services.scene_presets import list_scene_names
    return {
        "available": list_scene_names(),
        "current": runtime.current_scene,
    }


@app.post("/api/scenes/load/{name}", dependencies=[Depends(rate_limit_dep)])
async def load_scene(name: str):
    """Reset runtime and apply the named scene preset."""
    try:
        result = runtime.load_scene(name)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return result


@app.get("/api/scenes/current", dependencies=[])
async def current_scene():
    """Return the active scene preset (or 404 if none loaded)."""
    from backend.services.scene_presets import get_scene
    if runtime.current_scene is None:
        raise HTTPException(status_code=404, detail="no scene is currently active")
    return get_scene(runtime.current_scene)


@app.get("/api/scenes/{name}/kpi", dependencies=[])
async def scene_kpi(name: str):
    """Compute KPI snapshot for the named scene."""
    from backend.services.scene_presets import get_scene
    try:
        get_scene(name)  # validate name
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return runtime._scene_kpi(name)
```

## Verification (Step 3)

All commands were launched from `D:\projects\robot-logic\simulation` with `RCS_EMBEDDED=0` (the local environment has no `rcs` package installed, so the embedded mode import fails; setting `RCS_EMBEDDED=0` is the supported switch documented in the runtime config block at lines 27–40 of `main.py`). Port `8765` was used per the brief. Every uvicorn subprocess was `.terminate()`'d at the end.

### Command 1 — List / Load / KPI happy path

```
LIST: {"available":["pallet","box","bag"],"current":null}
LOAD: {"scene":"pallet","devices":[{"device_id":"forklift-01","device_type":"pallet_forklift","name":"托盘叉车 1","position":[-3.0,0.0,2.0],"route":[],"speed":0.6,"status":"idle","progress":0.0,"battery":100.0,
KPI: {"scene":"pallet","throughput_per_hour":42,"success_rate":0.0,"active_tasks":0,"completed_tasks":0,"failed_tasks":0}
```

### Command 2 — Register `pallet_forklift` device

```
REG status: 200 body: {"device_id":"test-fk","device_type":"pallet_forklift","name":"t","position":[0.0,0.0,0.0],"route":[],"speed":0.8,"status":"idle","progress":0.0,"batt
```

### Command 3 — Unknown scene name → 404

```
unknown scene status: 404 {"detail":"\"unknown scene: 'nope'; available: ['pallet', 'box', 'bag']\""}
```

### Bonus — `/api/scenes/current` and `/api/scenes/{name}/kpi` error paths

```
current(empty): 404 {"detail":"no scene is currently active"}
current(loaded) name: pallet
kpi(nope): 404 {"detail":"\"unknown scene: 'nope'; available: ['pallet', 'box', 'bag']\""}
```

## Existing test suite

`pytest backend/tests/test_api.py -v` → **19 passed in 1.85s**

```
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
backend\tests\test_api.py::test_create_duplicate_site_conflict PASSED   [ 78%]
backend\tests\test_api.py::test_patch_site PASSED                        [ 84%]
backend\tests\test_api.py::test_register_and_delete_custom_device PASSED [ 89%]
backend\tests\test_api.py::test_register_duplicate_conflict PASSED       [ 94%]
backend\tests\test_api.py::test_patch_device PASSED                      [100%]
============================= 19 passed in 1.85s ==============================
```

## Acceptance Checklist

- [x] `DeviceCreateRequest.device_type` regex includes `pallet_forklift` (and `loading_robot`)
- [x] 4 endpoints registered: `GET /api/scenes`, `POST /api/scenes/load/{name}`, `GET /api/scenes/current`, `GET /api/scenes/{name}/kpi`
- [x] `GET /api/scenes` returns `{"available": [...], "current": null | "..."}`
- [x] `POST /api/scenes/load/pallet` returns `{"scene": "pallet", "devices": [...], "sites": [...]}`
- [x] `POST /api/scenes/load/nope` returns 404
- [x] `GET /api/scenes/current` returns 404 when no scene active; returns `ScenePreset` after load
- [x] `GET /api/scenes/pallet/kpi` returns KPI dict containing `throughput_per_hour` / `success_rate` / `scene`
- [x] `GET /api/scenes/nope/kpi` returns 404
- [x] `POST /api/devices/register` accepts `device_type="pallet_forklift"` → 200
- [x] Existing 19 tests still pass

## Concerns

1. **Local RCS package absent** — `backend/main.py` raises `ImportError` when `RCS_EMBEDDED=1` because no `rcs` package is importable in this workspace. The brief did not call out this fact; tests pass because `pytest.ini` / conftest sets `RCS_EMBEDDED=0` for the test process. The uvicorn validation therefore required setting `RCS_EMBEDDED=0` manually via `os.environ`. The implemented code itself is independent of this — no other behavior was changed.
2. **Loading a scene wipes prior runtime state** — this is intentional (matches `Runtime.reset` + `Runtime.load_scene` semantics from Task 2). `/api/scenes/load/{name}` issues an implicit reset; calling clients should be aware that any in-flight task / device ids are discarded.
3. **`_scene_kpi` returns 0% success rate immediately after load** — expected because tasks are still `pending`. Throughput uses the same 42+completed*3 placeholder as `Runtime.metrics`. This is a known stub and not regressed by this task.
