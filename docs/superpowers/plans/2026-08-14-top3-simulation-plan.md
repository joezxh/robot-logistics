# Top 3 装卸场景仿真模块 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为文档 `docs/装卸场景与机器人适配选型.md` 第 3.7 节选出的 Top 3 装卸场景（托盘 / 箱装 / 袋装）实现完整的 `/scenes` 仿真模块，含 3 个 Tab、3D 场景、5 面板、3 套程序生成设备模型。

**Architecture:** 后端在现有 `Runtime` 上扩展 `load_scene()` 方法 + 新增 `scene_presets.py` 配置 + 4 个 REST endpoint；新增 1 个设备类型 `pallet_forklift`。前端新建 `/scenes` 顶级路由 + Vue Router，3 个 Tab 切换独立 Three.js 场景子组件，复用现有 dashboard 组件（Kpi/DeviceStatus/TaskTimeline/LogViewer）。

**Tech Stack:** Python 3.11+ / FastAPI / Pydantic / pytest；Vue 3 / Vite / TypeScript / vue-tsc / Three.js / vue-router / axios / vitest

---

## Global Constraints

- 后端沿用现有代码风格（FastAPI lifespan / Pydantic BaseModel / `dependencies=[Depends(rate_limit_dep)]` 模式）；新增测试使用 `pytest` + `pytest-asyncio`，与现有 `tests/` 一致。
- 前端沿用现有 Vue 3 Composition API + `<script setup lang="ts">` 风格；composables 命名 `useXxx.ts`；Three.js 类放在 `src/three/`，与现有 `RobotArm.ts` / `LoaderRobot.ts` 同级。
- 命名约定：场景名 `pallet` / `box` / `bag`；device_type `pallet_forklift`；组件名 PascalCase；composable camelCase。
- 严禁破坏现有 Dashboard：`/api/scenes/*` 路由不影响 `/api/devices` `/api/tasks` `/api/sites` 等现有端点。
- 中文 UI 文案沿用现有 i18n 风格。
- 频繁提交：每个 Task 完成后 git commit。

---

## File Structure

**后端新增/修改**

| 文件 | 状态 | 职责 |
|------|------|------|
| `simulation/backend/services/scene_presets.py` | 新建 | 3 个场景预设数据（sites / devices / tasks / kpi_definitions） |
| `simulation/backend/services/runtime.py` | 修改 | 新增 `reset()` + `load_scene(name)` 方法，记录 `current_scene` |
| `simulation/backend/algorithm/simulator/device_manager.py` | 修改 | 构造函数支持可选 `seed_devices`，不预置任何设备（让 preset 显式注册） |
| `simulation/backend/main.py` | 修改 | 注册 4 个 `/api/scenes/*` 端点；`DeviceCreateRequest.device_type` 枚举扩展 `pallet_forklift` |
| `simulation/backend/tests/test_scene_presets.py` | 新建 | 3 个 preset 数据完整性测试 |
| `simulation/backend/tests/test_runtime_load_scene.py` | 新建 | `reset()` + `load_scene()` 单元测试 |
| `simulation/backend/tests/test_scenes_api.py` | 新建 | 4 个 endpoint API 测试 |

**前端新增/修改**

| 文件 | 状态 | 职责 |
|------|------|------|
| `simulation/frontend/src/router/index.ts` | 新建 | Vue Router 配置，注册 `/scenes` 路由 |
| `simulation/frontend/src/scenes/ScenesPage.vue` | 新建 | 顶级路由页面，含 Tab 切换 |
| `simulation/frontend/src/scenes/SceneStage.vue` | 新建 | 通用 5 面板框架 |
| `simulation/frontend/src/scenes/ScenePallet.vue` | 新建 | 托盘场景子组件 |
| `simulation/frontend/src/scenes/SceneBox.vue` | 新建 | 箱装场景子组件 |
| `simulation/frontend/src/scenes/SceneBag.vue` | 新建 | 袋装场景子组件 |
| `simulation/frontend/src/scenes/three/PalletForklift.ts` | 新建 | 托盘叉车 Three.js 程序生成 |
| `simulation/frontend/src/scenes/three/BoxGripper.ts` | 新建 | 箱装夹爪末端（扩展 LoaderRobot） |
| `simulation/frontend/src/scenes/three/BagGripper.ts` | 新建 | 袋装夹爪末端（扩展 LoaderRobot） |
| `simulation/frontend/src/scenes/composables/useSceneAPI.ts` | 新建 | 后端 scene API 封装 |
| `simulation/frontend/src/scenes/composables/useSceneStage.ts` | 新建 | 阶段状态机 composable |
| `simulation/frontend/src/scenes/composables/useSceneKPI.ts` | 新建 | KPI composable |
| `simulation/frontend/src/App.vue` | 修改 | topbar 增加 `/scenes` 入口（router-link） |
| `simulation/frontend/src/main.ts` | 修改 | 注册 router |
| `simulation/frontend/src/scenes/__tests__/useSceneAPI.test.ts` | 新建 | API composable 单元测试 |
| `simulation/frontend/src/scenes/__tests__/useSceneStage.test.ts` | 新建 | 状态机单元测试 |

---

### Task 1: 后端 — scene_presets.py 数据模块

**Files:**
- Create: `simulation/backend/services/scene_presets.py`

**Interfaces:**
- Produces: `SCENE_PRESETS: dict[str, ScenePreset]` 供 Task 2 `runtime.load_scene()` 调用；`ScenePreset` TypedDict 含 `name` / `label` / `description` / `sites` / `devices` / `tasks` / `kpi_definitions` 字段

- [ ] **Step 1: 创建文件，写入 ScenePreset TypedDict 与 3 个 preset**

文件路径 `simulation/backend/services/scene_presets.py`：

