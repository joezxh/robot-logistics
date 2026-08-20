# 仓库 3D 可视化迁移设计文档

> **项目**: Robot Logic Simulation  
> **日期**: 2026-08-20  
> **状态**: 已批准

## 1. 概述

### 1.1 目标
将 `warehouse_theatre_3d` 的完整 3D 仓库可视化能力迁移到 `robot-logic/simulation` 项目中，作为仿真运行的基础框架。迁移后，simulation 将拥有一个功能完整的 3D 仓库场景，同时保持现有的机器人控制、任务管理、API 交互等能力。

### 1.2 范围

| 模块 | 迁移内容 |
|------|----------|
| **前端 3D 引擎** | `ThreeEngine` 类、区域渲染、设施模型、相机控制 |
| **前端 UI 组件** | 侧边栏、详情面板、编辑器、向导、物流面板 |
| **前端交互逻辑** | AGV 导航、路径规划、动画系统、事件处理 |
| **后端 API** | 仓库管理、布局蓝图、月台物流、AGV 网格 |
| **数据模型** | 仓库层级、区域配置、布局蓝图、任务数据 |

### 1.3 迁移来源
- **前端**: `warehouse_theatre_3d/warehouse_theatre_3d/public/js/wt3d-vue.js` (~4800 行)
- **后端**: `warehouse_theatre_3d/warehouse_theatre_3d/api/` (api.py, layout.py, dock.py, agv.py)

### 1.4 目标位置
- **前端**: `simulation/frontend/src/warehouse/`
- **后端**: `simulation/backend/routers/warehouse/`, `simulation/backend/models/warehouse/`

---

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  Robot Control  │  │  Warehouse 3D    │  │   KPI & Stats   │ │
│  │  Dashboard      │  │  Visualization  │  │   Dashboard     │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                      │                     │          │
│           └──────────────────────┼─────────────────────┘          │
│                                  │                                │
│                    ┌─────────────┴─────────────┐                │
│                    │    Shared Store (Pinia)   │                │
│                    └─────────────┬─────────────┘                │
└──────────────────────────────────┼───────────────────────────────┘
                                   │ HTTP/SSE
