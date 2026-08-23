# RCS 控制台前端设计文档

> **项目**: Robot Logic RCS
> **日期**: 2026-08-23
> **状态**: 已批准（v2 — 全量 PRD 对齐）
> **后端**: `robot-logic/rcs` (FastAPI, 端口 8100)

## 1. 概述

### 1.1 目标

为 `rcs` 调度中枢构建一套**工业具身智能风格的 Web 控制台前端**，覆盖 PRD 规定的完整业务闭环：**订单管理 → 任务编排 → 调度监控 → 异常告警**。覆盖**三类用户角色**：运营监控、工程师调试、客户远程运维。提供浅色 / 深色双主题切换与中文 / 英文 / 日文三语切换。

### 1.2 系统定位

```
┌──────────────────────────────────────────────────────┐
│                  Browser (Vue 3 SPA)                  │
│  运营大屏 | 订单管理 | 任务中心 | 站点地图 | 设备台账 │
│  告警中心 | 系统设置 | 工程师调试                     │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP / WebSocket / MQTT
┌────────────────────▼─────────────────────────────────┐
│         RCS FastAPI (8100) /api/rcs/*               │
│  • 订单 REST  + MQTT 接入 WMS/MES                    │
│  • 任务 DAG 编排与持久化                             │
│  • 调度器（EDF + 关键路径）                         │
│  • 设备台账 Registry + 状态流 WebSocket             │
│  • MQTT ←→ HAL 抽象层                                │
└────────────────────┬─────────────────────────────────┘
                     │ MQTT / HAL（沙盒使用 SimHAL；真实部署用真实硬件 HAL）
          ┌──────────┴────────────┐
          │  6 类设备执行层       │
          │  装卸机器人 · AGV    │
          │  立库 · 输送带       │
          │  四向穿梭车 · 电梯  │
          └───────────────────────┘
```

> **关键约束**：
> - `robot-control-stack`（VLA / Wrapper / MuJoCo）仅作参考，功能迁移到 RCS 后端；前端**仅连接 RCS FastAPI**。
> - 沙盒模式使用 SimHAL + 模拟订单生成器，无需真实硬件；真实部署时通过真实 HAL 接入 PLC / 单机控制器。

### 1.3 范围

| 模块 | 内容 |
|------|------|
| **工程脚手架** | Vite 5 + Vue 3.4 (Composition API) + TypeScript 5 |
| **UI 组件库** | Ant Design Vue 3.x |
| **状态管理** | Pinia 2 |
| **路由** | Vue Router 4（history 模式） |
| **国际化** | vue-i18n 9（zh-CN / en-US / ja-JP） |
| **实时通信** | REST (Axios) + WebSocket（原生，10Hz 状态流）+ MQTT（mqtt.js，告警事件） |
| **可视化** | ECharts 5（图表/甘特图/仪表盘）+ Three.js（3D 机器人模型） |
| **主题系统** | CSS Variables + Ant Design Vue ConfigProvider 算法（dark/light） |
| **部署** | Docker Compose（前端 nginx + 后端 uvicorn + SimHAL 数据生成） |

### 1.4 不在范围

- 不实现 WMS/MES 业务逻辑（保持 FastAPI 现有 `/api/rcs/*` 路由；订单通过 REST/MQTT 接入）
- 不实现真实硬件 HAL（沙盒模式使用 SimHAL + 模拟订单生成器）
- 不引入 SSR（后端独立部署，SPA 模式更简洁）
- 不引入 Nuxt 等全栈框架
- 不直接对接 `robot-control-stack` 的 rpyc 接口

### 1.5 目录位置

