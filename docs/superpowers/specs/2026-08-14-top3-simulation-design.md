# Top 3 装卸场景仿真模块设计

> 为装卸场景与机器人适配选型文档（`docs/装卸场景与机器人适配选型.md` 第 3.7 节）所选的最容易实现 Top 3 场景，提供仿真模块的完整设计方案。
>
> 立项依据：见 `docs/装卸场景与机器人适配选型.md` 第 3.7.3 节"完整 18 场景易实现性排名表"。

---

## 0. 阅读指南

- **第 1 章**：背景与目标
- **第 2 章**：总体架构
- **第 3 章**：后端设计（场景预设、新设备类型、新 API）
- **第 4 章**：前端设计（路由、组件、面板）
- **第 5 章**：3 个场景详情（设备模型 + 任务流 + KPI）
- **第 6 章**：错误处理 + 测试 + 边界
- **第 7 章**：实施步骤与验收

---

## 1. 背景与目标

### 1.1 背景

文档 `docs/装卸场景与机器人适配选型.md` 第 3.7 节通过"方案成熟度 / 技术风险 / 改造成本 / 集成复杂度 / 法规障碍"5 个维度评估 18 个装卸场景，得出最容易实现的 Top 3：

| 排名 | 场景 | 推荐机器人本体 | 综合分 |
|:---:|------|--------------|:---:|
| 🥇 #1 | **2.2.7 托盘单元（欧/美/田/川）** | D 复合 + C 叉型 | 9.5/10 |
| 🥈 #2 | **2.2.2 箱装（瓦楞/塑料箱）** | D 复合 + B 夹爪 | 9.2/10 |
| 🥉 #3 | **2.2.1 袋装（编织/牛皮袋 ≤50kg）** | D 复合 + B 夹爪（防滑齿） | 8.5/10 |

### 1.2 目标

在当前工程基础上实现一个**仿真模块**，在 `/scenes` 顶级路由下以 3 个 Tab 形式切换并展示上述 Top 3 场景，每个场景包含：
- 独立的 Three.js 3D 场景 + 程序生成的设备模型
- 设备列表 / KPI / 任务时间轴 / 运行日志 5 个面板
- 复用现有 FastAPI backend runtime + 任务调度 + 设备系统

### 1.3 非目标

- 不实现真实物理引擎（Box2D/Rapier 等），货物位置由前端/后端按时间轴驱动。
- 不接入 VLA 模型，纯几何 + 状态机仿真。
- 不支持 Top 3 以外的场景（其他场景可作为后续 spec）。

---

## 2. 总体架构

### 2.1 架构图

```
┌──────────────────────────────────────────────────────────┐
│              /scenes 顶级路由（Vue 3 + Vue Router）       │
│   ┌──────────┬──────────┬──────────┐                    │
│   │ Pallet   │ Box      │ Bag      │   ← Tab 切换        │
│   │ 托盘     │ 箱装     │ 袋装     │                    │
│   └────┬─────┴────┬─────┴────┬─────┘                    │
│        │ ScenePallet.vue / SceneBox.vue / SceneBag.vue   │
│        │   ├ Three.js 场景 + 设备模型                    │
│        │   ├ DeviceList 面板                             │
│        │   ├ KPI 面板（吞吐、成功率、节拍）              │
│        │   ├ TaskTimeline（任务时间轴）                  │
│        │   └ LogViewer（运行日志）                       │
└───────│──────────────────────────────────────────────────┘
        │ POST /api/scenes/load/{name}
        ▼
┌──────────────────────────────────────────────────────────┐
│         backend/services/runtime.py（扩展）              │
│   新增:                                                 │
│     - scene_presets.py：3 个场景预设数据                 │
│     - load_scene(name)：reset + apply preset            │
│     - 4 个 API endpoint（见 §3.2）                       │
│   新增 device_type: pallet_forklift                     │
│   复用: loading_robot（箱装/袋装场景共用）              │
└───────│──────────────────────────────────────────────────┘
        │
        ▼ 现有 runtime tick(0.5s) 驱动设备移动
   现有 TaskScheduler / SiteManager / DeviceManager
```

### 2.2 工程复用清单

