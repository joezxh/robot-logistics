# Task 4 Brief — pytest for presets/runtime/api

## Project Context

工程 `d:\projects\robot-logic\` Top 3 仿真模块。Task 1-3 完成数据层 + Runtime + API。HEAD = `2d23310`。本 Task 为新功能补 pytest 覆盖。

## Files

- **Create**: `d:\projects\robot-logic\simulation\backend\tests\test_scene_presets.py`
- **Create**: `d:\projects\robot-logic\simulation\backend\tests\test_runtime_load_scene.py`
- **Create**: `d:\projects\robot-logic\simulation\backend\tests\test_scenes_api.py`

## Requirements（verbatim from plan）

### Step 1: 创建 `test_scene_presets.py`

完整文件内容（verbatim）：

```python
"""Tests for scene preset data integrity."""
from backend.services.scene_presets import (
    SCENE_PRESETS, list_scene_names, get_scene,
)


def test_three_scenes_present():
    assert set(SCENE_PRESETS.keys()) == {"pallet", "box", "bag"}
    assert list_scene_names() == ["pallet", "box", "bag"]


def test_each_preset_has_required_fields():
    required = {"name", "label", "description", "sites", "devices", "tasks", "kpi_definitions"}
    for name, preset in SCENE_PRESETS.items():
        assert required.issubset(preset.keys()), f"{name} missing fields"
        assert preset["name"] == name


def test_each_preset_has_minimum_one_site_device_task():
    for name, preset in SCENE_PRESETS.items():
        assert len(preset["sites"]) >= 1, f"{name} no sites"
        assert len(preset["devices"]) >= 2, f"{name} not enough devices"
        assert len(preset["tasks"]) >= 1, f"{name} no tasks"


def test_get_scene_raises_for_unknown():
    import pytest
    with pytest.raises(KeyError, match="unknown scene"):
        get_scene("does-not-exist")


def test_pallet_has_pallet_forklift_devices():
    devices = SCENE_PRESETS["pallet"]["devices"]
    types = {d["device_type"] for d in devices}
    assert "pallet_forklift" in types
```

### Step 2: 创建 `test_runtime_load_scene.py`

```python
"""Tests for Runtime.reset() and Runtime.load_scene()."""
from backend.algorithm.scheduler.task import TaskPriority
from backend.services.runtime import Runtime


def test_reset_clears_devices_tasks_logs():
    runtime = Runtime()
    initial_device_count = len(runtime.devices.devices)
    assert initial_device_count > 0  # seeded devices
    runtime.create_task("dock_loading", "x", TaskPriority.NORMAL, "robot-01")
    assert len(runtime.tasks) > 0
    runtime.reset()
    assert len(runtime.devices.devices) == 0
    assert len(runtime.tasks) == 0
    assert len(runtime.logs) > 0  # reset logs its own entry


def test_load_scene_pallet_registers_expected_devices():
    runtime = Runtime()
    result = runtime.load_scene("pallet")
    assert result["scene"] == "pallet"
    device_ids = {d["device_id"] for d in result["devices"]}
    assert {"forklift-01", "forklift-02", "agv-01"}.issubset(device_ids)
    assert runtime.current_scene == "pallet"


def test_load_scene_box_loads_correctly():
    runtime = Runtime()
    result = runtime.load_scene("box")
    assert result["scene"] == "box"
    device_ids = {d["device_id"] for d in result["devices"]}
    assert "loader-01" in device_ids
    assert "stacker-01" in device_ids


def test_load_scene_bag_loads_correctly():
    runtime = Runtime()
    result = runtime.load_scene("bag")
    assert result["scene"] == "bag"
    device_ids = {d["device_id"] for d in result["devices"]}
    assert "loader-01" in device_ids


def test_load_scene_unknown_raises_keyerror():
    runtime = Runtime()
    try:
        runtime.load_scene("does-not-exist")
    except KeyError:
        return
    assert False, "expected KeyError"


def test_load_scene_clears_previous_state():
    runtime = Runtime()
    runtime.load_scene("pallet")
    count_after_pallet = len(runtime.devices.devices)
    runtime.load_scene("box")
    assert len(runtime.devices.devices) != count_after_pallet  # different device set
    device_ids = {d["device_id"] for d in runtime.devices.list()}
    assert "forklift-01" not in device_ids  # pallet-only device gone