```
robot-logic/
├── rcs/
│   ├── Dockerfile              # 后端镜像
│   ├── docker-compose.yml      # 一键启动前后端 + SimHAL 数据
│   ├── frontend/               # 新增：前端工程
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── http.ts             # Axios 实例 + 拦截器
│   │   │   │   ├── ws.ts               # WebSocket 单例 + 自动重连（指数退避）
│   │   │   │   ├── mqtt.ts             # mqtt.js 客户端（告警订阅）
│   │   │   │   ├── devices.ts          # 设备 REST 封装
│   │   │   │   ├── orders.ts           # 订单 REST 封装
│   │   │   │   ├── tasks.ts            # 任务 DAG REST 封装
│   │   │   │   ├── topology.ts         # 站点地图 REST 封装
│   │   │   │   ├── simulator.ts        # 模拟订单生成器 API
│   │   │   │   └── types.ts            # 与 shared/contracts 对齐的 TS 类型
│   │   │   ├── stores/
│   │   │   │   ├── devices.ts          # 设备注册表 + 状态流
│   │   │   │   ├── orders.ts           # 订单列表 + 当前选中
│   │   │   │   ├── tasks.ts            # 任务 DAG + 进度
│   │   │   │   ├── topology.ts         # 站点地图节点/边
│   │   │   │   ├── alerts.ts           # 告警订阅（MQTT）
│   │   │   │   ├── simulator.ts        # 模拟订单生成器状态
│   │   │   │   ├── theme.ts            # 浅色/深色切换
│   │   │   │   ├── locale.ts           # i18n 切换
│   │   │   │   └── auth.ts             # 角色 + API Key 管理
│   │   │   ├── views/
│   │   │   │   ├── DashboardView.vue   # 运营大屏
│   │   │   │   ├── OrdersView.vue      # 订单管理
│   │   │   │   ├── TasksView.vue       # 任务中心（DAG 甘特图）
│   │   │   │   ├── SiteMapView.vue     # 站点地图编辑器
│   │   │   │   ├── DevicesView.vue     # 设备台账 + 专属命令面板
│   │   │   │   ├── AlertsView.vue      # 告警中心
│   │   │   │   └── SettingsView.vue    # 系统设置
│   │   │   ├── components/
│   │   │   │   ├── robot/
│   │   │   │   │   ├── RobotCard.vue        # 通用机器人卡片
│   │   │   │   │   ├── JointState.vue       # 关节角度可视化
│   │   │   │   │   ├── PoseViewer.vue       # 笛卡尔位姿 6D 显示
│   │   │   │   │   ├── DualArmLoader.vue    # 双臂装卸机器人专属面板
│   │   │   │   │   ├── StateBadge.vue       # 状态机徽章（IDLE/RUNNING/HALTED/...）
│   │   │   │   │   └── devicePanels/        # 按设备类型的命令面板
│   │   │   │   │       ├── AgvPanel.vue
│   │   │   │   │       ├── AsrsPanel.vue     # 立库（堆垛机）
│   │   │   │   │       ├── ConveyorPanel.vue
│   │   │   │   │       ├── ShuttlePanel.vue  # 四向穿梭车
│   │   │   │   │       └── ElevatorPanel.vue
│   │   │   │   ├── map/
│   │   │   │   │   ├── DeviceMap2D.vue      # 2D 站点地图（ECharts）
│   │   │   │   │   ├── DeviceMap3D.vue      # 3D 机器人模型（Three.js）
│   │   │   │   │   └── TopologyEditor.vue   # 节点/边拖拽编辑器
│   │   │   │   ├── charts/
│   │   │   │   │   ├── SloGauge.vue         # SLO 仪表盘
│   │   │   │   │   ├── TaskGantt.vue        # 任务甘特图（TaskDAG 时间线）
│   │   │   │   │   ├── ThroughputChart.vue  # 吞吐量曲线
│   │   │   │   │   └── DagGraph.vue         # 任务 DAG 有向图
│   │   │   │   ├── simulator/
│   │   │   │   │   └── OrderSimulator.vue   # 模拟订单生成器面板
│   │   │   │   └── layout/
│   │   │   │       ├── AppHeader.vue        # 顶栏（主题/语言/角色切换）
│   │   │   │       ├── SideNav.vue          # 侧边导航（按角色权限过滤）
│   │   │   │       └── StatusBar.vue        # 底栏（连接状态 / WS / MQTT）
│   │   │   ├── themes/
│   │   │   │   ├── light.ts            # Ant Design Vue light 算法
│   │   │   │   ├── dark.ts             # Ant Design Vue dark 算法 + 工业具身定制
│   │   │   │   └── variables.css       # CSS 变量（背景/边框/光晕）
│   │   │   ├── i18n/
│   │   │   │   ├── index.ts            # vue-i18n 配置
│   │   │   │   ├── zh-CN.ts
│   │   │   │   ├── en-US.ts
│   │   │   │   └── ja-JP.ts
│   │   │   ├── router/
│   │   │   │   └── index.ts            # Vue Router 配置（含角色权限守卫）
│   │   │   ├── utils/
│   │   │   │   ├── format.ts           # 数值/时间格式化
│   │   │   │   └── color.ts            # 状态颜色映射
│   │   │   ├── types/
│   │   │   │   └── shared.d.ts         # 共享类型（与 shared/contracts 对齐）
│   │   │   ├── App.vue                 # 根组件（ConfigProvider 主题/i18n 注入）
│   │   │   └── main.ts                 # 应用入口
│   │   ├── public/
│   │   │   ├── favicon.svg
│   │   │   └── robots/
│   │   │       ├── arm.glb             # 单臂机器人 3D 模型
│   │   │       ├── dual-arm.glb        # 双臂装卸机器人
│   │   │       └── agv.glb             # AGV
│   │   ├── package.json
│   │   ├── vite.config.ts              # 开发代理 /api → 8100
│   │   ├── tsconfig.json
│   │   ├── Dockerfile                  # nginx:1.25-alpine
│   │   └── nginx.conf                  # try_files for SPA
│   ├── backend/api/                    # 后端扩展（订单 / 任务 / 拓扑 REST）
│   │   ├── orders.py                   # 订单 CRUD + 模拟生成
│   │   ├── tasks.py                    # TaskDAG 查询接口
│   │   ├── topology.py                 # 站点地图 CRUD
│   │   ├── simulator.py                # 模拟订单生成 API
│   │   └── alerts_ws.py                # MQTT 告警 WebSocket 桥接（如需）
│   └── simulator/                      # SimHAL 数据生成（沙盒模式）
│       └── seed_devices.py             # 6 类设备默认配置
```

