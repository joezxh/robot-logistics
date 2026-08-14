# Task 2 Report — DeviceManager + Runtime reset/load_scene

## Status: DONE_WITH_CONCERNS

## Commit

`ef9bcab` — feat(scenes): extend DeviceManager + Runtime with reset/load_scene

## Step 4 Verification Output

Command:
```powershell
python -c "import os, sys; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); from backend.services.runtime import runtime; r = runtime.load_scene('pallet'); print(r['scene'], len(r['devices']))"
```

Actual output:
```
pallet 3
```

Matches expected `pallet 3`.

## Existing Test Results

```
============================= test session starts =============================
collected 19 items
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

============================= 19 passed in 3.12s =============================
```

All 19 existing tests pass.

## Self-Check List

- [x] `DeviceManager()` 不传参数时仍保留原 5 个种子设备 (robot-01/loader-01/agv-01/agv-02/stacker-01) — 通过 `test_devices_lists_seed`
- [x] `DeviceManager(seed_devices=[])` 或 `DeviceManager(seed_devices=[...])` 按需定制 — 已实现
- [x] `DeviceManager.add(spec)` 接受 scene_presets.DeviceSpec 格式 — 已实现（用 `_register()` 共享解析逻辑）
- [x] `SiteManager(seed=False)` 不预置任何站点 — 已实现
- [x] `SiteManager(seed=True)` 或默认行为预置原 9 个默认站点 — 已实现（通过 `test_list_sites_seeded`）
- [x] `SiteManager.add(payload)` 已存在，无需新增 — 保持不变
- [x] `Runtime` 新增 `current_scene: str | None = None` 字段 — 已实现
- [x] `Runtime.reset()` 清空 devices/sites/tasks/logs/reverted_tasks/_detections/_nav_paths/_joint_cache，重置 started_at — 已实现
- [x] `Runtime.load_scene(name)` 调用顺序正确 — 已实现
- [x] `Runtime._scene_kpi(name)` 返回 dict 含全部 6 个字段 — 已实现
- [x] load_scene("pallet") 后 devices 列表含 forklift-01/forklift-02/agv-01 — 验证通过
- [x] load_scene("box") 后 devices 列表含 loader-01/stacker-01 — 验证通过（实际还有 agv-01/agv-02）
- [x] load_scene("bag") 后 devices 列表含 loader-01/stacker-01 — 验证通过（实际还有 agv-01）
- [x] load_scene("nonexistent") 抛 KeyError — 验证通过
- [x] 现有 Dashboard 功能不被破坏 — 19/19 测试通过，seed 默认行为保持

## Dashboard Compatibility

`DeviceManager.__init__` 默认行为（不传参数）继续保留原 5 个种子设备（通过 `DEFAULT_SEED_DEVICES` 常量）。`SiteManager.__init__` 默认 `seed=True` 保留原 9 个默认站点。`Runtime.__init__` 仍调用 `DeviceManager()` 与 `SiteManager()`（不带显式 seed 参数），因此现有 Dashboard 启动时仍看到 5 个种子设备和 9 个默认站点。19 个 API 测试全部通过证明兼容。

## Concerns

**Plan 与 brief 在 `reset()` 实现上有一处小的不一致**：brief 第 169 行写 `self.devices = DeviceManager()`，但如果严格按此实现，会带入 5 个默认种子设备（robot-01/loader-01/agv-01/agv-02/stacker-01），然后 `load_scene` 会因 `agv-01` 冲突而抛 `ValueError`（与 brief 第 17 行 "Plan 缺陷" 中描述的 site_id 冲突同源问题）。我采用了一致的修复方案：用 `DeviceManager(seed_devices=[])` 构造（与 `SiteManager(seed=False)` 模式对齐），使 `reset()` 后 devices 为空，可被 `load_scene` 干净地填充。这同时满足 brief 验收清单 "DeviceManager(seed_devices=[]) 按需定制" 一条，并使 Step 4 输出 `pallet 3` 与期望一致。

`SiteManager._seed()` 默认仍然预置 9 个站点，但 `load_scene` 调用 `reset()` 后用 `SiteManager(seed=False)` 重建，再 `add()` scene 自己的 sites（dock-01/warehouse-01...），不会冲突。