| 模块 | 用途 | 改动 |
|------|------|------|
| `backend/algorithm/simulator/device_manager.py` | 设备实例化 | **修改**：注册 `pallet_forklift` 类型设备 |
| `backend/services/runtime.py` | 运行时 | **修改**：新增 `load_scene()` 方法 |
| `backend/algorithm/scheduler/scheduler.py` | 任务调度 | **不改动**（沿用） |
| `backend/services/motion_commander.py` | 运动指令 | **不改动** |
| `backend/services/alerts.py` | 告警 | **不改动** |
| `backend/algorithm/simulator/site_manager.py` | 站点管理 | **不改动**（仅被场景预设调用） |
| `backend/main.py` | FastAPI 入口 | **修改**：注册 4 个 scenes API |
| `simulation/frontend/src/three/RobotArm.ts` | 机械臂 3D | **复用**（不改动） |
| `simulation/frontend/src/three/LoaderRobot.ts` | 双臂 AGV 3D | **复用**（不改动） |
| `simulation/frontend/src/dashboard/Kpi.vue` | KPI 面板 | **复用** |
| `simulation/frontend/src/dashboard/DeviceStatus.vue` | 设备面板 | **复用** |
| `simulation/frontend/src/dashboard/TaskTimeline.vue` | 时间轴 | **复用** |
| `simulation/frontend/src/panel/LogViewer.vue` | 日志 | **复用** |
| `simulation/frontend/src/three/WarehouseScene.vue` | 现有场景 | **不改动**（Dashboard 仍用旧版） |

---

## 3. 后端设计

### 3.1 文件结构

```
simulation/backend/
├── services/
│   ├── scene_presets.py     ← 新建：场景预设数据
│   └── runtime.py           ← 修改：新增 load_scene
├── algorithm/
│   └── simulator/
│       └── device_manager.py ← 修改：注册 pallet_forklift
├── tests/
│   ├── test_scene_presets.py ← 新建
│   └── test_scenes_api.py    ← 新建
└── main.py                  ← 修改：注册 scenes API 路由
```

### 3.2 API 设计

| API | 方法 | 请求 | 响应 | 说明 |
|-----|------|------|------|------|
| `/api/scenes` | GET | — | `{ "available": ["pallet","box","bag"], "current": "pallet" }` | 列出可用场景 + 当前激活 |
| `/api/scenes/load/{name}` | POST | — | `{ "scene": "pallet", "devices": [...], "sites": [...] }` | 重置 runtime + 应用预设 |
| `/api/scenes/current` | GET | — | `{ "name": "pallet", "kpi_definitions": [...] }` | 当前场景元数据 |
| `/api/scenes/{name}/kpi` | GET | — | `{ "throughput_per_hour": 38, "success_rate": 97.4, ... }` | 场景专属 KPI |

### 3.3 scene_presets.py 数据结构

```python
from typing import TypedDict

class ScenePreset(TypedDict):
    name: str               # "pallet" | "box" | "bag"
    label: str              # 中文标签
    description: str        # 场景说明
    sites: list[dict]       # SiteManager 注册数据
    devices: list[dict]     # DeviceManager 注册数据（含 device_type）
    tasks: list[dict]       # 初始任务（type/description/priority/device_id）
    kpi_definitions: list[dict]  # KPI 指标定义（label/key/unit/target）

SCENE_PRESETS: dict[str, ScenePreset] = {
    "pallet": { ... },
    "box":    { ... },
    "bag":    { ... },
}
```

### 3.4 pallet_forklift 设备类型扩展

**device_manager.py 改动**：

```python
# 注册 pallet_forklift 设备（场景预设中加载）
"forklift-01": Device(
    device_id="forklift-01",
    device_type="pallet_forklift",
    name="托盘叉车 1",
    position=[-6.0, 0.0, 4.0],
    speed=0.6,
),
```

**main.py DeviceCreateRequest 校验扩展**：

```python
class DeviceCreateRequest(BaseModel):
    device_type: str = Field(
        ...,
        pattern="^(container_robot|loading_robot|agv|stacker|pallet_forklift)$"
    )
```

### 3.5 runtime.load_scene() 方法

```python
def load_scene(self, name: str) -> dict[str, Any]:
    """重置 runtime 并应用指定场景预设。

    步骤：
      1. 校验 name 在 SCENE_PRESETS 中。
      2. 调用 self.reset()：清空 devices/sites/tasks/logs。
      3. 重新实例化 DeviceManager / SiteManager 并应用 preset。
      4. 创建预设 tasks。
      5. 记录当前 scene。
      6. 返回 devices/sites 列表。
    """
```