## 2. 架构设计

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                      Browser (Vue 3 SPA)                         │
├──────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Dashboard │  │  Orders  │  │  Tasks   │  │ SiteMap  │         │
│  │ 运营大屏 │  │ 订单管理 │  │ 任务中心 │  │ 地图编辑 │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │              │             │                │
│  ┌────▼─────────────▼──────────────▼─────────────▼────┐          │
│  │        Pinia Stores (devices/orders/tasks/...)     │          │
│  └────┬───────────┬───────────┬───────────────┬───────┘          │
│       │           │           │               │                   │
│  ┌────▼─────┐ ┌───▼────┐ ┌────▼─────┐ ┌──────▼──────┐           │
│  │  Axios   │ │  WS    │ │  mqtt.js │ │  Simulator  │           │
│  │  REST    │ │ 10Hz   │ │ 告警订阅 │ │ 模拟订单    │           │
│  └────┬─────┘ └───┬────┘ └────┬─────┘ └──────┬──────┘           │
└───────┼───────────┼───────────┼──────────────┼─────────────────┘
        │ HTTP      │ WSS       │ mqtt         │ HTTP
┌───────▼───────────▼───────────▼──────────────▼─────────────────┐
│             FastAPI (8100) /api/rcs                            │
│  • /orders       /tasks       /topology       /registry         │
│  • /ws/overview  /ws/device/{id}  /simulator/generate         │
│  • /alerts/ws    MQTT broker bridge                            │
└────────────────────────────────────────────────────────────────┘
```

### 2.2 状态管理（Pinia）

```ts
// stores/orders.ts (示意)
export const useOrdersStore = defineStore('orders', () => {
  const orders = ref<Map<string, Order>>(new Map())
  const selectedId = ref<string | null>(null)

  async function fetchList(filter?: OrderFilter) { /* REST 调用 */ }
  async function createOrder(req: CreateOrderRequest) { /* REST POST */ }
  async function simulateOrders(n: number, template: SimTemplate) { /* 调用模拟 API */ }

  return { orders, selectedId, fetchList, createOrder, simulateOrders }
})
```

### 2.3 WebSocket 协议约定

**后端现有端点**（`rcs/rcs/service.py`，无需新增）：
- `ws_overview` —— 全量状态流（订阅 `_loop.stream`）
- `ws_device(device_id)` —— 单设备状态流（订阅 + 过滤 `device_id`）

**推送 payload**（来自 `loop.stream`，JSON）：
```json
{
  "device_id": "dual-arm-01",
  "mode": "RUNNING",
  "joints": [0.0, 0.1, ...],
  "pose": { "x": 1.0, "y": 0.5, "z": 0.3, "qx": 0, "qy": 0, "qz": 0, "qw": 1 },
  "active_command_id": "uuid",
  "task_id": "task-uuid",
  "task_progress": 0.42,
  "last_error": null,
  "ts": 1734567890.123
}
```

**前端接入策略**：
- 当前直接使用 `ws_overview`，所有设备状态一条 WebSocket 流；前端按 `device_id` 字段做客户端侧过滤
- `ws_device` 作为单设备详情页备用（低频轮询场景）
- 不实现客户端订阅协议（前端不做 topic 过滤），与现有后端保持一致
- 新增 `task_id` 与 `task_progress` 字段（待后端扩展 `StateFrame`），用于甘特图实时进度

**断线重连**：指数退避（1s → 2s → 4s → 8s，上限 30s），心跳 30s 一次（`ping/pong`）。

### 2.4 MQTT 告警订阅

| Topic | 用途 | 频率 |
|-------|------|------|
| `rcs/{device_id}/alert` | 设备级告警（来自 `AlertPublisher`） | 事件驱动 |
| `rcs/system/alert` | 系统级告警（调度器故障、订单超时） | 事件驱动 |

前端通过 `mqtt.js` 订阅上述 topic，事件写入 `alerts` store，触发：
- AlertsView 列表实时刷新
- Dashboard 顶部告警计数徽章
- 浏览器通知（可选，需用户授权）

### 2.5 与现有后端的契约

#### 现有 REST 端点（不动）

| Method | Path | 描述 |
|--------|------|------|
| GET | `/api/rcs/registry` | 设备台账列表 |
| POST | `/api/rcs/{device_id}/command` | 命令下发（顶层 `type ∈ {move_j, move_l, stop, home, estop, recover}`）；设备专属动作通过 `parameters.task_type` 传递（如 `DualArmLoader` 的 `open_grip`/`close_grip`/`hug_grasp`/`dual_arm_sync`，`Stacker` 的 `pick`/`place`，`Forklift` 的 `extend`/`lift`/`move_to`/`pick`/`drop`） |
| GET | `/api/rcs/{device_id}/state` | 设备状态快照 |
| POST | `/api/rcs/{device_id}/estop` | 紧急停止 |
| POST | `/api/rcs/{device_id}/clear_estop` | 急停恢复 |
| GET | `/api/rcs/_health` | 控制回路健康检查 |

#### 现有 WebSocket

- `ws://host:8100/api/rcs/ws/overview` — 全量状态流（来自 `ws_overview`）
- `ws://host:8100/api/rcs/ws/device/{device_id}` — 单设备状态流

