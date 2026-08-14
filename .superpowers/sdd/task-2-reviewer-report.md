# Task 2 Reviewer Report — DeviceManager + Runtime reset/load_scene

## Verdict

- **Spec compliance**: ✅
- **Code quality**: ✅
- **Spec deviation**: Acceptable (see §C)

## A. Spec Compliance (Acceptance Checklist)

| # | Item | Status | Evidence |
|---|------|--------|----------|
| 1 | `DeviceManager()` 保留 5 个种子设备 | ✅ | Verified: `['robot-01', 'loader-01', 'agv-01', 'agv-02', 'stacker-01']` |
| 2 | `DeviceManager(seed_devices=[])` 自定义 | ✅ | `__init__` accepts `Iterable[dict] \| None`; default branch uses `DEFAULT_SEED_DEVICES` only when `seed_devices is None` |
| 3 | `DeviceManager.add(spec)` 接受 `DeviceSpec` 格式 (`x`/`z`/`device_id`/`device_type`/`name`/`speed`) | ✅ | `_register()` reads all 6 keys; `add()` adds `ValueError` duplicate guard |
| 4 | `SiteManager(seed=False)` 不预置站点 | ✅ | Verified empty after construction |
| 5 | `SiteManager(seed=True)` / 默认预置 9 站点 | ✅ | Verified `len(sites) == 9` after `SiteManager()` |
| 6 | `SiteManager.add(payload)` 保持不变 | ✅ | Unmodified from prior commit (file diff shows only `__init__` change) |
| 7 | `Runtime.current_scene: str \| None = None` | ✅ | `runtime.py:30` — added after `self.running = False` |
| 8 | `Runtime.reset()` 清空 devices/sites/tasks/logs/reverted_tasks/_detections/_nav_paths/_joint_cache + 重置 started_at + 保留 running | ✅ | Verified: after `reset()`, `devices == {}`, `sites == {}`, `tasks == {}`, `started_at is None`; `self.running` not touched |
| 9 | `Runtime.load_scene(name)` 调用顺序 | ✅ | Verified diff order: `get_scene → reset → add sites → add devices → create_task → set current_scene → log → return` |
| 10 | `Runtime._scene_kpi(name)` 返回 dict 含 6 字段 | ✅ | Verified keys: `{'scene', 'throughput_per_hour', 'success_rate', 'active_tasks', 'completed_tasks', 'failed_tasks'}` |
| 11 | load_scene("pallet") 含 forklift-01/forklift-02/agv-01 | ✅ | Verified: `['forklift-01', 'forklift-02', 'agv-01']` |
| 12 | load_scene("box") 含 loader-01/stacker-01 | ✅ | Verified: `['loader-01', 'agv-01', 'agv-02', 'stacker-01']` |
| 13 | load_scene("bag") 含 loader-01/stacker-01 | ✅ | Verified: `['loader-01', 'agv-01', 'stacker-01']` |
| 14 | load_scene("nonexistent") 抛 KeyError | ✅ | Verified raises `KeyError("unknown scene: 'nonexistent'; available: [...]")` |
| 15 | Dashboard 不被破坏 | ✅ | 19/19 existing tests pass; default `DeviceManager()` / `SiteManager()` behavior preserved |

## B. Code Quality

| Check | Status | Notes |
|-------|--------|-------|
| 无 FastAPI / Pydantic 依赖 | ✅ | Only added stdlib `Iterable` from `typing`; no FastAPI/Pydantic imports introduced. Pre-existing FAPI/Pydantic in `main.py` and `requirements.txt` is not from this commit. |
| Type hints 完整 | ✅ | `seed_devices: Iterable[dict] \| None`, `add(spec: dict) -> Device`, `reset() -> None`, `load_scene(name: str) -> dict[str, Any]`, `_scene_kpi(name: str) -> dict[str, Any]` all annotated |
| Docstring 在新方法上 | ✅ | `DeviceManager.add` (line 41), `Runtime.reset` (lines 67-73), `Runtime.load_scene` (line 86), `Runtime._scene_kpi` (line 269) all have docstrings |
| 无 print / TODO / 占位符 | ✅ | No `print`, no `TODO/FIXME/XXX` in the 3 changed files (existing `print` in `main.py:134,137` is pre-existing) |
| 与现有 backend 风格一致 | ✅ | Matches existing pattern: 4-space indent, `from __future__ import annotations`, snake_case, `Any` from `typing` |