`reset()` 方法需要新增（当前没有），行为：
- `self.devices = DeviceManager()` 重置为空白（不带任何设备）
- `self.sites = SiteManager()` 重置
- `self.tasks.clear()`
- `self.logs.clear()`

DeviceManager 需要扩展：构造函数支持传入 `seed_devices: list[dict] | None = None`，为空时不预置任何设备，让场景预设显式注册。

---

## 4. 前端设计

### 4.1 文件结构

```
simulation/frontend/src/
├── router/
│   └── index.ts                   ← 新建：Vue Router 配置（含 /scenes）
├── scenes/
│   ├── ScenesPage.vue             ← 新建：顶级路由页面（含 Tab）
│   ├── SceneStage.vue             ← 新建：5 面板通用框架
│   ├── ScenePallet.vue            ← 新建：托盘场景子组件
│   ├── SceneBox.vue               ← 新建：箱装场景子组件
│   ├── SceneBag.vue               ← 新建：袋装场景子组件
│   ├── three/
│   │   ├── PalletForklift.ts      ← 新建：托盘叉车 Three.js 类
│   │   ├── BoxGripper.ts          ← 新建：箱装夹爪末端（扩展 LoaderRobot）
│   │   └── BagGripper.ts          ← 新建：袋装夹爪末端（扩展 LoaderRobot）
│   └── composables/
│       ├── useSceneAPI.ts         ← 新建：后端 scene API 封装
│       ├── useSceneStage.ts       ← 新建：阶段状态机 composable
│       └── useSceneKPI.ts         ← 新建：KPI composable
├── App.vue                        ← 修改：增加 /scenes 入口（侧边导航）
└── main.ts                        ← 修改：注册 router
```

### 4.2 路由

```typescript
// simulation/frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import ScenesPage from '@/scenes/ScenesPage.vue'

const routes = [
  { path: '/', name: 'dashboard', component: () => import('@/App.vue') },
  { path: '/scenes', name: 'scenes', component: ScenesPage },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
```

**App.vue 入口**：在 topbar 增加 "🚛 场景仿真" 链接（`<router-link to="/scenes">`）。

### 4.3 ScenesPage.vue 布局

```
┌──────────────────────────────────────────────────────────┐
│  [顶栏] 机器人智能仓储物流系统 / 🚛 场景仿真            │
├──────────────────────────────────────────────────────────┤
│  Tabs:  [📦 托盘]  [📦 箱装]  [📦 袋装]                  │
│                                                          │
│         ┌─────────────────────────────────────────────┐ │
│         │            SceneStage.vue                   │ │
│         │   ┌───────────────────┬──────────────────┐  │ │
│         │   │  Three.js 场景     │  DeviceList      │  │ │
│         │   │  (主视觉)          │                  │  │ │
│         │   │                    ├──────────────────┤  │ │
│         │   │                    │  KPI             │  │ │
│         │   └────────────────────┴──────────────────┘  │ │
│         │   ┌─────────────────────────────────────────┐ │ │
│         │   │  TaskTimeline                          │ │ │
│         │   └─────────────────────────────────────────┘ │ │
│         │   ┌─────────────────────────────────────────┐ │ │
│         │   │  LogViewer                             │ │ │
│         │   └─────────────────────────────────────────┘ │ │
│         └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

### 4.4 SceneStage.vue 通用框架

**Props**：
- `sceneName: 'pallet' | 'box' | 'bag'`（来自 Tab 选中）

**内部状态**：
- `currentStage: SceneStageName` —— 当前阶段（idle/approach/engage/lift/transfer/place/return）
- `paused: boolean` —— 暂停状态
- `speed: number` —— 0.25 ~ 3 倍速

**布局组件**：
- 左侧 70%：动态加载 `ScenePallet.vue` / `SceneBox.vue` / `SceneBag.vue`
- 右上 30%：DeviceList（来自 `dashboard/DeviceStatus.vue`，传 devices）
- 右下 30%：KPI 卡片（4 张：吞吐、成功率、节拍、设备数）
- 下中：TaskTimeline（`dashboard/TaskTimeline.vue`）
- 下底：LogViewer（`panel/LogViewer.vue`）

**数据流**：
- 设备列表：每 1s 拉取 `GET /api/devices`
- 任务时间轴：每 1s 拉取 `GET /api/tasks`
- 日志：SSE 订阅 `/api/logs/stream`
- KPI：每 2s 拉取 `GET /api/scenes/{name}/kpi`
- 场景元数据：`GET /api/scenes/current`（一次性）

### 4.5 useSceneAPI.ts

```typescript
export function useSceneAPI() {
  const currentScene = ref<string>('')

  async function list() {
    return (await axios.get('/api/scenes')).data
  }

  async function load(name: string) {
    const res = await axios.post(`/api/scenes/load/${name}`)
    currentScene.value = name
    return res.data
  }

  async function getCurrent() {
    return (await axios.get('/api/scenes/current')).data
  }

  async function getKPI(name: string) {
    return (await axios.get(`/api/scenes/${name}/kpi`)).data
  }

  return { currentScene, list, load, getCurrent, getKPI }
}
```

### 4.6 useSceneStage.ts 阶段状态机

7 个 stage：idle → approach → engage → lift → transfer → place → return

```typescript
export type SceneStageName =
  | 'idle' | 'approach' | 'engage' | 'lift' | 'transfer' | 'place' | 'return'