#### 新增 REST 端点（前端驱动，需要后端实现）

| Method | Path | 描述 | 角色 |
|--------|------|------|------|
| GET | `/api/rcs/orders` | 订单列表（分页 + 过滤） | 运营 / 工程师 |
| POST | `/api/rcs/orders` | 创建订单（入库/出库/移库） | 运营 |
| GET | `/api/rcs/orders/{order_id}` | 订单详情（含 TaskDAG 引用） | 运营 |
| DELETE | `/api/rcs/orders/{order_id}` | 取消订单（未执行） | 运营 |
| GET | `/api/rcs/orders/{order_id}/dag` | 订单的 DAG 结构（节点 + 边） | 运营 |
| GET | `/api/rcs/tasks` | 任务列表（按状态过滤） | 工程师 |
| GET | `/api/rcs/tasks/{task_id}` | 任务详情 | 工程师 |
| GET | `/api/rcs/topology` | 站点地图（节点 + 边） | 工程师 |
| PUT | `/api/rcs/topology` | 保存站点地图 | 工程师 |
| POST | `/api/rcs/topology/path` | A* 路径查询（src, dst） | 工程师 |
| POST | `/api/rcs/simulator/generate` | 模拟订单生成（n, type, template） | 运营 / 工程师 |
| GET | `/api/rcs/simulator/devices` | SimHAL 设备 seed 配置列表 | 运营 |

**认证**：所有 REST 端点需 `X-API-Key` Header（`security.require_api_key`），WebSocket 通过 query 参数 `?api_key=...` 传递，MQTT 通过用户名/密码或匿名（沙盒模式默认允许）。

### 2.6 模拟订单生成器

**目的**：在无 WMS/MES 接入时，前端可一键生成测试订单，演示完整业务流程。

**前端入口**：`components/simulator/OrderSimulator.vue`

**配置参数**：
- 订单类型：入库 / 出库 / 移库
- 数量：1 ~ 100
- 模板：随机 / 固定 SKU / 自定义（sku_list、locations）
- 提交节奏：立即 / 间隔 N 秒（模拟订单流）