## C. Spec Deviation 评估

**Implementer 偏离**：brief 第 169 行原方案 `self.devices = DeviceManager()` 被替换为 `self.devices = DeviceManager(seed_devices=[])`。

### 评估结论

1. **是否 plan / brief 的真实缺陷？** ✅ **是**
   - 严格按 brief 字面实现 `DeviceManager()` 会带入 5 个种子设备（robot-01/loader-01/agv-01/agv-02/stacker-01），其中 `agv-01` 与 `box`/`bag` scene 的 `agv-01` device_id 冲突，`add()` 抛 `ValueError`。
   - 这与 brief 第 17 行已识别的 "site_id 冲突" 缺陷是同源问题（仅 site vs device 不同）。
2. **修正是否合理且与整体设计意图一致？** ✅ **是**
   - 与同 commit 中 `SiteManager(seed=False)` 模式完全对称（两边都用 "构造函数接受一个关闭 seed 的开关"）。
   - 同时复用 brief 验收清单第 2 条 `DeviceManager(seed_devices=[]) 按需定制` 的同一参数。
   - 不破坏默认 Dashboard 行为（`__init__` 在不传参时仍预置 5 个设备）。
3. **修正后是否仍满足 acceptance checklist？** ✅ **是** — 见 §A 表第 8/9/11/12/13/14 行全部通过。

**判定**：偏差属于 "必要且与 brief 设计意图一致"，视为 spec 合规。

### 额外观察（非阻碍）

- `Runtime._scene_kpi` 在 `len(tasks) == 0` 时 `success_rate = 0.0`（因为 `total = len(tasks) or 1 = 1`，`completed = 0`，`0/1 * 100 = 0.0`），与 `Runtime.metrics()` 的 `100.0` 默认值不一致。这与 brief 第 222 行公式一致（`total = len(tasks) or 1`），属于按 brief 字面实现的预期行为，**不视为缺陷**。
- `_scene_kpi` 的 `throughput_per_hour` 占位算法（`42 + completed * 3`）与 `metrics()` 同源，与 brief 第 224 行注释 "沿用 metrics() 的占位算法" 一致。

## D. Dashboard 兼容性

- ✅ 19/19 existing tests pass (`test_devices_lists_seed`, `test_list_sites_seeded` 等都覆盖默认行为)
- ✅ 5 个种子设备 + 9 个默认站点在默认 `DeviceManager()` / `SiteManager()` 下保留（`test_devices_lists_seed` 通过即证）
- ✅ Commit 仅修改 3 个文件 (`device_manager.py`, `site_manager.py`, `runtime.py`)，`main.py` 与其他文件未触动

## Findings

- **Critical**: 0
- **Important**: 0
- **Minor**: 0

（无可报告的 issue）

## Verification Commands Executed

1. `git show ef9bcab --stat` / `git show ef9bcab` — 3 files, +111/-10 lines
2. `python -c "...load_scene('pallet')..."` → `pallet 3` ✅ (matches brief expected)
3. `pytest backend/tests/test_api.py -v` → **19 passed in 1.88s** ✅
4. Custom assertion harness: pallet/box/bag device ids, KeyError on nonexistent, KPI dict keys, reset clears state, default DeviceManager/SiteManager seeds, SiteManager(seed=False) empty

## Verdict

**APPROVED** — Task 2 满足 brief acceptance checklist，代码质量符合现有 backend 风格，Dashboard 兼容性 19/19 测试通过。Spec deviation（`DeviceManager(seed_devices=[])` vs brief 字面 `DeviceManager()`）是必要的修正，与 brief 整体设计意图一致。

---
**Reviewer**: Task Reviewer Subagent
**Commit reviewed**: `ef9bcab`
**Review date**: 2026-08-14