┌──────────────────────────────────┼───────────────────────────────┐
│                     Backend (FastAPI)                             │
├─────────────────────────────────┼───────────────────────────────┤
│  ┌─────────────────────────────┴──────────────────────────┐   │
│  │                  RCS Env Integration Layer                │   │
│  └─────────────────────────────┬──────────────────────────┘   │
│                                  │                               │
│  ┌──────────────┐  ┌────────────┴───────────┐  ┌──────────┐ │
│  │ RCS Core     │  │ Warehouse Viz API        │  │ Task API │ │
│  │ (Robot Ctrl) │  │ /api/warehouse/*       │  │ /api/*   │ │
│  └──────────────┘  └────────────────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 前端模块结构

```
simulation/frontend/src/warehouse/
├── engine/                      # Three.js 引擎核心
│   ├── ThreeEngine.ts         # 渲染引擎（从 wt3d-vue.js 提取）
│   ├── CameraController.ts    # 相机控制
│   ├── MouseHandler.ts        # 鼠标交互
│   ├── ZoneRenderer.ts       # 区域渲染基类
│   ├── zones/                # 区域渲染器
│   │   ├── RackZone.ts       # 货架区 (buildRackZone)
│   │   ├── AsrsZone.ts      # 立库 (buildAsrsZone)
│   │   ├── HighRackZone.ts  # 高位货架 (buildHighRackZone)
│   │   ├── MezzanineZone.ts # 夹层 (buildMezzanineZone)
│   │   ├── TempZone.ts      # 临时存储区
│   │   ├── TempBaggedZone.ts # 袋装暂存区
│   │   └── ReturnsZone.ts   # 退货区
│   ├── facilities/            # 设施模型
│   │   ├── Charger.ts       # 充电桩
│   │   ├── Sorting.ts       # 分拣台
│   │   ├── Packing.ts       # 打包区
│   │   ├── QC.ts            # 质检区
│   │   └── Entrance.ts      # 大门
│   ├── docks/               # 月台渲染
│   │   └── DockRenderer.ts  # 月台 + 卷帘门
│   ├── vehicles/             # 车辆渲染
│   │   └── VehicleRenderer.ts # 卡车 + 货物
│   ├── shell/               # 布局蓝图渲染
│   │   ├── ShellRenderer.ts # 外墙、屋顶、地面
│   │   ├── MarkingRenderer.ts # 标线
│   │   └── WallRenderer.ts   # 墙壁
│   └── buildScene.ts        # 场景构建入口
├── agv/                      # AGV 导航系统
│   ├── AGVGrid.ts          # 导航网格类
│   ├── PathPlanner.ts      # A* 路径规划
│   ├── ManhattanGrid.ts     # Manhattan 网格
│   └── AnimationSystem.ts  # 路径动画
├── components/               # Vue 3 组件
│   ├── WarehouseView.vue     # 主视图容器
│   ├── Sidebar.vue         # 仓库导航侧边栏
│   ├── TopBar.vue          # 顶栏（搜索、视图切换）
│   ├── BottomBar.vue       # 底栏（统计、图例）
│   ├── DetailPanel.vue    # 库位详情面板
│   ├── ItemModal.vue       # 物品详情模态框
│   ├── ConfigModal.vue     # 库位配置模态框
│   ├── FloorPlanEditor.vue # 布局编辑器
│   ├── AGVGridEditor.vue  # AGV 网格编辑器
│   ├── LogisticsSidebar.vue # 物流任务侧边栏
│   ├── LogisticsStats.vue   # 物流统计面板
│   └── SetupWizard.vue    # 设置向导
├── store/                   # Pinia 状态管理
│   ├── index.ts            # Store 入口
│   ├── warehouse.ts         # 仓库状态
│   └── ui.ts               # UI 状态
├── api/                     # API 客户端
│   ├── client.ts           # 基础 HTTP 客户端
│   ├── warehouse.ts        # 仓库 API
│   ├── layout.ts          # 布局 API
│   ├── logistics.ts        # 物流 API
│   └── agv.ts             # AGV API
├── composables/            # Vue Composables
│   ├── useWarehouse.ts     # 仓库操作
│   ├── useLogistics.ts     # 物流操作
│   └── useAGV.ts          # AGV 操作
├── i18n/                    # 国际化
│   ├── index.ts
│   ├── zh.ts
│   └── en.ts
├── types/                   # TypeScript 类型
│   ├── warehouse.ts        # 仓库类型
│   ├── zone.ts            # 区域类型
│   ├── logistics.ts        # 物流类型
│   └── agv.ts             # AGV 类型
└── utils/                   # 工具函数
    ├── geometry.ts        # 几何计算
    ├── colors.ts          # 颜色映射
    └── i18n.ts           # 翻译辅助
```

### 2.3 后端模块结构

```
simulation/backend/
├── routers/
│   └── warehouse/          # 仓库管理路由
│       ├── __init__.py
│       ├── slots.py        # 库位管理
│       ├── groups.py       # 仓库组
│       ├── layout.py       # 布局蓝图
│       ├── docks.py        # 月台管理
│       ├── logistics.py    # 物流任务
│       └── agv.py          # AGV 导航
├── models/
│   └── warehouse/           # Pydantic 数据模型
│       ├── __init__.py
│       ├── slot.py         # 库位模型
│       ├── zone.py         # 区域模型
│       ├── layout.py       # 布局蓝图模型
│       ├── dock.py         # 月台模型
│       ├── logistics.py    # 物流模型
│       └── agv.py          # AGV 模型
├── services/
│   └── warehouse/          # 业务逻辑服务
│       ├── __init__.py
│       ├── slot_service.py
│       ├── layout_service.py
│       ├── logistics_service.py
│       └── agv_service.py
├── data/                   # 数据存储（JSON 文件）
│   └── warehouse/
│       ├── slots.json
│       ├── layout/
│       └── agv/
└── main.py                # 扩展路由注册
```

---

## 3. 功能映射

### 3.1 3D 渲染功能

| warehouse_theatre_3d | simulation 迁移目标 | 说明 |
|---------------------|---------------------|------|
| `ThreeEngine` 类 | `engine/ThreeEngine.ts` | 核心渲染引擎 |
| `buildRackZone()` | `engine/zones/RackZone.ts` | 货架区渲染 |
| `buildAsrsZone()` | `engine/zones/AsrsZone.ts` | ASRS 立库渲染 |
| `buildHighRackZone()` | `engine/zones/HighRackZone.ts` | 高位货架渲染 |
| `buildMezzanineZone()` | `engine/zones/MezzanineZone.ts` | 夹层渲染 |
| `buildTempZone()` | `engine/zones/TempZone.ts` | 临时存储区渲染 |
| `buildTempBaggedZone()` | `engine/zones/TempBaggedZone.ts` | 袋装暂存区 |
| `buildReturnsZone()` | `engine/zones/ReturnsZone.ts` | 退货区渲染 |
| `buildFacilities()` | `engine/facilities/*.ts` | 设施模型（充电桩等） |
| `buildDocks()` | `engine/docks/DockRenderer.ts` | 月台 + 卷帘门 |
| `buildVehicles()` | `engine/vehicles/VehicleRenderer.ts` | 卡车 + 货物 |
| `buildShell()` | `engine/shell/ShellRenderer.ts` | 布局蓝图渲染 |
| 轨道视角 | 保留 | 扩展自动旋转 |
| 第一人称漫游 | 保留 | WASD 导航 |

### 3.2 交互功能

| 功能 | 迁移目标 | 说明 |
|------|----------|------|
| 鼠标悬停提示 | `Tooltip.vue` | 显示库位占用率 |
| 点击高亮 + 详情面板 | `DetailPanel.vue` | 侧边详情 |
| 双击查看物品详情 | `ItemModal.vue` | 物品列表 |
| 库位配置编辑 | `ConfigModal.vue` | 层数、容量配置 |
| 布局蓝图编辑器 | `FloorPlanEditor.vue` | 可视化编辑器 |
| 物流任务面板 | `LogisticsSidebar.vue` | 实时任务列表 |
| 物流统计 | `LogisticsStats.vue` | 历史统计 |
| AGV 网格编辑器 | `AGVGridEditor.vue` | 2D 网格绘制 |

### 3.3 后端 API 映射

| Frappe API | FastAPI 端点 | 方法 |
|------------|--------------|------|
| `api.get_warehouse_groups` | `/api/warehouse/groups` | GET |
| `api.get_slots` | `/api/warehouse/slots` | GET |
| `api.get_warehouse_detail` | `/api/warehouse/detail/{id}` | GET |
| `api.save_uom_capacity` | `/api/warehouse/slots/{id}/capacity` | PATCH |
| `layout.get_floor_full` | `/api/warehouse/layout/floor/{floor}` | GET |
| `layout.save_floor_shell` | `/api/warehouse/layout/shell/{floor}` | PUT |
| `dock.get_docks` | `/api/warehouse/docks` | GET |
| `dock.get_logistics_tasks` | `/api/warehouse/logistics/tasks` | GET |
| `dock.get_logistics_stats` | `/api/warehouse/logistics/stats` | GET |
| `agv.get_agv_grid` | `/api/warehouse/agv/grid/{group}` | GET |
| `agv.save_agv_grid` | `/api/warehouse/agv/grid/{group}` | PUT |

---

## 4. 数据模型设计

### 4.1 后端数据模型 (Pydantic)

```python
# models/warehouse/slot.py
class UOMCapacity(BaseModel):
    uom: str
    qty: float
    reserved: float
    cap: float

class ItemStock(BaseModel):
    code: str
    name: str
    uom: str
    group: str
    qty: float
    reserved: float
    rate: float
    stock_value: float

class SlotLevel(BaseModel):
    warehouse_id: str
    label: str
    uoms: list[UOMCapacity] = []
    items: list[ItemStock] = []

class Slot(BaseModel):
    warehouse_id: str
    label: str
    row: int
    col: int
    row_gap: float
    levels: list[SlotLevel]

# models/warehouse/layout.py
class Bounds(BaseModel):
    w: float
    d: float

class Wall(BaseModel):
    x0: float; z0: float; x1: float; z1: float; h: float
    dock_bumper: bool = False

class DockPlacement(BaseModel):
    ref: str; x: float; z: float; rot: float = 0

class FacilityPlacement(BaseModel):
    ref: str; kind: str; x: float; z: float; w: float; d: float

class Corridor(BaseModel):
    x0: float; z0: float; x1: float; z1: float
    main: bool = False

class ShellBlueprint(BaseModel):
    bounds: Bounds
    walls: list[Wall] = []
    docks: list[DockPlacement] = []
    facilities: list[FacilityPlacement] = []
    corridors: list[Corridor] = []

class FloorFull(BaseModel):
    shell: ShellBlueprint | None
    zones: list[Zone]
    facilities: list[Facility]
    docks: list[Dock]
```

### 4.2 前端状态模型 (TypeScript)

```typescript
// store/warehouse.ts
interface WarehouseState {
  // 视图状态
  isDark: boolean
  lang: 'zh' | 'en'
  curView: '3d' | '2d' | 'editor'
  
  // 仓库数据
  groups: WarehouseGroup[]
  curGroup: WarehouseGroup | null
  slots: Slot[]
  
  // 选中状态
  selectedKey: string | null
  detailPanelOpen: boolean
  detailData: SlotDetail | null
  itemModalOpen: boolean
  itemData: ItemDetail | null
  
  // 布局蓝图
  floorFull: FloorFull | null
  showWalls: boolean
  showMarkings: boolean
  
  // 月台与物流
  docks: Dock[]
  logisticsTasks: LogisticsTask[]
  logisticsStats: LogisticsStats
  
  // AGV
  agvGrid: AGVGrid | null
  agvOverlay: boolean
  agvTool: 'walk' | 'block' | 'main' | 'restricted'
  
  // 相机状态
  aisleMode: boolean
  aisleGaps: AisleGap[]
  
  // 编辑器状态
  floorPlanOpen: boolean
  agvEditorOpen: boolean
  configOpen: boolean
  
  // 加载状态
  loading: boolean
  setupComplete: boolean
}
```

---

## 5. API 设计

### 5.1 仓库管理 API

```
GET    /api/warehouse/groups
       Response: WarehouseGroup[]

GET    /api/warehouse/slots?group={id}
       Response: Slot[]

GET    /api/warehouse/slots/{warehouse_id}
       Response: Slot

GET    /api/warehouse/detail/{warehouse}
       Response: WarehouseDetail

PATCH  /api/warehouse/slots/{warehouse_id}
       Body: SlotUpdate
       Response: Slot

PATCH  /api/warehouse/slots/{warehouse_id}/capacity
       Body: { uom: string, capacity: float }
       Response: { ok: true }
```

### 5.2 布局蓝图 API

```
GET    /api/warehouse/layout/floor/{floor}
       Response: FloorFull

PUT    /api/warehouse/layout/shell/{floor}
       Body: ShellBlueprint
       Response: { ok: true }

POST   /api/warehouse/layout/export-dxf?floor={floor}
       Response: DXF file download

GET    /api/warehouse/layout/preview
       Response: { rows: FloorPlanRow[] }
```

### 5.3 月台与物流 API

```
GET    /api/warehouse/docks
       Response: Dock[]

GET    /api/warehouse/docks/{id}
       Response: DockDetail

GET    /api/warehouse/logistics/tasks?dock={}&status={}&date_range={}
       Response: LogisticsTask[]

GET    /api/warehouse/logistics/stats?dock={}&date_range={}
       Response: LogisticsStats
```

### 5.4 AGV 导航 API

```
GET    /api/warehouse/agv/grid/{group}
       Response: AGVGrid

PUT    /api/warehouse/agv/grid/{group}
       Body: AGVGrid
       Response: { ok: true }

POST   /api/warehouse/agv/grid/{group}/derive
       Response: AGVGrid

GET    /api/warehouse/agv/path?from={node}&to={node}
       Response: { path: Point[], cost: float }
```

---

## 6. 集成策略

### 6.1 与现有 simulation 前端集成

```vue
<!-- 新增: src/scenes/SceneWarehouse.vue -->
<template>
  <div class="warehouse-stage">
    <WarehouseView class="warehouse-3d" />
    <div class="control-panel">
      <DeviceStatus />
      <TaskQueue />
      <Kpi />
    </div>
  </div>
</template>
```

### 6.2 与 RCS 仿真集成

```typescript
// 机器人设备放置到仓库坐标
interface RobotPlacement {
  device_id: string
  position: [x: number, y: number, z: number]
  target_slot?: string  // 关联的库位
}

// API: 获取场景中的机器人位置
GET /api/warehouse/robot-placements
Response: RobotPlacement[]

// API: 更新机器人物理位置
PATCH /api/warehouse/robot-placements/{device_id}
Body: { position: [x, y, z], target_slot?: string }
```

### 6.3 与任务系统集成

```typescript
// 物流任务与库位关联
interface LogisticsTask {
  task_id: string
  task_type: 'inbound' | 'outbound' | 'transfer'
  source_dock: string
  target_slot: string
  items: TaskItem[]
  status: 'pending' | 'running' | 'completed'
}

// API: 触发任务动画
POST /api/warehouse/logistics/tasks/{task_id}/animate
Response: { path: Vector3[], duration: number }
```

---

## 7. 实现计划

### Phase 1: 核心 3D 引擎迁移
**预计工时**: 3-4 天

| 任务 | 说明 |
|------|------|
| 创建目录结构 | `src/warehouse/engine/` |
| 迁移 ThreeEngine | 渲染引擎核心类 |
| 迁移区域渲染器 | RackZone, AsrsZone, HighRackZone 等 |
| 迁移设施渲染器 | Charger, Sorting, Packing, QC 等 |
| 迁移月台和车辆 | DockRenderer, VehicleRenderer |
| 迁移相机控制 | 轨道视角 + 第一人称漫游 |

### Phase 2: AGV 导航系统
**预计工时**: 2-3 天

| 任务 | 说明 |
|------|------|
| 迁移 AGVGrid | 导航网格类 |
| 迁移 PathPlanner | A* 路径规划 |
| 迁移 AnimationSystem | 路径动画 |
| 迁移物流动画 | CatmullRom 曲线动画 |

### Phase 3: UI 组件迁移
**预计工时**: 3-4 天

| 任务 | 说明 |
|------|------|
| 创建 Pinia Store | 状态管理 |
| 迁移侧边栏 | Sidebar, TopBar, BottomBar |
| 迁移详情组件 | DetailPanel, ItemModal |
| 迁移编辑器 | FloorPlanEditor, ConfigModal |
| 迁移物流面板 | LogisticsSidebar, LogisticsStats |
| 迁移 AGV 编辑器 | AGVGridEditor |

### Phase 4: 后端 API 实现
**预计工时**: 3-4 天

| 任务 | 说明 |
|------|------|
| 创建数据模型 | Pydantic models |
| 实现仓库路由 | CRUD endpoints |
| 实现布局路由 | Shell blueprint |
| 实现物流路由 | Tasks, stats |
| 实现 AGV 路由 | Grid, path |

### Phase 5: 集成与测试
**预计工时**: 2-3 天

| 任务 | 说明 |
|------|------|
| 前端集成 | SceneWarehouse.vue |
| 后端集成 | main.py 路由注册 |
| RCS 集成 | 机器人位置映射 |
| E2E 测试 | 完整功能验证 |
| 性能优化 | 大规模场景优化 |

---

## 8. 关键决策

| 决策项 | 选择 | 理由 |
|--------|------|------|
| 渲染风格 | 保留 warehouse 原风格 | 确保视觉一致性 |
| 状态管理 | Pinia | TypeScript 友好，Vue 3 官方推荐 |
| API 风格 | FastAPI | 与 simulation 现有架构一致 |
| 坐标系 | 保持原坐标系 | 避免数据转换错误 |
| 启动方式 | 嵌入 simulation | 统一用户体验 |
| 数据存储 | JSON 文件 | 简化后端，无需数据库 |

---

## 9. 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 代码量巨大 (~4800 行) | 迁移周期长 | 分阶段交付，每阶段可运行 |
| 依赖 Frappe 特定 API 模式 | API 映射复杂 | 转换为 FastAPI REST 风格 |
| Three.js 与 Vue 3 CDN 版本 | 版本兼容 | 使用 npm 包锁定版本 |
| AGV 路径规划算法 | 性能问题 | A* 缓存 + 增量更新 |

---

## 10. 验收标准

1. **3D 渲染**: 所有区域类型（货架、立库、高位货架等）正确渲染
2. **相机控制**: 轨道视角和第一人称漫游正常工作
3. **交互功能**: 悬停、点击、双击、编辑功能完整
4. **AGV 导航**: 网格显示、路径规划、动画正常
5. **物流面板**: 任务列表、统计面板可用
6. **API 端点**: 所有定义的 API 端点可访问
7. **集成运行**: 可在 simulation 中启动并运行

---

*文档版本: 1.0*  
*最后更新: 2026-08-20*
