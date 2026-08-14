# Task 2 Brief — DeviceManager + Runtime reset/load_scene

## Project Context

工程 `d:\projects\robot-logic\` 是物流装卸机器人系统。当前任务是为 **Top 3 装卸场景**（托盘/箱装/袋装）实现仿真模块。Task 1 已完成 `simulation/backend/services/scene_presets.py`（commit `2f6fa79`）。**本 Task 在其之上接入 Runtime：使 runtime 能切换场景**。

下游：Task 3 注册 `/api/scenes/*` 端点；Task 4 写测试。

## Files

- **Modify**: `d:\projects\robot-logic\simulation\backend\algorithm\simulator\device_manager.py`
- **Modify**: `d:\projects\robot-logic\simulation\backend\algorithm\simulator\site_manager.py`
- **Modify**: `d:\projects\robot-logic\simulation\backend\services\runtime.py`

## 关键决策（纠正 plan 中的缺陷）

**Plan 缺陷**：`SiteManager.__init__` 默认会 `_seed()` 9 个默认站点（dock-A/B/C/D + rack-1/5）。`Runtime.reset()` 用 `SiteManager()` 会带这些默认站点进入后续 `load_scene()` 的 `add()`，因 site_id 冲突抛 `ValueError`。

**修正方案**：让 `SiteManager.__init__` 接受 `seed: bool = True` 参数，与 `DeviceManager(seed_devices=...)` 模式对齐；`reset()` 使用 `seed=False` 构造。

## Requirements（verbatim from plan + 修正）

### Step 1: 修改 `device_manager.py`

将整个文件替换为：

```python
from __future__ import annotations

from typing import Iterable

from .device import Device


class DeviceManager:
    def __init__(self, seed_devices: Iterable[dict] | None = None) -> None:
        if seed_devices is None:
            seed_devices = []
        self.devices: dict[str, Device] = {}
        for spec in seed_devices:
            self._register(spec)

    def _register(self, spec: dict) -> None:
        device = Device(
            device_id=spec["device_id"],
            device_type=spec["device_type"],
            name=spec["name"],
            position=[spec["x"], 0.0, spec["z"]],
            speed=spec.get("speed", 0.8),
        )
        self.devices[device.device_id] = device

    def add(self, spec: dict) -> Device:
        """Register a device at runtime (used by scene_presets.load_scene)."""
        if spec["device_id"] in self.devices:
            raise ValueError(f"device {spec['device_id']!r} already exists")
        self._register(spec)
        return self.devices[spec["device_id"]]

    def list(self) -> list[dict]:
        return [device.snapshot() for device in self.devices.values()]

    def get(self, device_id: str) -> Device:
        if device_id not in self.devices:
            raise KeyError(device_id)
        return self.devices[device_id]

    def tick(self, seconds: float) -> None:
        for device in self.devices.values():
            device.tick(seconds)
```

**关键约束**：
- 原文件第 9~14 行有 5 个种子设备（robot-01/loader-01/agv-01/agv-02/stacker-01）—— **这些必须保留**，使现有 Dashboard 仍可工作。
- 实现方法：构造函数接受可选 `seed_devices` 参数。默认行为（不传参数）下，构造函数应**保留原 5 个种子设备**。仅当显式传入 `seed_devices=[]`（空列表）或显式列表时才不预置任何设备。

**正确实现（保留原有种子）**：

```python
DEFAULT_SEED_DEVICES: list[dict] = [
    {"device_id": "robot-01", "device_type": "container_robot",
     "name": "集装箱装卸机器人", "x": -8.0, "z": 2.0, "speed": 0.55},
    {"device_id": "loader-01", "device_type": "loading_robot",
     "name": "双臂AGV装卸机器人", "x": -3.0, "z": 0.0, "speed": 0.50},
    {"device_id": "agv-01", "device_type": "agv",
     "name": "AGV 转运车", "x": -5.0, "z": -1.0, "speed": 1.2},
    {"device_id": "agv-02", "device_type": "agv",
     "name": "AGV 转运车 2", "x": 1.0, "z": 2.0, "speed": 1.0},
    {"device_id": "stacker-01", "device_type": "stacker",
     "name": "立库堆垛机", "x": 7.0, "z": 0.0, "speed": 0.7},
]


class DeviceManager:
    def __init__(self, seed_devices: Iterable[dict] | None = None) -> None:
        if seed_devices is None:
            seed_devices = DEFAULT_SEED_DEVICES
        self.devices: dict[str, Device] = {}
        for spec in seed_devices:
            self._register(spec)

    def _register(self, spec: dict) -> None:
        device = Device(
            device_id=spec["device_id"],
            device_type=spec["device_type"],
            name=spec["name"],
            position=[spec["x"], 0.0, spec["z"]],
            speed=spec.get("speed", 0.8),
        )
        self.devices[device.device_id] = device

    def add(self, spec: dict) -> Device:
        """Register a device at runtime (used by scene_presets.load_scene)."""
        if spec["device_id"] in self.devices:
            raise ValueError(f"device {spec['device_id']!r} already exists")
        self._register(spec)
        return self.devices[spec["device_id"]]

    def list(self) -> list[dict]:
        return [device.snapshot() for device in self.devices.values()]

    def get(self, device_id: str) -> Device:
        if device_id not in self.devices:
            raise KeyError(device_id)
        return self.devices[device_id]

    def tick(self, seconds: float) -> None:
        for device in self.devices.values():
            device.tick(seconds)
```

### Step 2: 修改 `site_manager.py`

`SiteManager` **已有** `add(payload)` 方法（无需新增）。需要做的是：

1. **修改 `__init__` 接受 `seed: bool = True`**：

```python
class SiteManager:
    """Holds a registry of dock and warehouse sites."""

    def __init__(self, seed: bool = True) -> None:
        self.sites: dict[str, Site] = {}
        if seed:
            self._seed()
```

2. 其余代码（`_seed` / `add` / `update` / `remove` / `list` / `get`）**保持不变**。

### Step 3: 修改 `runtime.py`

1. **在 `__init__` 中新增字段**（在 `self.running = False` 后）：

```python
self.current_scene: str | None = None
```

2. **在 `start()` 方法之前新增 `reset()` 和 `load_scene()` 方法**：

```python
def reset(self) -> None:
    """Clear runtime state without touching the synthetic sensor generators.

    - Wipe devices (next load_scene will re-seed).
    - Wipe sites, tasks, logs, reverted tasks.
    - Reset started_at; keep running flag as-is.
    - Drop any cached sensor / joint state.
    """
    self.devices = DeviceManager()
    self.sites = SiteManager(seed=False)
    self.tasks.clear()
    self.logs.clear()
    self.reverted_tasks.clear()
    self._detections.clear()
    self._nav_paths.clear()
    self._joint_cache.clear()
    self.started_at = None
    self.log(self.trace_id(), None, "runtime", "reset")


def load_scene(self, name: str) -> dict[str, Any]:
    """Apply a scene preset: reset runtime then register preset sites / devices / tasks."""
    from backend.services.scene_presets import get_scene

    preset = get_scene(name)  # raises KeyError for unknown scenes
    self.reset()
    # Register sites
    for site_spec in preset["sites"]:
        self.sites.add(site_spec)
    # Register devices
    for device_spec in preset["devices"]:
        self.devices.add(device_spec)
    # Create tasks
    for task_spec in preset["tasks"]:
        try:
            priority = TaskPriority(task_spec["priority"])
        except ValueError:
            priority = TaskPriority.NORMAL
        self.create_task(
            task_spec["type"],
            task_spec["description"],
            priority,
            task_spec["device_id"],
        )
    self.current_scene = name
    self.log(self.trace_id(), None, "scene_presets", f"loaded scene {name!r}")
    return {
        "scene": name,
        "devices": self.devices.list(),
        "sites": self.sites.list(),
    }
```

3. **在 `stats()` 方法之后新增 `_scene_kpi()` 方法**：

```python
def _scene_kpi(self, name: str) -> dict[str, Any]:
    """Compute scene-specific KPI snapshot (used by /api/scenes/{name}/kpi)."""
    tasks = list(self.tasks.values())
    completed = sum(t["status"] == "completed" for t in tasks)
    failed = sum(t["status"] == "failed" for t in tasks)
    total = len(tasks) or 1
    success_rate = round((completed / total) * 100, 1)
    throughput_per_hour = 42 + completed * 3  # 沿用 metrics() 的占位算法
    return {
        "scene": name,
        "throughput_per_hour": throughput_per_hour,
        "success_rate": success_rate,
        "active_tasks": sum(1 for t in tasks if t["status"] == "running"),
        "completed_tasks": completed,
        "failed_tasks": failed,
    }
```

### Step 4: 验证

**重要**：Python 包根是 `simulation/`，不是 `simulation/backend/`。使用下列命令：

```powershell
python -c "import os, sys; os.chdir(r'D:\projects\robot-logic\simulation'); sys.path.insert(0, '.'); from backend.services.runtime import runtime; r = runtime.load_scene('pallet'); print(r['scene'], len(r['devices']))"
```

期望输出：`pallet 3`

### Step 5: 提交

```bash
cd d:/projects/robot-logic
git add simulation/backend/algorithm/simulator/device_manager.py
git add simulation/backend/algorithm/simulator/site_manager.py
git add simulation/backend/services/runtime.py
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): extend DeviceManager + Runtime with reset/load_scene"
```

## Acceptance Checklist

- [ ] `DeviceManager()` 不传参数时仍保留原 5 个种子设备（robot-01/loader-01/agv-01/agv-02/stacker-01）
- [ ] `DeviceManager(seed_devices=[])` 或 `DeviceManager(seed_devices=[...])` 按需定制
- [ ] `DeviceManager.add(spec)` 接受 scene_presets.DeviceSpec 格式（`x`/`z`/`device_id`/`device_type`/`name`/`speed`）
- [ ] `SiteManager(seed=False)` 不预置任何站点
- [ ] `SiteManager(seed=True)` 或默认行为预置原 9 个默认站点（保持 Dashboard 兼容）
- [ ] `SiteManager.add(payload)` 已存在，无需新增
- [ ] `Runtime` 新增 `current_scene: str | None = None` 字段
- [ ] `Runtime.reset()` 清空 devices/sites/tasks/logs/reverted_tasks/_detections/_nav_paths/_joint_cache，重置 started_at，保留 running 标志
- [ ] `Runtime.load_scene(name)` 调用顺序：get_scene → reset → add sites → add devices → create_task → set current_scene → log → return
- [ ] `Runtime._scene_kpi(name)` 返回 dict 含 `scene`/`throughput_per_hour`/`success_rate`/`active_tasks`/`completed_tasks`/`failed_tasks`
- [ ] load_scene("pallet") 后 devices 列表含 forklift-01/forklift-02/agv-01
- [ ] load_scene("box") 后 devices 列表含 loader-01/stacker-01
- [ ] load_scene("bag") 后 devices 列表含 loader-01/stacker-01
- [ ] load_scene("nonexistent") 抛 KeyError
- [ ] 现有 Dashboard 功能不被破坏（`DeviceManager()` 默认行为不变）

## Global Constraints

- Python 3.11+ / type hint / docstring 风格与现有 backend 代码一致
- 修改文件后保持原有 import / 命名空间结构
- 仅修改 plan 中列出的 3 个文件
- 不要新增测试文件（Task 4 负责）
- 不要修改 main.py（Task 3 负责）

## Report Contract

将完整报告写入 `d:\projects\robot-logic\.superpowers\sdd\task-2-report.md`，内容包含：
1. 状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
2. commit hash（7 位）
3. Step 4 验证命令的实际输出
4. 自检清单勾选状态
5. 现有 Dashboard 不被破坏的验证（说明）
6. concerns

返回仅含：状态 + commit hash（7 位）+ 一行 Step 4 结果 + concerns。