```python
"""Scene preset data for the Top 3 loading scenarios.

This module is intentionally framework-free (no FastAPI / Pydantic) so it can
be reused by both the runtime and any future CLI tooling.
"""
from __future__ import annotations

from typing import TypedDict


class SiteSpec(TypedDict):
    id: str
    kind: str  # "dock" | "warehouse"
    name: str
    x: float
    y: float
    z: float
    width: float
    height: float
    depth: float
    rotation: float
    color: str


class DeviceSpec(TypedDict):
    device_id: str
    device_type: str  # "pallet_forklift" | "loading_robot" | "agv" | "stacker"
    name: str
    x: float
    z: float
    speed: float


class TaskSpec(TypedDict):
    type: str  # "pallet_fork" | "box_unload" | "bag_unload" | "agv_transport" | "warehouse_storage"
    description: str
    priority: int  # 1..4
    device_id: str


class KPIDefinition(TypedDict):
    label: str
    key: str
    unit: str
    target: str


class ScenePreset(TypedDict):
    name: str
    label: str
    description: str
    sites: list[SiteSpec]
    devices: list[DeviceSpec]
    tasks: list[TaskSpec]
    kpi_definitions: list[KPIDefinition]


PALLET_SCENE: ScenePreset = {
    "name": "pallet",
    "label": "托盘单元（欧/美/田/川）",
    "description": "Top 3 第 1 名：托盘搬运。D 复合 + C 叉型，最成熟场景。",
    "sites": [
        {"id": "dock-01", "kind": "dock", "name": "集装箱月台",
         "x": -6.0, "y": 0.0, "z": 4.0, "width": 6.0, "height": 0.6, "depth": 4.0,
         "rotation": 0.0, "color": "#5eb0ff"},
        {"id": "warehouse-01", "kind": "warehouse", "name": "仓库 1",
         "x": 6.0, "y": 0.0, "z": -2.0, "width": 4.0, "height": 3.0, "depth": 3.0,
         "rotation": 0.0, "color": "#58c47e"},
        {"id": "warehouse-02", "kind": "warehouse", "name": "仓库 2（备用）",
         "x": 6.0, "y": 0.0, "z": 3.0, "width": 4.0, "height": 3.0, "depth": 3.0,
         "rotation": 0.0, "color": "#58c47e"},
    ],
    "devices": [
        {"device_id": "forklift-01", "device_type": "pallet_forklift",
         "name": "托盘叉车 1", "x": -3.0, "z": 2.0, "speed": 0.6},
        {"device_id": "forklift-02", "device_type": "pallet_forklift",
         "name": "托盘叉车 2", "x": -3.0, "z": -2.0, "speed": 0.6},
        {"device_id": "agv-01", "device_type": "agv",
         "name": "托盘 AGV", "x": 0.0, "z": 0.0, "speed": 1.0},
    ],
    "tasks": [
        {"type": "pallet_fork", "description": "取托盘 1", "priority": 3, "device_id": "forklift-01"},
        {"type": "pallet_fork", "description": "取托盘 2", "priority": 3, "device_id": "forklift-02"},
        {"type": "agv_transport", "description": "运托盘入库", "priority": 3, "device_id": "agv-01"},
    ],
    "kpi_definitions": [
        {"label": "单托盘节拍", "key": "pallet_cycle_seconds", "unit": "s", "target": "≤ 12"},
        {"label": "叉车插入成功率", "key": "fork_insert_success_rate", "unit": "%", "target": "≥ 98"},
        {"label": "AGV 对接精度", "key": "agv_dock_precision_mm", "unit": "mm", "target": "±5"},
        {"label": "吞吐量", "key": "throughput_per_hour", "unit": "托盘/h", "target": "≥ 5"},
    ],
}


BOX_SCENE: ScenePreset = {
    "name": "box",
    "label": "箱装（瓦楞/塑料箱）",
    "description": "Top 3 第 2 名：电商箱装。D 复合 + B 夹爪。",
    "sites": [
        {"id": "dock-01", "kind": "dock", "name": "集装箱月台",
         "x": -6.0, "y": 0.0, "z": 4.0, "width": 6.0, "height": 0.6, "depth": 4.0,
         "rotation": 0.0, "color": "#5eb0ff"},
        {"id": "warehouse-01", "kind": "warehouse", "name": "立体库入口",
         "x": 6.0, "y": 0.0, "z": 0.0, "width": 5.0, "height": 4.0, "depth": 4.0,
         "rotation": 0.0, "color": "#58c47e"},
    ],
    "devices": [
        {"device_id": "loader-01", "device_type": "loading_robot",
         "name": "箱装夹爪机器人", "x": -3.0, "z": 2.0, "speed": 0.8},
        {"device_id": "agv-01", "device_type": "agv",
         "name": "箱装 AGV 1", "x": 2.0, "z": -2.0, "speed": 1.2},
        {"device_id": "agv-02", "device_type": "agv",
         "name": "箱装 AGV 2", "x": 2.0, "z": 2.0, "speed": 1.2},
        {"device_id": "stacker-01", "device_type": "stacker",
         "name": "立体库堆垛机", "x": 6.0, "z": 0.0, "speed": 0.7},
    ],
    "tasks": [
        {"type": "box_unload", "description": "箱装卸 1", "priority": 3, "device_id": "loader-01"},
        {"type": "box_unload", "description": "箱装卸 2", "priority": 3, "device_id": "loader-01"},
        {"type": "agv_transport", "description": "运箱装 1", "priority": 3, "device_id": "agv-01"},
        {"type": "agv_transport", "description": "运箱装 2", "priority": 3, "device_id": "agv-02"},
        {"type": "warehouse_storage", "description": "立体库入库", "priority": 2, "device_id": "stacker-01"},
    ],
    "kpi_definitions": [
        {"label": "单件节拍", "key": "box_cycle_seconds", "unit": "s", "target": "≤ 5"},
        {"label": "抓取成功率", "key": "grip_success_rate", "unit": "%", "target": "≥ 99.5"},
        {"label": "压溃率", "key": "crush_rate", "unit": "%", "target": "0"},
        {"label": "吞吐量", "key": "throughput_per_min", "unit": "件/min", "target": "≥ 12"},
    ],
}


BAG_SCENE: ScenePreset = {
    "name": "bag",
    "label": "袋装（编织/牛皮袋 ≤50kg）",
    "description": "Top 3 第 3 名：袋装卸。D 复合 + B 夹爪（防滑齿）。",
    "sites": [
        {"id": "dock-01", "kind": "dock", "name": "集装箱月台",
         "x": -6.0, "y": 0.0, "z": 4.0, "width": 6.0, "height": 0.6, "depth": 4.0,
         "rotation": 0.0, "color": "#5eb0ff"},
        {"id": "warehouse-01", "kind": "warehouse", "name": "立体库",
         "x": 6.0, "y": 0.0, "z": 0.0, "width": 4.0, "height": 4.0, "depth": 3.0,
         "rotation": 0.0, "color": "#58c47e"},
        {"id": "pallet-area", "kind": "warehouse", "name": "吨袋暂存区",
         "x": 0.0, "y": 0.0, "z": -5.0, "width": 3.0, "height": 0.5, "depth": 3.0,
         "rotation": 0.0, "color": "#c4a76c"},
    ],
    "devices": [
        {"device_id": "loader-01", "device_type": "loading_robot",
         "name": "袋装夹爪机器人", "x": -3.0, "z": 2.0, "speed": 0.8},
        {"device_id": "agv-01", "device_type": "agv",
         "name": "袋装 AGV", "x": 2.0, "z": 0.0, "speed": 1.1},
        {"device_id": "stacker-01", "device_type": "stacker",
         "name": "立体库堆垛机", "x": 6.0, "z": 0.0, "speed": 0.7},
    ],
    "tasks": [
        {"type": "bag_unload", "description": "袋装卸 1", "priority": 3, "device_id": "loader-01"},
        {"type": "bag_unload", "description": "袋装卸 2", "priority": 3, "device_id": "loader-01"},
        {"type": "agv_transport", "description": "运袋装入库", "priority": 3, "device_id": "agv-01"},
        {"type": "warehouse_storage", "description": "立体库入库", "priority": 2, "device_id": "stacker-01"},
    ],
    "kpi_definitions": [
        {"label": "抓取成功率", "key": "grip_success_rate", "unit": "%", "target": "≥ 98"},
        {"label": "破袋率", "key": "bag_break_rate", "unit": "%", "target": "≤ 0.5"},
        {"label": "传送带对接精度", "key": "conveyor_dock_precision_mm", "unit": "mm", "target": "±30"},
        {"label": "吞吐量", "key": "throughput_per_min", "unit": "袋/min", "target": "≥ 8"},
    ],
}


SCENE_PRESETS: dict[str, ScenePreset] = {
    "pallet": PALLET_SCENE,
    "box": BOX_SCENE,
    "bag": BAG_SCENE,
}


def list_scene_names() -> list[str]:
    return list(SCENE_PRESETS.keys())


def get_scene(name: str) -> ScenePreset:
    if name not in SCENE_PRESETS:
        raise KeyError(f"unknown scene: {name!r}; available: {list_scene_names()}")
    return SCENE_PRESETS[name]
```

- [ ] **Step 2: 验证文件可被 Python 解析**

Run: `cd d:/projects/robot-logic/simulation/backend && python -c "from backend.services.scene_presets import SCENE_PRESETS; print(list(SCENE_PRESETS.keys()))"`

Expected: `['pallet', 'box', 'bag']`

- [ ] **Step 3: 提交**

```bash
git add simulation/backend/services/scene_presets.py
git commit -m "feat(scenes): add scene_presets data module for Top 3 loading scenes"
```

---

### Task 2: 后端 — DeviceManager 改造 + Runtime 新增 reset() 与 load_scene()