export function useSceneStage() {
  const stage = ref<SceneStageName>('idle')

  const STAGE_DURATION_MS: Record<SceneStageName, number> = {
    idle: 500,
    approach: 2000,
    engage: 1500,
    lift: 800,
    transfer: 2500,
    place: 1500,
    return: 2000,
  }

  function advance() {
    const order: SceneStageName[] = [
      'idle', 'approach', 'engage', 'lift', 'transfer', 'place', 'return',
    ]
    const idx = order.indexOf(stage.value)
    stage.value = order[(idx + 1) % order.length]
  }

  let timer: number | undefined
  function start() {
    timer = window.setInterval(advance, STAGE_DURATION_MS[stage.value])
  }
  function stop() {
    if (timer) clearInterval(timer)
  }

  return { stage, advance, start, stop }
}
```

### 4.7 PalletForklift.ts 程序生成

**结构**：
- `body: BoxGeometry(1.6, 0.6, 1.0)` —— 主车体（深灰色）
- `cabin: BoxGeometry(0.6, 0.8, 1.0)` —— 驾驶舱（顶部凸起）
- `wheels: 4 × CylinderGeometry(0.2, 0.2, 0.2)` —— 4 轮
- `mast: BoxGeometry(0.1, 2.0, 0.1) × 2` —— 立柱（可升降）
- `fork: BoxGeometry(0.1, 0.05, 1.2) × 2` —— 货叉（可升降 + 伸出）
- `palletLoad: Group` —— 当前装载的托盘货物（按需显示/隐藏）

**可动参数**：
- `mastHeight: 0~1.8` —— 立柱 + 货叉垂直位移
- `forkExtension: 0~0.3` —— 货叉水平伸出
- `hasLoad: bool` —— 是否装载货物

**方法**：
- `setMastHeight(h)` —— 设置升降高度
- `setExtension(e)` —— 设置伸出
- `setLoad(pallet)` —— 显示/隐藏货物
- `update(dt)` —— 平滑过渡动画

---

## 5. 3 个场景详情

### 5.1 场景 1：托盘（pallet）

**设备组合**
| 设备 ID | device_type | 数量 | 角色 |
|---------|-------------|:---:|------|
| forklift-01 | pallet_forklift | 2 | 叉车（双车交替） |
| agv-01 | agv | 1 | 托盘转运 |

**站点配置**
| 站点 ID | 类型 | 尺寸（m） | 颜色 | 用途 |
|---------|------|----------|------|------|
| dock-01 | dock | 6×4 | #5eb0ff | 集装箱月台（叉车取货） |
| warehouse-01 | warehouse | 4×3 | #58c47e | 仓库 1（托盘入库） |
| warehouse-02 | warehouse | 4×3 | #58c47e | 仓库 2（备用） |

**任务流**
1. forklift-01 从 dock-01 取托盘（fork 伸出 → 升起 → 收回）
2. 行驶至 agv-01 顶面（route: dock → [0,0,0] → agv）
3. 放下托盘（fork 下降 → 伸出 → 收回）
4. forklift-02 同流程（双车交替演示）
5. agv-01 接收托盘后转运至 warehouse-01

**关键 KPI**
| 指标 | 目标 |
|------|------|
| 单托盘节拍 | ≤ 12s |
| 叉车插入成功率 | ≥ 98% |
| AGV 对接精度 | ±5mm |
| 吞吐量 | ≥ 5 托盘/小时 |

### 5.2 场景 2：箱装（box）

**设备组合**
| 设备 ID | device_type | 数量 | 角色 |
|---------|-------------|:---:|------|
| loader-01 | loading_robot | 1 | 双臂箱装抓取机器人 |
| agv-01 | agv | 2 | 箱装转运 |
| stacker-01 | stacker | 1 | 立体库堆垛机 |

**站点配置**
| 站点 ID | 类型 | 尺寸 | 颜色 | 用途 |
|---------|------|------|------|------|
| dock-01 | dock | 6×4 | #5eb0ff | 集装箱月台 |
| warehouse-01 | warehouse | 5×4 | #58c47e | 立体库入口 |

**任务流**
1. loader-01 从 dock-01 抓取箱装（双末端快换为 box-gripper）
2. 放入传送带起点（视觉演示传送带）
3. agv-01 / agv-02 在传送带终点接力（queue 调度）
4. 运至 stacker-01 入口
5. stacker-01 入库（视觉演示）

**关键 KPI**
| 指标 | 目标 |
|------|------|
| 单件节拍 | ≤ 5s |
| 抓取成功率 | ≥ 99.5% |
| 压溃率 | 0 |
| 吞吐量 | ≥ 12 件/min |

### 5.3 场景 3：袋装（bag）

**设备组合**
| 设备 ID | device_type | 数量 | 角色 |
|---------|-------------|:---:|------|
| loader-01 | loading_robot | 1 | 双臂袋装抓取机器人 |
| agv-01 | agv | 1 | 袋装转运 |
| stacker-01 | stacker | 1 | 立体库堆垛机 |

**站点配置**
| 站点 ID | 类型 | 尺寸 | 颜色 | 用途 |
|---------|------|------|------|------|
| dock-01 | dock | 6×4 | #5eb0ff | 集装箱月台 |
| warehouse-01 | warehouse | 4×3 | #58c47e | 立体库 |
| pallet-area | warehouse | 3×3 | #c4a76c | 吨袋暂存区 |

**任务流**
1. loader-01 从 dock-01 抓取袋装（末端为 wide-gripper + 防滑纹）
2. 视觉检测袋装满度（演示）
3. 放入 stacker-01 入库位（防破袋力控）
4. stacker-01 入库
5. loader-01 返回 dock

**关键 KPI**
| 指标 | 目标 |
|------|------|
| 抓取成功率 | ≥ 98% |
| 破袋率 | ≤ 0.5% |
| 传送带对接精度 | ±30mm |
| 吞吐量 | ≥ 8 袋/min |

---

## 6. 错误处理 + 测试 + 边界

### 6.1 错误处理

| 层 | 错误 | 处理 |
|----|------|------|
| 后端 | 未知 scene name | HTTPException 404 "unknown scene: {name}" |
| 后端 | scene preset 数据校验失败 | HTTPException 422 |
| 后端 | runtime.reset() 失败 | 日志 + 返回 500 |
| 前端 | 后端不可达 | axios error → 顶部 toast"无法连接后端服务" |
| 前端 | Three.js 初始化失败 | 容器 fallback 渲染"3D 渲染不可用，请使用现代浏览器" |
| 前端 | 切换场景时仍有未完成任务 | 弹窗确认"将丢失当前进度" |
| 设备 | pallet_forklift 路径不可达 | runtime 标记 task failed + 触发 alert.warning |
| 设备 | loading_robot 抓取失败（演示用 5% 概率） | 日志记录 + alert.warning |

### 6.2 测试

| 层 | 类型 | 文件 | 覆盖 |
|----|------|------|------|
| 后端 | unit | `tests/test_scene_presets.py` | 3 个 preset 数据完整性（sites/devices/tasks 字段齐全） |
| 后端 | unit | `tests/test_runtime_load_scene.py` | load_scene 重置 + 应用 + 异常分支 |
| 后端 | API | `tests/test_scenes_api.py` | 4 个 endpoint 正常 + 异常分支 |
| 后端 | 回归 | `tests/test_api.py` | 现有 API 不被破坏 |
| 前端 | unit | `src/scenes/__tests__/useSceneAPI.test.ts` | API composable 4 个方法 |
| 前端 | unit | `src/scenes/__tests__/useSceneStage.test.ts` | 状态机 7 阶段切换 |
| E2E | 手动 | — | 浏览器验证 3 场景：3D 渲染、Tab 切换、KPI 同步、日志流 |

### 6.3 关键边界

1. **场景互斥**：同一时刻只允许一个 scene active，`load_scene` 必须先 `reset`。
2. **设备类型扩展**：必须在 `DeviceCreateRequest.device_type` 枚举中加 `pallet_forklift`。
3. **任务类型扩展**：3 个新任务类型 `pallet_fork` / `box_unload` / `bag_unload`，任务处理逻辑沿用现有 `dock_loading` 风格（route-based 移动）。
4. **不影响 Dashboard**：在加载场景时不清空 dashboard 数据；dashboard 是独立视图，独立 Three.js 实例。
5. **SSE 自动重连**：前端 SSE 连接断开时自动重连（现有 dashboard 已实现，沿用）。

### 6.4 性能预算

- 3 个 Three.js 场景，单次只激活一个，切换时间 < 1s
- 后端 runtime tick 0.5s/帧，前端 SSE 30Hz（关节）/ 10Hz（检测）
- 内存：每个 Three.js 场景 ~10MB
- KPI 轮询：每 2s 一次

---

## 7. 实施步骤与验收

### 7.1 实施步骤

| 步骤 | 内容 | 工时估计 |
|------|------|----------|
| 1 | 后端 `scene_presets.py` 数据 + `runtime.load_scene()` | 0.5d |
| 2 | 后端 4 个 API + 测试 | 0.5d |
| 3 | 前端 Vue Router + `/scenes` 入口 | 0.25d |
| 4 | 前端 `ScenesPage.vue` + `SceneStage.vue` + 5 面板 | 0.5d |
| 5 | 前端 3 个 `Scene*.vue` 子组件（不含设备模型） | 0.5d |
| 6 | 前端 `PalletForklift.ts` + 夹爪扩展 | 0.5d |
| 7 | 前端 `useSceneAPI.ts` + `useSceneStage.ts` composable | 0.25d |
| 8 | E2E 测试 + 浏览器手动验证 | 0.5d |
| **总计** | — | **~3.5d** |

### 7.2 验收标准

**功能验收**
- [ ] `/scenes` 路由可访问
- [ ] 3 个 Tab 均可切换，切换后 3D 场景正确显示对应设备
- [ ] 后端 `GET /api/scenes` 返回 3 个场景 + current
- [ ] 后端 `POST /api/scenes/load/{name}` 正确重置 + 应用
- [ ] 设备列表、KPI、时间轴、日志 5 面板数据正确同步
- [ ] 后端测试 100% 通过
- [ ] 前端类型检查通过（`vue-tsc`）
- [ ] Dashboard 现有功能未被破坏

**性能验收**
- [ ] Tab 切换时间 < 1s
- [ ] Three.js 渲染 ≥ 30fps
- [ ] SSE 延迟 < 100ms

**质量验收**
- [ ] 代码符合现有风格（Python + Vue 3）
- [ ] 新增文件均含 docstring/comment
- [ ] 测试覆盖率：后端 preset/runtime 100%

---

## 附录 A：与其他文档的引用关系

- **场景评估依据**：`docs/装卸场景与机器人适配选型.md` 第 3.7 节
- **现有架构**：`docs/ARCHITECTURE.md`、`docs/OPERATIONS-ZH.md`
- **算法细节**：`docs/algorithm/02-motion-planning.md`、`docs/algorithm/04-task-scheduling.md`
- **DUAL ARM 设计**：`docs/superpowers/specs/2026-08-09-loading-robot-dual-arm-agv-design.md`

## 附录 B：版本日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0 | 2026-08-14 | 初版：Top 3 装卸场景仿真模块设计（pallet/box/bag） |
