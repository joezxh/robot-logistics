# Task 1 Brief — scene_presets.py

## Project Context

工程 `d:\projects\robot-logic\` 是物流装卸机器人系统。当前任务是为文档 `docs/装卸场景与机器人适配选型.md` 第 3.7 节选出的 **Top 3 装卸场景**（托盘 / 箱装 / 袋装）实现完整仿真模块。本 Task 是仿真模块的 **数据层基石** —— 后续 Task 2 的 `Runtime.load_scene()` 会读取本文件。

## Files

- **Create**: `d:\projects\robot-logic\simulation\backend\services\scene_presets.py`

## Requirements（verbatim from plan）

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

## Acceptance Steps

1. **Step 1**: 创建上述文件（verbatim 写入）。
2. **Step 2**: 验证 Python 可解析：

```bash
cd "d:/projects/robot-logic/simulation/backend" && python -c "from backend.services.scene_presets import SCENE_PRESETS; print(list(SCENE_PRESETS.keys()))"
```

期望输出：`['pallet', 'box', 'bag']`

3. **Step 3**: 提交 commit：

```bash
cd "d:/projects/robot-logic"
git add simulation/backend/services/scene_presets.py
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add scene_presets data module for Top 3 loading scenes"
```

## Self-Review Checklist

- [ ] 文件路径正确：`simulation/backend/services/scene_presets.py`（不是 `simulation/backend/services/scene_preset.py`）
- [ ] 包含 docstring + `from __future__ import annotations`
- [ ] 5 个 TypedDict：`SiteSpec` / `DeviceSpec` / `TaskSpec` / `KPIDefinition` / `ScenePreset`
- [ ] 3 个常量：`PALLET_SCENE` / `BOX_SCENE` / `BAG_SCENE`
- [ ] 字典 `SCENE_PRESETS` 含全部 3 个场景
- [ ] 辅助函数 `list_scene_names()` / `get_scene(name)`
- [ ] `get_scene` 对未知名抛 `KeyError`
- [ ] Pallet 场景含 `pallet_forklift` 设备类型
- [ ] Python 解析无错，输出 3 个场景名

## Global Constraints (binding)

- 后端风格：Python 3.11+ / TypedDict 模式 / docstring 在文件顶部
- 严禁依赖 FastAPI / Pydantic（保持 framework-free）
- 中文 label / description 使用全角标点
- 仅 commit 这一个文件（不要顺手改其他文件）

## Report Contract

将完整报告写入 `d:\projects\robot-logic\.superpowers\sdd\task-1-report.md`，内容包含：
1. 状态：DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
2. commit hash（7 位）
3. Step 2 验证命令的实际输出
4. 自检清单的勾选状态
5. concerns（如有）

返回内容仅含：状态 + commit hash（7 位）+ 一行测试结果 + concerns。