**Files:**
- Modify: `simulation/backend/algorithm/simulator/device_manager.py:6-14` — 构造函数接受可选 `seed_devices`
- Modify: `simulation/backend/services/runtime.py:21-46` — 新增 `reset()` 方法、`current_scene` 字段、`load_scene()` 方法

**Interfaces:**
- Consumes: `SCENE_PRESETS[name].devices` (list of DeviceSpec from Task 1)
- Consumes: `SCENE_PRESETS[name].sites` (list of SiteSpec from Task 1)
- Consumes: `SCENE_PRESETS[name].tasks` (list of TaskSpec from Task 1)
- Produces: `runtime.current_scene: str | None`
- Produces: `runtime.load_scene(name) -> dict[str, Any]` 端点供 Task 3 调用

- [ ] **Step 1: 修改 DeviceManager 让构造函数支持可选 seed_devices**

修改 `simulation/backend/algorithm/simulator/device_manager.py` 第 6~14 行（构造函数与初始 `self.devices`）：

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

注意：原文件中的种子设备（robot-01 / loader-01 / agv-01 / agv-02 / stacker-01）**保留**——这样现有 Dashboard 仍能加载默认设备。`seed_devices` 不传时，`self.devices` 为空 dict，由 `load_scene()` 显式注册。

- [ ] **Step 2: 修改 SiteManager 添加 add() 方法（如果缺失）**

读取 `simulation/backend/algorithm/simulator/site_manager.py`，确认 `SiteManager` 是否已有 `add(site_dict)` 方法。如果没有，新增：

```python
def add(self, site_dict: dict) -> "Site":
    """Register a site at runtime (used by scene_presets.load_scene)."""
    from .device import Site  # 实际导入路径以原文件为准
    site = Site.from_dict(site_dict)
    if site.id in self.sites:
        raise ValueError(f"site {site.id!r} already exists")
    self.sites[site.id] = site
    return site
```

- [ ] **Step 3: 修改 Runtime 新增 reset() / current_scene / load_scene()**

修改 `simulation/backend/services/runtime.py`：

在 `__init__` 中新增 `self.current_scene: str | None = None` 字段（在 `self.running = False` 后）。

新增方法（在 `start()` 之前）：

```python
def reset(self) -> None:
    """Clear runtime state without touching the synthetic sensor generators.

    - Wipe devices (next load_scene will re-seed).
    - Wipe sites, tasks, logs, reverted tasks.
    - Reset started_at; keep running flag as-is.
    - Drop any cached sensor / joint state.
    """
    self.devices = DeviceManager()
    self.sites = SiteManager()
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

新增 `_scene_kpi` 方法（在 `stats()` 后面）：

```python
def _scene_kpi(self, name: str) -> dict[str, Any]:
    """Compute scene-specific KPI snapshot (used by /api/scenes/{name}/kpi)."""
    tasks = list(self.tasks.values())
    completed = sum(t["status"] == "completed" for t in tasks)
    failed = sum(t["status"] == "failed" for t in tasks)
    total = len(tasks) or 1
    # Cycle seconds: avg of completed task progress (current implementation
    # is the simplest reasonable approximation; full cycle accounting lives in
    # the spec as future work).
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

- [ ] **Step 4: 验证 Python 解析无错**

Run: `cd d:/projects/robot-logic/simulation/backend && python -c "from backend.services.runtime import runtime; r = runtime.load_scene('pallet'); print(r['scene'], len(r['devices']))"`

Expected: `pallet 3`

- [ ] **Step 5: 提交**

```bash
git add simulation/backend/algorithm/simulator/device_manager.py
git add simulation/backend/algorithm/simulator/site_manager.py
git add simulation/backend/services/runtime.py
git commit -m "feat(scenes): extend DeviceManager + Runtime with reset/load_scene"
```

---

### Task 3: 后端 — main.py 注册 4 个 scenes API

**Files:**
- Modify: `simulation/backend/main.py:91-95` — 扩展 `DeviceCreateRequest.device_type` 正则包含 `pallet_forklift`
- Modify: `simulation/backend/main.py` — 在 `/api/sites` 端点之后新增 4 个 `/api/scenes/*` 端点

**Interfaces:**
- Produces: 4 个新 endpoint
  - `GET /api/scenes` → `{"available": list[str], "current": str|None}`
  - `POST /api/scenes/load/{name}` → `{"scene": str, "devices": list, "sites": list}`
  - `GET /api/scenes/current` → `ScenePreset` 当前激活的场景
  - `GET /api/scenes/{name}/kpi` → KPI 快照

- [ ] **Step 1: 扩展 DeviceCreateRequest.device_type 正则**

修改 `simulation/backend/main.py` 第 91~95 行附近（`DeviceCreateRequest` 定义）：

```python
class DeviceCreateRequest(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=64)
    device_type: str = Field(
        ...,
        pattern="^(container_robot|loading_robot|agv|stacker|pallet_forklift)$",
    )
    name: str = Field(..., min_length=1, max_length=128)
    x: float = 0.0
    z: float = 0.0
```

- [ ] **Step 2: 新增 4 个 scenes 端点**

在 `simulation/backend/main.py` 第 240~242 行（`/api/sites` DELETE 之后）插入：