**后端实现**（`rcs/backend/api/simulator.py`）：
- 接收 `{count, type, template, interval_ms?}`
- 生成对应 `Order` Pydantic 对象
- 调用 `decompose_order()` → TaskDAG
- 入库 + 加入调度队列
- 返回生成结果（order_ids + dag_ids）

### 2.7 角色与权限

| 角色 | 视图访问 | 操作权限 |
|------|---------|---------|
| **运营** | Dashboard / Orders / Tasks / Alerts（只读）/ Simulator | 创建/取消订单、生成模拟订单 |
| **工程师** | Dashboard / Orders / Tasks / SiteMap / Devices / Alerts / Settings | 全部 |
| **运维（只读）** | Dashboard / Tasks / Alerts（只读视图，复用 Dashboard 组件） | 只读 |

**前端实现**：
- `stores/auth.ts` 维护当前角色（localStorage 持久化）
- `router/index.ts` 通过 `beforeEach` 守卫拦截无权访问的路由
- `SideNav.vue` 根据角色过滤菜单项
- 按钮级别通过 `v-if="auth.can('device.estop')"` 控制

### 2.8 实时数据流

| 数据类型 | 通道 | 频率 | 用途 |
|---------|------|------|------|
| 设备状态（关节/位姿/控制器状态） | WebSocket | 50 Hz | 3D 模型、状态卡片 |
| 任务进度（DAG 节点完成事件） | WebSocket | 事件驱动 | 甘特图、DAG 渲染 |
| 命令下发响应 | REST POST | 请求-响应 | 命令历史、错误提示 |
| 告警 | MQTT | 事件驱动 | 告警中心、声音提醒 |
| 设备台账变更 | REST GET | 启动时 + 手动刷新 | 设备列表 |
| 订单状态变更 | WebSocket / REST polling | 1 Hz | 订单列表实时刷新 |

## 3. 视觉规范

### 3.1 浅色主题（Light）

- **主背景**：`#fafafa`
- **卡片背景**：`#ffffff` + `border: 1px solid #e8e8e8`
- **主色**：`#1677ff`（Ant Design 默认蓝）
- **强调色**：`#00e5ff`（青色，用于机器人状态指示）
- **状态色**：运行 `#52c41a` / 急停 `#ff4d4f` / 告警 `#faad14` / 空闲 `#8c8c8c`
- **风格特征**：玻璃拟态（`backdrop-filter: blur(20px)`）+ 微阴影（`box-shadow: 0 2px 8px rgba(0,0,0,0.06)`）

### 3.2 深色主题（Dark — 工业具身风格）

- **主背景**：`linear-gradient(135deg, #0a0e27 0%, #050816 100%)` + 拉丝纹理 SVG 叠加
- **卡片背景**：`rgba(15, 23, 42, 0.85)` + 金属边框 `1px solid rgba(0, 229, 255, 0.2)`
- **主色**：`#00e5ff`（青色霓虹）
- **强调色**：`#ff6b35`（急停橙红）、`#52c41a`（运行绿）、`#faad14`（告警黄）
- **光晕**：`box-shadow: 0 0 20px rgba(0, 229, 255, 0.3)`（按钮/激活态）
- **网格背景**：等距点阵 `radial-gradient(circle, rgba(0, 229, 255, 0.1) 1px, transparent 1px)` 30px 间隔
- **拟物元素**：机器人 3D 模型（Three.js 加载 `.glb`）、金属拉丝背景、霓虹边框
- **字体**：英文 `Inter` / 中文 `思源黑体` / 日文 `Noto Sans JP`

### 3.3 主题切换实现

```ts
// themes/dark.ts
export const darkTheme = {
  algorithm: darkAlgorithm,
  token: {
    colorPrimary: '#00e5ff',
    colorBgBase: '#050816',
    colorBgContainer: 'rgba(15, 23, 42, 0.85)',
    borderRadius: 6,
    fontFamily: 'Inter, "Noto Sans SC", "Noto Sans JP", sans-serif',
  },
  components: {
    Button: { primaryShadow: '0 0 20px rgba(0, 229, 255, 0.4)' },
    Card: { colorBorderSecondary: 'rgba(0, 229, 255, 0.2)' },
  },
}
```

```vue
<!-- App.vue -->
<a-config-provider :theme="themeStore.current">
  <router-view />
</a-config-provider>
```