def test_scene_kpi_returns_dict():
    runtime = Runtime()
    runtime.load_scene("pallet")
    kpi = runtime._scene_kpi("pallet")
    assert kpi["scene"] == "pallet"
    assert "throughput_per_hour" in kpi
    assert "success_rate" in kpi
```

### Step 3: 创建 `test_scenes_api.py`

```python
"""Tests for /api/scenes endpoints via FastAPI TestClient."""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.runtime import runtime


@pytest.fixture(autouse=True)
def _reset_runtime_after_test():
    yield
    runtime.reset()
    runtime.current_scene = None


def test_list_scenes_returns_three():
    client = TestClient(app)
    res = client.get("/api/scenes")
    assert res.status_code == 200
    body = res.json()
    assert set(body["available"]) == {"pallet", "box", "bag"}


def test_load_scene_pallet_succeeds():
    client = TestClient(app)
    res = client.post("/api/scenes/load/pallet")
    assert res.status_code == 200
    assert res.json()["scene"] == "pallet"


def test_load_scene_unknown_returns_404():
    client = TestClient(app)
    res = client.post("/api/scenes/load/nope")
    assert res.status_code == 404


def test_current_scene_404_when_none_loaded():
    client = TestClient(app)
    res = client.get("/api/scenes/current")
    assert res.status_code == 404


def test_current_scene_returns_preset_when_loaded():
    client = TestClient(app)
    client.post("/api/scenes/load/box")
    res = client.get("/api/scenes/current")
    assert res.status_code == 200
    assert res.json()["name"] == "box"


def test_scene_kpi_returns_snapshot():
    client = TestClient(app)
    client.post("/api/scenes/load/bag")
    res = client.get("/api/scenes/bag/kpi")
    assert res.status_code == 200
    body = res.json()
    assert body["scene"] == "bag"
    assert "throughput_per_hour" in body


def test_device_create_accepts_pallet_forklift_type():
    client = TestClient(app)
    res = client.post(
        "/api/devices/register",
        json={
            "device_id": "test-fork-01",
            "device_type": "pallet_forklift",
            "name": "test",
            "x": 0.0, "z": 0.0,
        },
    )
    assert res.status_code == 200
```

**注意**：plan 中 typo `test_list_senes_returns_three` 已修正为 `test_list_scenes_returns_three`（这是 plan typo，不是 spec 改动）。

### Step 4: 运行新测试（plan defect 修正）

pytest 配置（`backend/pytest.ini`）应已设置 `PYTHONPATH` 或通过 conftest 处理 import。如不通过，使用 `cd simulation` 而不是 `cd simulation/backend`：

```bash
cd "d:/projects/robot-logic/simulation"
pytest backend/tests/test_scene_presets.py backend/tests/test_runtime_load_scene.py backend/tests/test_scenes_api.py -v
```

期望：3 个文件全部通过。

### Step 5: 运行现有测试确认未破坏

```bash
cd "d:/projects/robot-logic/simulation"
pytest backend/tests/test_api.py -v
```

期望：19 个测试继续通过。

### Step 6: 提交

```bash
cd d:/projects/robot-logic
git add simulation/backend/tests/test_scene_presets.py
git add simulation/backend/tests/test_runtime_load_scene.py
git add simulation/backend/tests/test_scenes_api.py
git -c user.name="cursor" -c user.email="cursor@local" commit -m "test(scenes): add preset/runtime/api tests"
```

## Acceptance Checklist

- [ ] `test_scene_presets.py` 创建并 5 个测试全部通过
- [ ] `test_runtime_load_scene.py` 创建并 7 个测试全部通过
- [ ] `test_scenes_api.py` 创建并 7 个测试全部通过（含 fixture）
- [ ] 现有 `test_api.py` 19 个测试仍通过
- [ ] 仅 commit 这 3 个测试文件（不要修改任何其他文件）

## Global Constraints

- Python 测试风格与现有 `backend/tests/test_api.py` 一致
- 使用 `pytest` + `pytest-asyncio` + `TestClient`（现有项目风格）
- TestClient 使用全局 `app`，不创建新实例
- 不要 import `os` 设置 PYTHONPATH（如不通过，先读 `backend/pytest.ini` 看现有配置）

## Report Contract

写入 `d:\projects\robot-logic\.superpowers\sdd\task-4-report.md`，包含：
1. 状态
2. commit hash（7 位）
3. Step 4 / Step 5 测试输出（pytest summary 行 + 各测试 PASSED/FAILED 列表）
4. Acceptance checklist 勾选状态
5. concerns

返回仅含：状态 + commit + 一行测试摘要 + concerns。