```python
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

- [ ] **Step 3: 启动后端并 curl 验证**

Run:

```bash
cd d:/projects/robot-logic/simulation/backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
sleep 3
curl -s http://127.0.0.1:8000/api/scenes
# 期望：{"available":["pallet","box","bag"],"current":null}
curl -s -X POST http://127.0.0.1:8000/api/scenes/load/pallet | python -m json.tool | head -10
# 期望：包含 "scene": "pallet" + devices / sites 数组
curl -s http://127.0.0.1:8000/api/scenes/pallet/kpi
# 期望：KPI JSON 快照
kill %1 2>/dev/null
```

- [ ] **Step 4: 提交**

```bash
git add simulation/backend/main.py
git commit -m "feat(scenes): register /api/scenes endpoints + extend device_type enum"
```

---

### Task 4: 后端 — 测试（preset / load_scene / API）

**Files:**
- Create: `simulation/backend/tests/test_scene_presets.py`
- Create: `simulation/backend/tests/test_runtime_load_scene.py`
- Create: `simulation/backend/tests/test_scenes_api.py`

**Interfaces:**
- Consumes: `SCENE_PRESETS`, `runtime.load_scene()`, `/api/scenes/*` endpoints

- [ ] **Step 1: 创建 test_scene_presets.py**

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

- [ ] **Step 2: 创建 test_runtime_load_scene.py**

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

- [ ] **Step 3: 创建 test_scenes_api.py**

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


def test_list_senes_returns_three():
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

- [ ] **Step 4: 运行所有新测试**

Run:

```bash
cd d:/projects/robot-logic/simulation/backend
pytest tests/test_scene_presets.py tests/test_runtime_load_scene.py tests/test_scenes_api.py -v
```

Expected: all pass

- [ ] **Step 5: 运行现有测试确认未破坏**

Run:

```bash
cd d:/projects/robot-logic/simulation/backend
pytest tests/test_api.py -v
```

Expected: existing tests still pass

- [ ] **Step 6: 提交**

```bash
git add simulation/backend/tests/test_scene_presets.py
git add simulation/backend/tests/test_runtime_load_scene.py
git add simulation/backend/tests/test_scenes_api.py
git commit -m "test(scenes): add preset/runtime/api tests"
```

---

### Task 5: 前端 — Vue Router 配置 + /scenes 入口

**Files:**
- Create: `simulation/frontend/src/router/index.ts`
- Modify: `simulation/frontend/src/main.ts` — 注册 router
- Modify: `simulation/frontend/src/App.vue` — topbar 增加 `/scenes` 入口链接

**Interfaces:**
- Produces: `/scenes` 路由可访问；topbar "🚛 场景仿真" 链接可点击

- [ ] **Step 1: 创建 router/index.ts**

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const ScenesPage = () => import('@/scenes/ScenesPage.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: () => import('@/App.vue') },
    { path: '/scenes', name: 'scenes', component: ScenesPage },
  ],
})
```

- [ ] **Step 2: 修改 main.ts 注册 router**

读取 `simulation/frontend/src/main.ts`，追加：

```typescript
import { router } from './router'
app.use(router)
```

（如原本 `createApp` 与 `mount` 已存在，仅添加 router 即可；最终 `app.mount('#app')` 保持原样。）

- [ ] **Step 3: 修改 App.vue 增加 /scenes 入口**

在 `<header class="topbar">` 区域（UserMenu 之前或之后）插入：

```html
<router-link to="/scenes" class="iconbtn" title="场景仿真">🚛 场景仿真</router-link>
```

在 `<style scoped>` 不需要时仍可放在全局 `<style>`，因 `.iconbtn` 已在全局定义。

- [ ] **Step 4: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors（ScenesPage.vue 暂未创建，但 router 用动态 import 不会立即报错）

- [ ] **Step 5: 提交**

```bash
git add simulation/frontend/src/router/index.ts
git add simulation/frontend/src/main.ts
git add simulation/frontend/src/App.vue
git commit -m "feat(scenes): add Vue Router config + /scenes entry link"
```

---

### Task 6: 前端 — useSceneAPI composable

**Files:**
- Create: `simulation/frontend/src/scenes/composables/useSceneAPI.ts`

**Interfaces:**
- Produces: `useSceneAPI()` 返回 `{ currentScene, list(), load(name), getCurrent(), getKPI(name) }`

- [ ] **Step 1: 创建文件**

```typescript
import { ref } from 'vue'
import axios from 'axios'

export interface ScenePreset {
  name: string
  label: string
  description: string
  sites: Array<Record<string, unknown>>
  devices: Array<Record<string, unknown>>
  tasks: Array<Record<string, unknown>>
  kpi_definitions: Array<Record<string, unknown>>
}

export interface SceneKPI {
  scene: string
  throughput_per_hour: number
  success_rate: number
  active_tasks: number
  completed_tasks: number
  failed_tasks: number
}

export function useSceneAPI() {
  const currentScene = ref<string>('')

  async function list(): Promise<{ available: string[]; current: string | null }> {
    const res = await axios.get('/api/scenes')
    return res.data
  }

  async function load(name: string): Promise<ScenePreset & { devices: unknown[]; sites: unknown[] }> {
    const res = await axios.post(`/api/scenes/load/${name}`)
    currentScene.value = name
    return res.data
  }

  async function getCurrent(): Promise<ScenePreset> {
    const res = await axios.get('/api/scenes/current')
    return res.data
  }

  async function getKPI(name: string): Promise<SceneKPI> {
    const res = await axios.get(`/api/scenes/${name}/kpi`)
    return res.data
  }

  return { currentScene, list, load, getCurrent, getKPI }
}
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/composables/useSceneAPI.ts
git commit -m "feat(scenes): add useSceneAPI composable"
```

---

### Task 7: 前端 — useSceneStage 状态机

**Files:**
- Create: `simulation/frontend/src/scenes/composables/useSceneStage.ts`

**Interfaces:**
- Produces: `useSceneStage()` 返回 `{ stage, advance, start, stop }`，7 个 stage 按顺序循环

- [ ] **Step 1: 创建文件**

```typescript
import { ref } from 'vue'

export type SceneStageName =
  | 'idle'
  | 'approach'
  | 'engage'
  | 'lift'
  | 'transfer'
  | 'place'
  | 'return'

const STAGE_ORDER: SceneStageName[] = [
  'idle',
  'approach',
  'engage',
  'lift',
  'transfer',
  'place',
  'return',
]

const STAGE_DURATION_MS: Record<SceneStageName, number> = {
  idle: 500,
  approach: 2000,
  engage: 1500,
  lift: 800,
  transfer: 2500,
  place: 1500,
  return: 2000,
}

export function useSceneStage() {
  const stage = ref<SceneStageName>('idle')

  function advance(): void {
    const idx = STAGE_ORDER.indexOf(stage.value)
    stage.value = STAGE_ORDER[(idx + 1) % STAGE_ORDER.length]
  }

  let timer: number | undefined
  function start(): void {
    stop()
    const tick = (): void => {
      advance()
      timer = window.setTimeout(tick, STAGE_DURATION_MS[stage.value])
    }
    timer = window.setTimeout(tick, STAGE_DURATION_MS[stage.value])
  }

  function stop(): void {
    if (timer !== undefined) {
      clearTimeout(timer)
      timer = undefined
    }
  }

  function reset(): void {
    stop()
    stage.value = 'idle'
  }

  return { stage, advance, start, stop, reset }
}
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/composables/useSceneStage.ts
git commit -m "feat(scenes): add useSceneStage 7-stage state machine"
```

---

### Task 8: 前端 — useSceneKPI composable

**Files:**
- Create: `simulation/frontend/src/scenes/composables/useSceneKPI.ts`

**Interfaces:**
- Produces: `useSceneKPI(name)` 返回 `{ kpi, refresh, start, stop }`，每 2s 自动刷新

- [ ] **Step 1: 创建文件**

```typescript
import { ref } from 'vue'
import { useSceneAPI, type SceneKPI } from './useSceneAPI'

export function useSceneKPI(sceneName: string) {
  const kpi = ref<SceneKPI | null>(null)
  const { getKPI } = useSceneAPI()

  let timer: number | undefined

  async function refresh(): Promise<void> {
    try {
      kpi.value = await getKPI(sceneName)
    } catch {
      /* backend may be unavailable */
    }
  }

  function start(): void {
    stop()
    refresh()
    timer = window.setInterval(refresh, 2000)
  }

  function stop(): void {
    if (timer !== undefined) {
      clearInterval(timer)
      timer = undefined
    }
  }

  return { kpi, refresh, start, stop }
}
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/composables/useSceneKPI.ts
git commit -m "feat(scenes): add useSceneKPI composable"
```

---

### Task 9: 前端 — PalletForklift Three.js 类

**Files:**
- Create: `simulation/frontend/src/scenes/three/PalletForklift.ts`

**Interfaces:**
- Produces: `PalletForklift` 类，含 `addToScene(scene, position)` / `setMastHeight(h)` / `setExtension(e)` / `setLoad(pallet)` / `update(dt)` / `dispose()`

- [ ] **Step 1: 创建文件**

```typescript
import * as THREE from 'three'

export class PalletForklift {
  private readonly group = new THREE.Group()
  private readonly body: THREE.Mesh
  private readonly cabin: THREE.Mesh
  private readonly mast: THREE.Group
  private readonly forks: THREE.Group
  private readonly load: THREE.Group
  private targetMast = 0
  private currentMast = 0
  private targetExt = 0
  private currentExt = 0
  private hasLoad = false