## 4. 国际化

### 4.1 语言支持

| 语言 | 区域代码 | 默认 | 触发条件 |
|------|---------|------|---------|
| 简体中文 | `zh-CN` | ✓ | `navigator.language` 以 `zh` 开头 |
| 英语 | `en-US` | | 其他（兜底） |
| 日语 | `ja-JP` | | `navigator.language` 以 `ja` 开头 |

### 4.2 实现

```ts
// i18n/index.ts
import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import enUS from './en-US'
import jaJP from './ja-JP'

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'en-US',
  messages: { 'zh-CN': zhCN, 'en-US': enUS, 'ja-JP': jaJP },
})
```

### 4.3 文案覆盖范围

- 所有业务文案（页面标题、按钮、表格头、状态标签）
- 告警信息（来自后端 `code` + 前端文案映射）
- 数值/时间单位（条/小时、秒、米）

## 5. 设备类型 UI 覆盖（PRD 6 类设备）

PRD §1.4 列出的核心场景要求覆盖：AGV、立库、装卸机器人、输送带、四向穿梭车、电梯。前端为每类设备提供专属命令面板：

| 设备类型 | 后端形态 | 命令类型 | UI 组件 | 状态展示 |
|---------|---------|---------|---------|---------|
| **双臂装卸机器人** ⭐ | `DualArmLoaderController` | `move_j`, `move_l`, `open_grip`, `close_grip`, `hug_grasp`, `dual_arm_sync`, `estop` | `DualArmLoader.vue` | 双臂关节曲线、6D 位姿、协同状态、夹爪开合度 |
| **AGV** | `AgvController` | `move_to`, `charge`, `stop`, `estop` | `AgvPanel.vue` | 2D 坐标、速度、电池、当前站点、目标站点 |
| **立库（堆垛机）** | `StackerController` | `pick`, `place`, `move_srm`, `home`, `estop` | `AsrsPanel.vue` | 货位列、货叉位置、作业进度、高度方向动画 |
| **输送带** | （新增 Morphology：`CONVEYOR`） | `start`, `stop`, `set_speed`, `reverse` | `ConveyorPanel.vue` | 当前速度、方向、传感器触发、速度曲线 |
| **四向穿梭车** | （新增 Morphology：`SHUTTLE`） | `move_rack`, `swap_level`, `charge`, `estop` | `ShuttlePanel.vue` | 网格坐标、货位状态、电池、网格地图热力图 |
| **电梯** | （新增 Morphology：`ELEVATOR`） | `call`, `goto_floor`, `open_door`, `close_door` | `ElevatorPanel.vue` | 当前楼层、门状态、上下行、楼层队列 |

> **后端扩展需求**：输送带、四向穿梭车、电梯目前在 `rcs/devices/` 与 `rcs/controllers/` 中**仅有基础 Pydantic 模型**或不存在完整控制器。详见 §10 "实施路径与后端扩展"。
>
> **辅助设备说明**：`ForkliftController`（叉车）虽在后端实现，但作为"装卸场景辅助"，不单独列入 6 类核心设备面板；其 UI 复用 `ArmController` 类卡片 + 专属命令字段（extend/lift/move_to/pick/drop）。

## 6. 部署方案

### 6.1 Docker Compose（推荐）

```yaml
# rcs/docker-compose.yml
version: '3.8'
services:
  rcs-frontend:
    build: ./frontend
    ports:
      - "8101:80"
    environment:
      - VITE_API_BASE=http://localhost:8100
      - VITE_WS_BASE=ws://localhost:8100
      - VITE_MQTT_URL=mqtt://localhost:1883
    depends_on:
      - rcs-backend
      - mosquitto

  rcs-backend:
    build: .
    ports:
      - "8100:8100"
    environment:
      - RCS_CORS_ORIGINS=http://localhost:8101
      - RCS_API_AUTH_ENABLED=true
      - RCS_API_KEYS=dev-key-1,dev-key-2
      - RCS_MQTT_ENABLED=true
      - RCS_MQTT_HOST=mosquitto
      - RCS_MQTT_PORT=1883
      - RCS_DEVICE_PROFILES=@seed_devices.json
    depends_on:
      - mosquitto

  mosquitto:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
```

### 6.2 开发模式

```bash
cd rcs/frontend
pnpm install
pnpm dev  # Vite dev server on 5173, proxy /api + /ws to 8100
```