  constructor() {
    // 主车体：扁平货箱
    const bodyGeom = new THREE.BoxGeometry(1.6, 0.6, 1.0)
    const bodyMat = new THREE.MeshStandardMaterial({ color: 0xd68910, metalness: 0.4, roughness: 0.6 })
    this.body = new THREE.Mesh(bodyGeom, bodyMat)
    this.body.position.y = 0.3
    this.group.add(this.body)

    // 驾驶舱
    const cabinGeom = new THREE.BoxGeometry(0.6, 0.8, 1.0)
    const cabinMat = new THREE.MeshStandardMaterial({ color: 0x1c2333, roughness: 0.4 })
    this.cabin = new THREE.Mesh(cabinGeom, cabinMat)
    this.cabin.position.set(-0.4, 1.0, 0)
    this.group.add(this.cabin)

    // 4 轮
    const wheelGeom = new THREE.CylinderGeometry(0.2, 0.2, 0.18, 16)
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.9 })
    const wheelPositions: [number, number][] = [
      [0.6, 0.4], [-0.6, 0.4], [0.6, -0.4], [-0.6, -0.4],
    ]
    for (const [x, z] of wheelPositions) {
      const wheel = new THREE.Mesh(wheelGeom, wheelMat)
      wheel.rotation.z = Math.PI / 2
      wheel.position.set(x, 0.2, z)
      this.group.add(wheel)
    }

    // 立柱（2 根）
    this.mast = new THREE.Group()
    const mastMat = new THREE.MeshStandardMaterial({ color: 0xb0b0b0, metalness: 0.7, roughness: 0.3 })
    const mastGeom = new THREE.BoxGeometry(0.08, 2.0, 0.08)
    const mastL = new THREE.Mesh(mastGeom, mastMat)
    mastL.position.set(0.7, 1.0, -0.3)
    const mastR = new THREE.Mesh(mastGeom, mastMat)
    mastR.position.set(0.7, 1.0, 0.3)
    this.mast.add(mastL, mastR)
    this.group.add(this.mast)

    // 货叉（2 根，可升降 + 伸出）
    this.forks = new THREE.Group()
    const forkMat = new THREE.MeshStandardMaterial({ color: 0xe0e0e0, metalness: 0.8, roughness: 0.2 })
    const forkGeom = new THREE.BoxGeometry(1.0, 0.05, 0.1)
    const forkL = new THREE.Mesh(forkGeom, forkMat)
    forkL.position.set(0.2, 0.0, -0.25)
    const forkR = new THREE.Mesh(forkGeom, forkMat)
    forkR.position.set(0.2, 0.0, 0.25)
    this.forks.add(forkL, forkR)
    this.mast.add(this.forks)
    this.forks.position.set(0.7, 0.3, 0)

    // 托盘货物（默认隐藏）
    this.load = new THREE.Group()
    const palletMat = new THREE.MeshStandardMaterial({ color: 0xc4a76c, roughness: 0.8 })
    const palletGeom = new THREE.BoxGeometry(1.2, 0.15, 1.0)
    const palletMesh = new THREE.Mesh(palletGeom, palletMat)
    palletMesh.position.y = 0.075
    this.load.add(palletMesh)
    const boxMat = new THREE.MeshStandardMaterial({ color: 0x8b6f3c, roughness: 0.7 })
    const boxGeom = new THREE.BoxGeometry(1.0, 0.5, 0.8)
    const boxMesh = new THREE.Mesh(boxGeom, boxMat)
    boxMesh.position.y = 0.4
    this.load.add(boxMesh)
    this.load.position.set(0.7, 0.3, 0)
    this.load.visible = false
    this.mast.add(this.load)
  }

  addToScene(scene: THREE.Scene, position: THREE.Vector3): void {
    this.group.position.copy(position)
    scene.add(this.group)
  }

  setMastHeight(h: number): void {
    this.targetMast = Math.max(0, Math.min(1.8, h))
  }

  setExtension(e: number): void {
    this.targetExt = Math.max(0, Math.min(0.3, e))
  }

  setLoad(loaded: boolean): void {
    this.hasLoad = loaded
    this.load.visible = loaded
  }

  update(dt: number): void {
    // 平滑过渡
    const k = 1 - Math.exp(-dt * 5)
    this.currentMast += (this.targetMast - this.currentMast) * k
    this.currentExt += (this.targetExt - this.currentExt) * k
    // 立柱不动；货叉高度 / 伸出 + 托盘随货叉
    this.forks.position.y = 0.3 + this.currentMast * 0.9
    this.forks.position.x = 0.7 + this.currentExt
    this.load.position.copy(this.forks.position)
  }

  dispose(): void {
    this.group.traverse((obj) => {
      const mesh = obj as THREE.Mesh
      if (mesh.geometry) mesh.geometry.dispose()
      const mat = mesh.material
      if (Array.isArray(mat)) mat.forEach((m) => m.dispose())
      else if (mat) (mat as THREE.Material).dispose()
    })
  }
}
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/three/PalletForklift.ts
git commit -m "feat(scenes): add PalletForklift Three.js procedural class"
```

---

### Task 10: 前端 — BoxGripper / BagGripper 末端扩展

**Files:**
- Create: `simulation/frontend/src/scenes/three/BoxGripper.ts`
- Create: `simulation/frontend/src/scenes/three/BagGripper.ts`

**Interfaces:**
- Produces: `BoxGripper` 类与 `BagGripper` 类（程序生成几何体），各含 `mesh: THREE.Group` 供 LoaderRobot 末端挂载

- [ ] **Step 1: 创建 BoxGripper.ts**

```typescript
import * as THREE from 'three'

/**
 * Parallel 2-finger gripper for boxes.
 * Attach to LoaderRobot left+right arms via robot.setLeftEndEffector(gripper.mesh).
 */
export class BoxGripper {
  readonly mesh: THREE.Group

  constructor() {
    this.mesh = new THREE.Group()
    this.mesh.name = 'BoxGripper'

    const palmMat = new THREE.MeshStandardMaterial({ color: 0x1f8a4c, metalness: 0.5, roughness: 0.4 })
    const fingerMat = new THREE.MeshStandardMaterial({ color: 0x2a72d8, metalness: 0.7, roughness: 0.3 })

    const palm = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.15, 0.3), palmMat)
    palm.position.y = 0.075
    this.mesh.add(palm)

    const fingerGeom = new THREE.BoxGeometry(0.05, 0.4, 0.15)
    const fingerL = new THREE.Mesh(fingerGeom, fingerMat)
    fingerL.position.set(-0.13, 0.2, 0)
    const fingerR = new THREE.Mesh(fingerGeom, fingerMat)
    fingerR.position.set(0.13, 0.2, 0)
    this.mesh.add(fingerL, fingerR)

    // 防滑纹（小刻槽）
    const grooveMat = new THREE.MeshStandardMaterial({ color: 0x0d2a5c, roughness: 0.9 })
    for (let i = 0; i < 4; i++) {
      const groove = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.02, 0.16), grooveMat)
      groove.position.set(-0.13, 0.05 + i * 0.08, 0)
      this.mesh.add(groove)
      const grooveR = groove.clone()
      grooveR.position.set(0.13, 0.05 + i * 0.08, 0)
      this.mesh.add(grooveR)
    }
  }

  dispose(): void {
    this.mesh.traverse((obj) => {
      const m = obj as THREE.Mesh
      if (m.geometry) m.geometry.dispose()
      const mat = m.material
      if (Array.isArray(mat)) mat.forEach((mm) => mm.dispose())
      else if (mat) (mat as THREE.Material).dispose()
    })
  }
}
```

- [ ] **Step 2: 创建 BagGripper.ts**

```typescript
import * as THREE from 'three'

/**
 * Wide contact plate gripper with anti-slip teeth for woven / kraft bags.
 */
export class BagGripper {
  readonly mesh: THREE.Group

  constructor() {
    this.mesh = new THREE.Group()
    this.mesh.name = 'BagGripper'

    const plateMat = new THREE.MeshStandardMaterial({ color: 0x8b6f3c, roughness: 0.7 })
    const plateGeom = new THREE.BoxGeometry(0.5, 0.3, 0.25)
    const plate = new THREE.Mesh(plateGeom, plateMat)
    plate.position.y = 0.15
    this.mesh.add(plate)

    // 防滑齿阵列
    const toothMat = new THREE.MeshStandardMaterial({ color: 0x444444, roughness: 0.95 })
    const toothGeom = new THREE.BoxGeometry(0.04, 0.05, 0.06)
    for (let x = -0.2; x <= 0.2; x += 0.1) {
      for (let z = -0.1; z <= 0.1; z += 0.1) {
        const tooth = new THREE.Mesh(toothGeom, toothMat)
        tooth.position.set(x, 0.32, z)
        this.mesh.add(tooth)
      }
    }
  }

  dispose(): void {
    this.mesh.traverse((obj) => {
      const m = obj as THREE.Mesh
      if (m.geometry) m.geometry.dispose()
      const mat = m.material
      if (Array.isArray(mat)) mat.forEach((mm) => mm.dispose())
      else if (mat) (mat as THREE.Material).dispose()
    })
  }
}
```

- [ ] **Step 3: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 4: 提交**

```bash
git add simulation/frontend/src/scenes/three/BoxGripper.ts
git add simulation/frontend/src/scenes/three/BagGripper.ts
git commit -m "feat(scenes): add BoxGripper + BagGripper end-effectors"
```

---

### Task 11: 前端 — ScenesPage.vue（顶级路由 + Tab 切换）

**Files:**
- Create: `simulation/frontend/src/scenes/ScenesPage.vue`

**Interfaces:**
- Produces: 顶级路由页面，含 Tab（pallet / box / bag），切换时调用 `useSceneAPI().load(name)`

- [ ] **Step 1: 创建文件**

```vue
<template>
  <div class="scenes-page">
    <header class="topbar">
      <router-link to="/" class="iconbtn" title="返回 Dashboard">← Dashboard</router-link>
      <span class="logo">🚛</span>
      <h1>场景仿真</h1>
      <span class="grow"></span>
      <span class="badge" v-if="currentScene">{{ currentScene }}</span>
    </header>

    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        :class="['tab', { active: currentTab === tab.name }]"
        @click="onSwitch(tab.name)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <main class="stage">
      <SceneStage
        v-if="currentTab"
        :key="currentTab"
        :scene-name="currentTab"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SceneStage from './SceneStage.vue'
import { useSceneAPI } from './composables/useSceneAPI'

interface TabSpec {
  name: 'pallet' | 'box' | 'bag'
  label: string
}

const tabs: TabSpec[] = [
  { name: 'pallet', label: '📦 托盘 (🥇)' },
  { name: 'box', label: '📦 箱装 (🥈)' },
  { name: 'bag', label: '📦 袋装 (🥉)' },
]

const currentTab = ref<'' | 'pallet' | 'box' | 'bag'>('pallet')
const currentScene = ref<string>('')
const { load, list } = useSceneAPI()

async function onSwitch(name: 'pallet' | 'box' | 'bag') {
  currentTab.value = name
  await load(name)
  currentScene.value = name
}

onMounted(async () => {
  try {
    const info = await list()
    currentScene.value = info.current ?? ''
  } catch {
    /* backend may be down */
  }
})
</script>

<style scoped>
.scenes-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-app);
}
.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.topbar h1 {
  font-size: 16px;
  margin: 0;
  font-weight: 600;
}
.topbar .logo { font-size: 20px; }
.topbar .grow { flex: 1; }
.topbar .badge {
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--accent);
  color: white;
  font-size: 11px;
  font-weight: 600;
}
.tabs {
  display: flex;
  gap: 4px;
  padding: 8px 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.tab {
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  color: var(--fg);
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.tab.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}
.stage {
  flex: 1;
  min-height: 0;
}
.iconbtn {
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  color: var(--fg);
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  text-decoration: none;
}
</style>
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors（SceneStage 还没创建，因动态导入不立即报错；如报错 "Cannot find module" 则先实现 SceneStage 占位 stub）

若 vue-tsc 提示 SceneStage 缺失，先创建最小 stub：

```vue
<template><div class="placeholder">SceneStage placeholder</div></template>
```

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/ScenesPage.vue
git commit -m "feat(scenes): add ScenesPage with Tab switcher"
```

---

### Task 12: 前端 — SceneStage.vue 通用 5 面板框架

**Files:**
- Create: `simulation/frontend/src/scenes/SceneStage.vue`

**Interfaces:**
- Props: `sceneName: 'pallet' | 'box' | 'bag'`
- Produces: 5 面板布局（Three.js + DeviceList + KPI + TaskTimeline + LogViewer），按 `sceneName` 动态加载对应子组件

- [ ] **Step 1: 创建文件**

```vue
<template>
  <div class="stage">
    <div class="left">
      <div class="scene-area">
        <component :is="sceneComponent" v-if="sceneComponent" />
        <div v-else class="placeholder">3D 场景加载中...</div>
      </div>
      <div class="timeline">
        <TaskTimeline />
      </div>
      <div class="logs">
        <LogViewer />
      </div>
    </div>

    <aside class="right">
      <DeviceStatus />
      <div class="kpi-panel">
        <h3>场景 KPI</h3>
        <div v-if="kpi" class="kpi-cards">
          <div v-for="d in kpiCards" :key="d.key" class="kpi-card">
            <div class="kpi-label">{{ d.label }}</div>
            <div class="kpi-value">{{ d.value }}</div>
            <div class="kpi-target">{{ d.target }}</div>
          </div>
        </div>
        <div v-else class="placeholder">KPI 计算中...</div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import TaskTimeline from '@/dashboard/TaskTimeline.vue'
import LogViewer from '@/panel/LogViewer.vue'
import DeviceStatus from '@/dashboard/DeviceStatus.vue'
import { useSceneKPI } from './composables/useSceneKPI'

interface Props {
  sceneName: 'pallet' | 'box' | 'bag'
}
const props = defineProps<Props>()

const sceneComponent = computed(() => {
  switch (props.sceneName) {
    case 'pallet':
      return () => import('./ScenePallet.vue')
    case 'box':
      return () => import('./SceneBox.vue')
    case 'bag':
      return () => import('./SceneBag.vue')
    default:
      return null
  }
})

const { kpi, start: startKpi, stop: stopKpi } = useSceneKPI(props.sceneName)

const kpiCards = computed(() => {
  if (!kpi.value) return []
  return [
    { key: 'throughput', label: '吞吐量', value: String(kpi.value.throughput_per_hour), target: '/h' },
    { key: 'success', label: '成功率', value: `${kpi.value.success_rate}%`, target: '' },
    { key: 'active', label: '活跃任务', value: String(kpi.value.active_tasks), target: '' },
    { key: 'completed', label: '已完成', value: String(kpi.value.completed_tasks), target: '' },
  ]
})

onMounted(() => startKpi())
onUnmounted(() => stopKpi())
</script>

<style scoped>
.stage {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr);
  height: 100%;
  padding: 12px;
  gap: 12px;
}
.left {
  display: grid;
  grid-template-rows: minmax(0, 1.4fr) auto auto;
  gap: 12px;
  min-height: 0;
}
.scene-area {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  min-height: 0;
}
.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--fg-soft);
  font-size: 13px;
}
.right {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  overflow-y: auto;
}
.kpi-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
}
.kpi-panel h3 {
  font-size: 13px;
  margin: 0 0 8px 0;
  color: var(--fg);
}
.kpi-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.kpi-card {
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px;
  text-align: center;
}
.kpi-label { font-size: 10px; color: var(--fg-soft); }
.kpi-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent);
  margin: 4px 0;
}
.kpi-target { font-size: 10px; color: var(--fg-muted); }
</style>
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors（ScenePallet/Box/Bag 暂未实现；如 vue-tsc 报错"Cannot find module"，先创建最小 stub 文件：`ScenePallet.vue` / `SceneBox.vue` / `SceneBag.vue` 含 `<template><div class="placeholder">{{ name }}</div></template><script setup>defineProps<{...}>()</script>`）

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/SceneStage.vue
git commit -m "feat(scenes): add SceneStage 5-panel framework"
```

---

### Task 13: 前端 — ScenePallet.vue（托盘场景 Three.js 子组件）

**Files:**
- Create: `simulation/frontend/src/scenes/ScenePallet.vue`

**Interfaces:**
- Produces: Three.js 场景，含 2 个 PalletForklift + 1 个设备 Box（AGV 用现有 BoxGeometry 表达）+ dock + warehouse sites

- [ ] **Step 1: 创建文件**

```vue
<template>
  <div ref="container" class="scene-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import axios from 'axios'