```ts
// vite.config.ts
server: {
  port: 5173,
  proxy: {
    '/api': { target: 'http://127.0.0.1:8100', changeOrigin: true, ws: true }
  }
}
```

### 6.3 前端 Dockerfile

```dockerfile
# rcs/frontend/Dockerfile
FROM nginx:1.25-alpine
COPY dist/ /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```nginx
# rcs/frontend/nginx.conf
server {
  listen 80;
  root /usr/share/nginx/html;
  index index.html;
  location / {
    try_files $uri $uri/ /index.html;  # SPA history 模式
  }
  location /api/ {
    proxy_pass http://rcs-backend:8100;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

## 7. 边界与依赖

### 7.1 依赖项

| 包名 | 版本 | 用途 |
|------|------|------|
| `vue` | ^3.4 | 框架 |
| `vue-router` | ^4.3 | 路由 |
| `pinia` | ^2.1 | 状态管理 |
| `ant-design-vue` | ^3.2 | UI 组件库 |
| `vue-i18n` | ^9.13 | 国际化 |
| `@ant-design/icons-vue` | ^7 | 图标 |
| `axios` | ^1.7 | HTTP 客户端 |
| `echarts` | ^5.5 | 图表 / DAG / 甘特图 |
| `three` | ^0.165 | 3D 渲染 |
| `@types/three` | ^0.165 | TS 类型 |
| `mqtt` | ^5.3 | MQTT 客户端（告警订阅） |
| `dayjs` | ^1.11 | 时间处理 |
| `vitest` | ^1.6 | 单元测试 |
| `@vue/test-utils` | ^2.4 | 组件测试 |

### 7.2 与现有代码的关系

- **不修改** `rcs/rcs/` 中任何 Python 文件（包括 `service.py`）
- WebSocket 直接使用 `ws_overview` / `ws_device` 现有 endpoint
- **新增后端模块**：`rcs/backend/api/`（订单 / 任务 / 拓扑 / 模拟器）；不与 `rcs/rcs/` 现有命名空间冲突
- **类型契约** 与 `rcs/rcs/service.py` 的 Pydantic 模型手动同步

### 7.3 测试策略

- 单元测试：`vitest` + `@vue/test-utils`，覆盖 stores 与工具函数
- 组件测试：关键组件（RobotCard、StateBadge、DagGraph）的渲染快照
- E2E（可选）：`playwright` 覆盖登录 → Dashboard → 创建订单 → 监控任务主路径

## 8. 验收标准

### 8.1 功能验收

#### Dashboard
- [ ] 实时显示至少 6 类设备的代表设备状态（≥ 10 台），刷新频率 ≥ 10 Hz
- [ ] SLO 仪表盘：订单完成率、平均任务延迟、设备利用率
- [ ] 吞吐量曲线：最近 1 小时每分钟完成的订单数
- [ ] 告警摘要：最近 10 条告警 + 未确认计数

#### Orders
- [ ] 订单列表：分页 + 按类型/状态/时间过滤
- [ ] 创建订单：表单校验（SKU 列表、起止位置、优先级、deadline）
- [ ] 订单详情：展示 TaskDAG 拆解结果（节点 + 边）
- [ ] 取消订单（仅未执行状态）
- [ ] 模拟订单生成器：一键生成 N 条订单，支持模板选择

#### Tasks
- [ ] 任务列表：按订单/状态/设备过滤
- [ ] 任务甘特图：可视化 DAG 节点的时间线（ECharts）
- [ ] DAG 图渲染：节点 + 边 + 状态着色
- [ ] 任务详情：参数、设备、执行结果

#### SiteMap
- [ ] 2D 站点地图：节点 + 边的可视化编辑（拖拽）
- [ ] A* 路径预览：选择起点终点后显示最短路径
- [ ] 拓扑保存 / 加载

#### Devices
- [ ] 6 类设备全覆盖，每类有独立命令面板
- [ ] 设备专属状态展示（关节 / 6D 位姿 / 速度 / 楼层等）
- [ ] 紧急停止（estop）/ 恢复（recover）按钮
- [ ] 设备台账列表（按形态过滤）

#### Alerts
- [ ] 实时告警列表（MQTT 订阅）
- [ ] 告警确认 / 解决操作
- [ ] 按设备 / 级别 / 时间过滤
- [ ] 浏览器通知（可选，需用户授权）

#### Settings
- [ ] 主题切换：浅色 ↔ 深色 无白屏闪烁（FOUC < 100ms）
- [ ] 语言切换：zh-CN / en-US / ja-JP
- [ ] 角色切换：运营 / 工程师 / 运维

### 8.2 性能指标

- 首屏加载（深色主题）：Lighthouse Performance ≥ 80
- 路由切换：< 200ms
- WebSocket 推流 50 Hz 时 CPU 占用 < 30%（中等配置笔记本）
- 打包体积：`dist/` gzip 后 ≤ 2 MB

### 8.3 视觉验收

- 深色主题具备工业具身特征：金属拉丝背景 + 青色霓虹光晕 + 3D 机器人模型
- 浅色主题具备玻璃拟态质感
- 3 种语言界面排版不溢出、无未翻译键

## 9. 实施里程碑

| 里程碑 | 时间 | 前端交付 |
|--------|------|---------|
| **M1（基础）** | 4 周 | 脚手架 + 主导航 + Dashboard + Devices + 主题/i18n + 角色权限 + Docker Compose |
| **M2（订单/任务）** | 4 周 | Orders + Tasks + 模拟订单生成器 + 后端 API 实现 |
| **M3（地图/告警）** | 3 周 | SiteMap 编辑器 + Alerts + MQTT 订阅 + 后端 API 实现 |
| **M4（增强）** | 2 周 | 3D 装卸机器人 + 高级图表 + E2E 测试 |

## 10. 实施路径与后端扩展

### 10.1 前端驱动的后端扩展

前端实现需要后端新增以下模块（M2/M3 阶段并行开发）：

| 模块 | 后端路径 | 描述 |
|------|---------|------|
| 订单 CRUD | `rcs/backend/api/orders.py` | 订单 REST 端点 + 持久化 |
| TaskDAG 查询 | `rcs/backend/api/tasks.py` | 任务列表 + DAG 结构接口 |
| 站点地图 | `rcs/backend/api/topology.py` | 拓扑 CRUD + A* 路径查询 |
| 模拟器 | `rcs/backend/api/simulator.py` | 模拟订单生成 + SimHAL 设备 seed |
| MQTT 告警桥接 | `rcs/backend/api/alerts_ws.py` | MQTT → WebSocket 桥接（如需） |

### 10.2 设备形态扩展（输送带 / 穿梭车 / 电梯）

PRD §1.4 列出的 6 类设备中，后端目前仅完整实现了 5 种（Arm/AGV/Stacker/Forklift/DualArmLoader）。**新增的 3 类设备**需要在后端扩展：

| 设备 | 需要新增 | 工作量 |
|------|---------|--------|
| **输送带** | `Morphology.CONVEYOR` + `ConveyorSpec` + `ConveyorController` | 2 ~ 3 天 |
| **四向穿梭车** | `Morphology.SHUTTLE` + `ShuttleSpec` + `ShuttleController` | 3 ~ 4 天 |
| **电梯** | `Morphology.ELEVATOR` + `ElevatorSpec` + `ElevatorController` | 2 ~ 3 天 |

> 详情见后续 writing-plans 阶段生成的实施计划。

### 10.3 StateFrame 扩展

需要在 `rcs/state/state_stream.py:StateFrame` 中新增字段：
```python
class StateFrame(BaseModel):
    # ... 现有字段
    task_id: str | None = None
    task_progress: float | None = None  # 0.0 ~ 1.0
```

供前端甘特图实时进度展示使用。

## 11. 引用文档

- `docs/superpowers/specs/2026-08-23-rcs-prd-design.md` — RCS PRD（业务需求来源）
- `docs/superpowers/plans/2026-08-23-rcs-prd-implementation.md` — RCS 后端实施计划
- `docs/algorithm/06-platform.md` — 平台架构（数据流、状态机定义）
- `docs/technical/ROADMAP.md` — 演进路线图
- `rcs/rcs/service.py` — 现有后端 REST/WebSocket 真实路由清单
- `rcs/rcs/state/command.py` — Command 数据结构
- `rcs/rcs/hal/base.py` — HALState 数据结构
- `rcs/rcs/orders/decomposer.py` — 订单 → DAG 拆解器
- `rcs/rcs/scheduler/allocator.py` — 设备分配器
- `rcs/rcs/topology/site_map.py` — 站点地图
- `rcs/rcs/topology/pathfinder.py` — A* 路径规划