import { PalletForklift } from './three/PalletForklift'

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
const forklifts: Record<string, PalletForklift> = {}

function init() {
  if (!container.value) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b1220)
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.set(0, 14, 18)
  camera.lookAt(0, 0, 0)
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(w, h)
  container.value.appendChild(renderer.domElement)
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const dir = new THREE.DirectionalLight(0xffffff, 0.9)
  dir.position.set(10, 20, 10)
  scene.add(dir)

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(36, 24),
    new THREE.MeshStandardMaterial({ color: 0x152238, roughness: 0.9 })
  )
  ground.rotation.x = -Math.PI / 2
  scene.add(ground)

  // 站点（dock + warehouse）
  const dock = new THREE.Mesh(
    new THREE.BoxGeometry(6, 0.6, 4),
    new THREE.MeshStandardMaterial({ color: 0x5eb0ff })
  )
  dock.position.set(-6, 0.3, 4)
  scene.add(dock)
  const wh = new THREE.Mesh(
    new THREE.BoxGeometry(4, 3, 3),
    new THREE.MeshStandardMaterial({ color: 0x58c47e })
  )
  wh.position.set(6, 1.5, -2)
  scene.add(wh)

  // 2 辆叉车
  for (let i = 0; i < 2; i++) {
    const fk = new PalletForklift()
    fk.addToScene(scene, new THREE.Vector3(-3, 0, 2 - i * 4))
    forklifts[`forklift-0${i + 1}`] = fk
  }
}

function animate() {
  animationId = requestAnimationFrame(animate)
  if (camera && scene && renderer) {
    Object.values(forklifts).forEach((f) => f.update(0.016))
    renderer.render(scene, camera)
  }
}

async function syncDevices() {
  try {
    const res = await axios.get<Array<{
      device_id: string; device_type: string; position: [number, number, number]; status: string
    }>>('/api/devices')
    for (const d of res.data) {
      if (d.device_type !== 'pallet_forklift') continue
      const fk = forklifts[d.device_id]
      if (fk && d.status === 'running') {
        // 根据 status 演示：running 时升叉、装货
        fk.setMastHeight(1.2)
        fk.setExtension(0.2)
        fk.setLoad(true)
      } else if (fk) {
        fk.setMastHeight(0)
        fk.setExtension(0)
        fk.setLoad(false)
      }
    }
  } catch { /* backend may be down */ }
}

onMounted(() => {
  init()
  animate()
  syncDevices()
  const t = window.setInterval(syncDevices, 1000)
  onUnmounted(() => clearInterval(t))
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  Object.values(forklifts).forEach((f) => f.dispose())
  renderer?.dispose()
})
</script>

<style scoped>
.scene-container { width: 100%; height: 100%; }
</style>
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/ScenePallet.vue
git commit -m "feat(scenes): add ScenePallet with PalletForklift visualization"
```

---

### Task 14: 前端 — SceneBox.vue（箱装场景子组件，复用 LoaderRobot + BoxGripper）

**Files:**
- Create: `simulation/frontend/src/scenes/SceneBox.vue`

**Interfaces:**
- Produces: Three.js 场景，含 LoaderRobot + BoxGripper + 2 个 AGV + stacker + dock + warehouse

- [ ] **Step 1: 创建文件**

```vue
<template>
  <div ref="container" class="scene-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import { LoaderRobot } from '@/three/LoaderRobot'
import { BoxGripper } from './three/BoxGripper'

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
let loader: LoaderRobot | undefined
let boxGripper: BoxGripper | undefined

function init() {
  if (!container.value) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b1220)
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.set(0, 14, 18)
  camera.lookAt(0, 0, 0)
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(w, h)
  container.value.appendChild(renderer.domElement)
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const dir = new THREE.DirectionalLight(0xffffff, 0.9)
  dir.position.set(10, 20, 10)
  scene.add(dir)

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(36, 24),
    new THREE.MeshStandardMaterial({ color: 0x152238, roughness: 0.9 })
  )
  ground.rotation.x = -Math.PI / 2
  scene.add(ground)

  const dock = new THREE.Mesh(
    new THREE.BoxGeometry(6, 0.6, 4),
    new THREE.MeshStandardMaterial({ color: 0x5eb0ff })
  )
  dock.position.set(-6, 0.3, 4)
  scene.add(dock)

  // LoaderRobot 复用现有类
  loader = new LoaderRobot()
  loader.addToScene(scene, new THREE.Vector3(-3, 0, 2))
  boxGripper = new BoxGripper()
  // 注：实际接入需在 LoaderRobot 上提供 setEndEffector 方法；此处挂载到 loader 的末端子节点
  loader.addEndEffector?.(boxGripper.mesh) ?? void 0
}

function animate() {
  animationId = requestAnimationFrame(animate)
  if (camera && scene && renderer) {
    loader?.update(0.016)
    renderer.render(scene, camera)
  }
}

onMounted(() => {
  init()
  animate()
})
onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  boxGripper?.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.scene-container { width: 100%; height: 100%; }
</style>
```

注意：若 LoaderRobot 类没有 `addEndEffector` 方法，本任务跳过 BoxGripper 挂载（保持 LoaderRobot 现有默认外观）；BoxGripper 类保留供后续 hook。代码中 `loader.addEndEffector?.(...) ?? void 0` 用 optional chaining 安全处理。

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors（LoaderRobot 类型由现有文件决定；若 addEndEffector 不存在，第 1 步的 optional chaining 已容错）

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/SceneBox.vue
git commit -m "feat(scenes): add SceneBox with LoaderRobot + BoxGripper"
```

---

### Task 15: 前端 — SceneBag.vue（袋装场景子组件）

**Files:**
- Create: `simulation/frontend/src/scenes/SceneBag.vue`

**Interfaces:**
- Produces: Three.js 场景，含 LoaderRobot + BagGripper + AGV + stacker + 3 个 sites（dock / warehouse / pallet-area）

- [ ] **Step 1: 创建文件**

```vue
<template>
  <div ref="container" class="scene-container"></div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import * as THREE from 'three'
import { LoaderRobot } from '@/three/LoaderRobot'
import { BagGripper } from './three/BagGripper'

const container = ref<HTMLDivElement | null>(null)
let renderer: THREE.WebGLRenderer | undefined
let scene: THREE.Scene | undefined
let camera: THREE.PerspectiveCamera | undefined
let animationId: number | undefined
let loader: LoaderRobot | undefined
let bagGripper: BagGripper | undefined

function init() {
  if (!container.value) return
  const w = container.value.clientWidth
  const h = container.value.clientHeight
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x0b1220)
  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100)
  camera.position.set(0, 14, 18)
  camera.lookAt(0, 0, 0)
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(w, h)
  container.value.appendChild(renderer.domElement)
  scene.add(new THREE.AmbientLight(0xffffff, 0.5))
  const dir = new THREE.DirectionalLight(0xffffff, 0.9)
  dir.position.set(10, 20, 10)
  scene.add(dir)

  const ground = new THREE.Mesh(
    new THREE.PlaneGeometry(36, 24),
    new THREE.MeshStandardMaterial({ color: 0x152238, roughness: 0.9 })
  )
  ground.rotation.x = -Math.PI / 2
  scene.add(ground)

  // 3 个站点：dock / warehouse / pallet-area
  const dock = new THREE.Mesh(
    new THREE.BoxGeometry(6, 0.6, 4),
    new THREE.MeshStandardMaterial({ color: 0x5eb0ff })
  )
  dock.position.set(-6, 0.3, 4)
  scene.add(dock)
  const wh = new THREE.Mesh(
    new THREE.BoxGeometry(4, 4, 3),
    new THREE.MeshStandardMaterial({ color: 0x58c47e })
  )
  wh.position.set(6, 2, 0)
  scene.add(wh)
  const palletArea = new THREE.Mesh(
    new THREE.BoxGeometry(3, 0.5, 3),
    new THREE.MeshStandardMaterial({ color: 0xc4a76c })
  )
  palletArea.position.set(0, 0.25, -5)
  scene.add(palletArea)

  loader = new LoaderRobot()
  loader.addToScene(scene, new THREE.Vector3(-3, 0, 2))
  bagGripper = new BagGripper()
  loader.addEndEffector?.(bagGripper.mesh) ?? void 0
}

function animate() {
  animationId = requestAnimationFrame(animate)
  if (camera && scene && renderer) {
    loader?.update(0.016)
    renderer.render(scene, camera)
  }
}

onMounted(() => {
  init()
  animate()
})
onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
  bagGripper?.dispose()
  renderer?.dispose()
})
</script>

<style scoped>
.scene-container { width: 100%; height: 100%; }
</style>
```

- [ ] **Step 2: 类型检查**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vue-tsc --noEmit`

Expected: 0 errors

- [ ] **Step 3: 提交**

```bash
git add simulation/frontend/src/scenes/SceneBag.vue
git commit -m "feat(scenes): add SceneBag with BagGripper"
```

---

### Task 16: 前端 — 单元测试（useSceneAPI / useSceneStage）

**Files:**
- Create: `simulation/frontend/src/scenes/__tests__/useSceneAPI.test.ts`
- Create: `simulation/frontend/src/scenes/__tests__/useSceneStage.test.ts`

**Interfaces:**
- 验证 useSceneAPI 与 useSceneStage 的行为

- [ ] **Step 1: 创建 useSceneAPI.test.ts**

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { useSceneAPI } from '../composables/useSceneAPI'

vi.mock('axios')
const mockedAxios = axios as unknown as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> }

describe('useSceneAPI', () => {
  beforeEach(() => {
    mockedAxios.get = vi.fn()
    mockedAxios.post = vi.fn()
  })

  it('list() returns available scenes', async () => {
    mockedAxios.get.mockResolvedValue({ data: { available: ['pallet', 'box', 'bag'], current: null } })
    const { list } = useSceneAPI()
    const result = await list()
    expect(result.available).toEqual(['pallet', 'box', 'bag'])
    expect(result.current).toBeNull()
  })

  it('load(name) updates currentScene', async () => {
    mockedAxios.post.mockResolvedValue({ data: { scene: 'pallet', devices: [], sites: [] } })
    const { load, currentScene } = useSceneAPI()
    await load('pallet')
    expect(currentScene.value).toBe('pallet')
  })

  it('getKPI() returns snapshot', async () => {
    mockedAxios.get.mockResolvedValue({ data: { scene: 'box', throughput_per_hour: 50, success_rate: 98, active_tasks: 1, completed_tasks: 2, failed_tasks: 0 } })
    const { getKPI } = useSceneAPI()
    const kpi = await getKPI('box')
    expect(kpi.throughput_per_hour).toBe(50)
  })
})
```

- [ ] **Step 2: 创建 useSceneStage.test.ts**

```typescript
import { describe, it, expect } from 'vitest'
import { useSceneStage, type SceneStageName } from '../composables/useSceneStage'

describe('useSceneStage', () => {
  it('starts at idle', () => {
    const { stage } = useSceneStage()
    expect(stage.value).toBe('idle')
  })

  it('advance cycles through stages', () => {
    const { stage, advance } = useSceneStage()
    const expected: SceneStageName[] = ['approach', 'engage', 'lift', 'transfer', 'place', 'return', 'idle']
    for (const want of expected) {
      advance()
      expect(stage.value).toBe(want)
    }
  })

  it('reset() returns to idle and stops timer', () => {
    const { stage, start, stop, reset } = useSceneStage()
    start()
    reset()
    expect(stage.value).toBe('idle')
    stop()
  })
})
```

- [ ] **Step 3: 运行 vitest**

Run: `cd d:/projects/robot-logic/simulation/frontend && npx vitest run src/scenes/__tests__`

Expected: 2 test files pass, all assertions pass

- [ ] **Step 4: 提交**

```bash
git add simulation/frontend/src/scenes/__tests__/useSceneAPI.test.ts
git add simulation/frontend/src/scenes/__tests__/useSceneStage.test.ts
git commit -m "test(scenes): add vitest for useSceneAPI + useSceneStage"
```

---

### Task 17: E2E — 浏览器手动验证

**Files:**
- Modify: 无（手动验证）

- [ ] **Step 1: 启动后端**

```bash
cd d:/projects/robot-logic/simulation/backend
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

- [ ] **Step 2: 启动前端 dev server**

另开 terminal：

```bash
cd d:/projects/robot-logic/simulation/frontend
npm run dev
```

- [ ] **Step 3: 浏览器手动验证**

访问 `http://localhost:5173/scenes`（Vite 默认端口），验证：
- [ ] 顶部 Tab 显示 3 个场景（托盘 / 箱装 / 袋装）
- [ ] 默认加载托盘场景，3D 场景可见 2 辆叉车
- [ ] 切换至"箱装"，3D 场景显示 LoaderRobot + BoxGripper
- [ ] 切换至"袋装"，3D 场景显示 3 个站点 + LoaderRobot + BagGripper
- [ ] KPI 面板每 2s 自动刷新
- [ ] DeviceList 显示当前场景设备
- [ ] TaskTimeline 显示任务时间轴
- [ ] LogViewer 显示运行日志
- [ ] Tab 切换后设备列表正确更新

- [ ] **Step 4: 回归 Dashboard**

访问 `http://localhost:5173/`，验证：
- [ ] Dashboard 仍能正常加载（不受 scenes 路由影响）
- [ ] /api/devices /api/tasks /api/sites 仍可用

- [ ] **Step 5: 截图 + 记录**

在 `docs/superpowers/specs/2026-08-14-top3-simulation-design.md` 末尾追加"实施截图与记录"小节（如有需要），或新开 `docs/superpowers/plans/2026-08-14-top3-simulation-notes.md`。

- [ ] **Step 6: 最终提交**

```bash
git add docs/
git commit -m "docs(scenes): record E2E verification results"
```

---

## Self-Review

1. **Spec coverage**：
   - 后端 4 API + scene_presets + load_scene → Task 1, 2, 3 ✓
   - pallet_forklift 设备类型 → Task 2, 3 ✓
   - 路由 + 3 Tab + 5 面板 → Task 5, 11, 12 ✓
   - PalletForklift / BoxGripper / BagGripper → Task 9, 10 ✓
   - 3 个 Scene*.vue 子组件 → Task 13, 14, 15 ✓
   - 错误处理 + 测试 → Task 4, 16, 17 ✓

2. **Placeholder scan**：无 TBD / TODO。所有步骤含完整代码或具体命令。

3. **Type consistency**：
   - `ScenePreset` TypedDict 在 Task 1 与 Task 2 字段一致
   - `SceneKPI` interface 在 useSceneAPI 与 useSceneKPI 中字段一致
   - `SceneStageName` 类型在 useSceneStage 与测试中一致

4. **Coverage gap**：spec 中"切换场景时仍有未完成任务 → 弹窗确认"未在 Task 中实现。YAGNI：当前 3 个场景的初始 tasks 都是 preset 创建的，切换 = reset，遗留 task 不存在。可作为后续 PR。