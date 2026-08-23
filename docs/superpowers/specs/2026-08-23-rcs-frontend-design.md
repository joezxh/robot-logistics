# RCS 控制台前端设计文档

> **项目**: Robot Logic RCS
> **日期**: 2026-08-23
> **状态**: 已批准
> **后端**: `robot-logic/rcs` (FastAPI, 端口 8100)

## 1. 概述

### 1.1 目标

为 `rcs` 后端构建一套工业具身智能风格的 Web 控制台前端，覆盖 **运营监控**（实时设备地图 + SLO 仪表盘）、**工程师调试**（命令下发 + 状态机可视化）、**客户远程运维**（任务回放 + 告警管理）三类核心场景。提供浅色 / 深色双主题切换与中文 / 英文 / 日文三语切换。

### 1.2 范围

| 模块 | 内容 |
|------|------|
| **工程脚手架** | Vite 5 + Vue 3.4 (Composition API) + TypeScript 5 |
| **UI 组件库** | Ant Design Vue 3.x |
| **状态管理** | Pinia 2 |
| **路由** | Vue Router 4（history 模式） |
| **国际化** | vue-i18n 9（zh-CN / en-US / ja-JP） |
| **实时通信** | REST (Axios) + WebSocket (原生) |
| **可视化** | ECharts 5（图表）+ Three.js（3D 机器人模型） |
| **主题系统** | CSS Variables + Ant Design Vue ConfigProvider 算法（dark/light） |
| **部署** | Nginx 静态托管（Docker 镜像） |

### 1.3 不在范围

- 不实现 WMS/MES 业务逻辑（保持 FastAPI 现有 `/api/rcs/*` 路由不动；1.x 节列出真实端点）
- 不引入 SSR（后端独立部署，SPA 模式更简洁）
- 不引入 Nuxt 等全栈框架（学习成本与生态契合度不优于纯 Vue 3）
- 客户远程运维场景作为**只读视图**（复用 Dashboard 组件 + 受限路由），不在 M1 范围新增独立模块

### 1.4 目录位置

```
robot-logic/
├── rcs/
│   ├── Dockerfile              # 后端镜像
│   ├── frontend/               # 新增：前端工程
│   │   ├── src/
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   ├── Dockerfile          # 前端镜像（nginx）
│   │   └── nginx.conf
└── ...
```

## 2. 架构设计

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────────────┐
│                      Browser (Vue 3 SPA)                         │
├──────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Dashboard  │  │   Devices   │  │    Tasks    │             │
│  │  运营大屏   │  │  设备管理   │  │  任务中心   │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│              ┌───────────┴───────────┐                         │
│              │  Pinia Stores         │                         │
│              │  - devices            │                         │
│              │  - tasks              │                         │
│              │  - alerts             │                         │
│              │  - theme              │                         │
│              └───────────┬───────────┘                         │
│                          │                                      │
│              ┌───────────┴───────────┐                         │
│              │  API Layer            │                         │
│              │  - Axios (REST)       │                         │
│              │  - WebSocket Client   │                         │
│              └───────────┬───────────┘                         │
└──────────────────────────┼─────────────────────────────────────┘
                           │ HTTP/WS
┌──────────────────────────▼─────────────────────────────────────┐
│                   FastAPI (8100) /api/rcs                       │
│  - REST endpoints                                              │
│  - WebSocket /api/rcs/ws (新增，见 2.4)                         │
│  - MQTT Adapter (可选)                                         │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 前端模块结构

```
rcs/frontend/
├── src/
│   ├── main.ts                 # 应用入口
│   ├── App.vue                 # 根组件（ConfigProvider 主题/i18n 注入）
│   ├── api/
│   │   ├── http.ts             # Axios 实例 + 拦截器
│   │   ├── ws.ts               # WebSocket 单例 + 自动重连
│   │   ├── devices.ts          # 设备 REST 封装
│   │   ├── commands.ts         # 命令下发封装
│   │   └── types.ts            # 与 shared/contracts 对齐的 TS 类型
│   ├── stores/
│   │   ├── devices.ts          # 设备注册表 + 状态流
│   │   ├── tasks.ts            # 任务 DAG + 进度
│   │   ├── alerts.ts           # 告警订阅
│   │   ├── theme.ts            # 浅色/深色切换
│   │   └── locale.ts           # i18n 切换
│   ├── views/
│   │   ├── DashboardView.vue   # 运营大屏
│   │   ├── DevicesView.vue     # 设备管理
│   │   ├── TasksView.vue       # 任务中心
│   │   └── AlertsView.vue      # 告警中心
│   ├── components/
│   │   ├── robot/
│   │   │   ├── RobotCard.vue        # 通用机器人卡片
│   │   │   ├── JointState.vue       # 关节角度可视化
│   │   │   ├── PoseViewer.vue       # 笛卡尔位姿 6D 显示
│   │   │   └── StateBadge.vue       # 状态机徽章（IDLE/RUNNING/HALTED/...）
│   │   ├── map/
│   │   │   ├── DeviceMap2D.vue      # 2D 站点地图（ECharts）
│   │   │   └── DeviceMap3D.vue      # 3D 机器人模型（Three.js）
│   │   ├── charts/
│   │   │   ├── SloGauge.vue         # SLO 仪表盘
│   │   │   ├── TaskGantt.vue        # 任务甘特图
│   │   │   └── ThroughputChart.vue  # 吞吐量曲线
│   │   └── layout/
│   │       ├── AppHeader.vue        # 顶栏（主题/语言切换）
│   │       ├── SideNav.vue          # 侧边导航
│   │       └── StatusBar.vue        # 底栏（连接状态）
│   ├── themes/
│   │   ├── light.ts            # Ant Design Vue light 算法
│   │   ├── dark.ts             # Ant Design Vue dark 算法 + 工业具身定制
│   │   └── variables.css       # CSS 变量（背景/边框/光晕）
│   ├── i18n/
│   │   ├── index.ts            # vue-i18n 配置
│   │   ├── zh-CN.ts
│   │   ├── en-US.ts
│   │   └── ja-JP.ts
│   ├── router/
│   │   └── index.ts            # Vue Router 配置
│   ├── utils/
│   │   ├── format.ts           # 数值/时间格式化
│   │   └── color.ts            # 状态颜色映射
│   └── types/
│       └── shared.d.ts         # 共享类型（与 shared/contracts 对齐）
├── public/
│   ├── favicon.svg
│   └── robots/
│       ├── arm.glb             # 单臂机器人 3D 模型
│       ├── dual-arm.glb        # 双臂装卸机器人
│       └── agv.glb             # AGV
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── Dockerfile                  # nginx:1.25-alpine
└── nginx.conf                  # try_files for SPA
```

### 2.3 状态管理（Pinia）

```ts
// stores/devices.ts (示意)
export const useDevicesStore = defineStore('devices', () => {
  const devices = ref<Map<string, DeviceProfile>>(new Map())
  const states = ref<Map<string, RobotState>>(new Map())

  // WebSocket 推流时增量更新 states
  watch(states, () => {
    // 触发 SLO 仪表盘、3D 模型位姿更新
  }, { deep: true })

  return { devices, states, registerDevice, sendCommand }
})
```

### 2.4 WebSocket 协议约定

**后端现有端点**（`rcs/rcs/service.py`，无需新增）：
- `ws_overview` —— 全量状态流（订阅 `_loop.stream`）
- `ws_device(device_id)` —— 单设备状态流（订阅 + 过滤 `device_id`）

**推送 payload**（来自 `loop.stream`，JSON）：
```json
{
  "device_id": "arm-01",
  "mode": "RUNNING",
  "joints": [0.0, 0.1, ...],
  "pose": { "x": 1.0, "y": 0.5, "z": 0.3, "qx": 0, "qy": 0, "qz": 0, "qw": 1 },
  "active_command_id": "uuid",
  "last_error": null,
  "ts": 1734567890.123
}
```

**前端接入策略**：
- 当前直接使用 `ws_overview`，所有设备状态一条 WebSocket 流；前端按 `device_id` 字段做客户端侧过滤
- `ws_device` 作为单设备详情页备用（低频轮询场景）
- 不实现客户端订阅协议（前端不做 topic 过滤），与现有后端保持一致

**断线重连**：指数退避（1s → 2s → 4s → 8s，上限 30s），心跳 30s 一次（`ping/pong`）。

### 2.5 与现有后端的契约

**REST 端点**（已存在于 `rcs/rcs/service.py`，挂载前缀 `/api/rcs`）：
- `GET  /api/rcs/registry` — 设备台账列表（含 profile 元数据）
- `POST /api/rcs/{device_id}/command` — 命令下发（`type ∈ {move_j, move_l, stop, home, estop, recover}`）
- `GET  /api/rcs/{device_id}/state` — 设备状态快照（mode / active_command_id / last_error）
- `POST /api/rcs/{device_id}/estop` — 紧急停止
- `POST /api/rcs/{device_id}/clear_estop` — 急停恢复
- `GET  /api/rcs/_health` — 控制回路健康检查

**WebSocket**（已存在）：
- `/api/rcs/ws/overview` — 全量状态流（来自 `ws_overview`）
- `/api/rcs/ws/device/{device_id}` — 单设备状态流（来自 `ws_device`）

**认证**：所有 REST 端点需 `X-API-Key` Header（`security.require_api_key`），WebSocket 通过 query 参数 `?api_key=...` 传递（**前端需确认 WebSocket 鉴权方案**，可与后端协商改造）。

**任务端点**：当前后端**未实现**任务列表接口。本设计 `TasksView` 暂以**历史命令日志**作为数据源（M1 阶段），待后端 `tasks/` 路由上线后切换（M2）。

**类型对齐**：前端 `types/shared.d.ts` 与 `rcs/rcs/service.py` 的 Pydantic 模型 `CommandRequest` 手动同步（暂不引入自动生成工具，降低初始复杂度）。

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

```vue
<!-- App.vue -->
<a-config-provider :locale="antLocale[i18n.locale.value]">
  <router-view />
</a-config-provider>
```

Ant Design Vue 的 `Locale` 类型从 `ant-design-vue/es/locale` 导入：`zhCN`、`enUS`、`jaJP`。

### 4.3 文案覆盖范围

- 所有业务文案（页面标题、按钮、表格头、状态标签）
- 告警信息（来自后端 `code` + 前端文案映射）
- 数值/时间单位（条/小时、秒、米）

## 5. 实时数据流

| 数据类型 | 通道 | 频率 | 用途 |
|---------|------|------|------|
| 设备状态（关节/位姿/控制器状态） | WebSocket | 50 Hz | 3D 模型、状态卡片 |
| 任务进度（DAG 节点完成事件） | WebSocket | 事件驱动 | 甘特图、DAG 渲染 |
| 命令下发响应 | REST POST | 请求-响应 | 命令历史、错误提示 |
| 告警 | WebSocket | 事件驱动 | 告警中心、声音提醒 |
| 设备台账变更 | REST GET | 启动时 + 手动刷新 | 设备列表 |

## 6. 部署方案

### 6.1 Docker 镜像

```dockerfile
# rcs/frontend/Dockerfile
FROM nginx:1.25-alpine
COPY dist/ /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

```nginx
# nginx.conf
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

### 6.2 Docker Compose（与后端）

```yaml
services:
  rcs-frontend:
    build: ./rcs/frontend
    ports:
      - "8101:80"
    depends_on:
      - rcs-backend
  rcs-backend:
    build: ./rcs
    ports:
      - "8100:8100"
    environment:
      RCS_CORS_ORIGINS: "http://localhost:8101"
```

### 6.3 开发模式

```bash
cd rcs/frontend
pnpm install
pnpm dev  # Vite dev server on 5173, proxy /api to 8100
```

`vite.config.ts` 中配置：
```ts
server: {
  port: 5173,
  proxy: {
    '/api': { target: 'http://127.0.0.1:8100', changeOrigin: true, ws: true }
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
| `echarts` | ^5.5 | 图表 |
| `three` | ^0.165 | 3D 渲染 |
| `@types/three` | ^0.165 | TS 类型 |
| `dayjs` | ^1.11 | 时间处理 |
| `vitest` | ^1.6 | 单元测试 |
| `@vue/test-utils` | ^2.4 | 组件测试 |

### 7.2 与现有代码的关系

- **不修改** `rcs/rcs/` 中任何 Python 文件（包括 `service.py`）
- WebSocket 直接使用 `ws_overview` / `ws_device` 现有 endpoint
- **待与后端确认**：WebSocket 鉴权方案（query `api_key` vs Header）
- **类型契约** 与 `rcs/rcs/service.py` 的 Pydantic 模型手动同步

### 7.3 测试策略

- 单元测试：`vitest` + `@vue/test-utils`，覆盖 stores 与工具函数
- 组件测试：关键组件（RobotCard、StateBadge）的渲染快照
- E2E（可选）：`playwright` 覆盖登录 → Dashboard → 命令下发主路径

## 8. 验收标准

### 8.1 功能验收

- [ ] Dashboard 页面：实时显示至少 10 台设备状态，刷新频率 ≥ 10 Hz
- [ ] Devices 页面：可下发 `move_j` / `move_l` / `stop` / `estop` 命令并查看响应
- [ ] Tasks 页面：可查看 DAG 任务图与时间线
- [ ] 主题切换：浅色 ↔ 深色 切换无白屏闪烁（FOUC < 100ms）
- [ ] 语言切换：zh-CN / en-US / ja-JP 切换正确，Ant Design 组件同步

### 8.2 性能指标

- 首屏加载（深色主题）：Lighthouse Performance ≥ 80
- 路由切换：< 200ms
- WebSocket 推流 50 Hz 时 CPU 占用 < 30%（中等配置笔记本）
- 打包体积：`dist/` gzip 后 ≤ 2 MB

### 8.3 视觉验收

- 深色主题具备工业具身特征：金属拉丝背景 + 青色霓虹光晕 + 3D 机器人模型
- 浅色主题具备玻璃拟态质感
- 3 种语言界面排版不溢出、无未翻译键

## 9. 实施里程碑（与 ROADMAP.md 对齐）

| 里程碑 | 时间 | 前端交付 |
|--------|------|---------|
| M1 | 2026-11 | 脚手架 + Dashboard + Devices + 主题/i18n 骨架 |
| M2 | 2027-02 | Tasks 中心 + 告警中心 + 3D 可视化增强 |
| M3 | 2027-08 | 多租户切换 + 高级分析图表 + 移动端适配（可选） |

## 10. 引用文档

- `docs/algorithm/06-platform.md` — 平台架构（数据流、状态机定义）
- `docs/technical/ROADMAP.md` — 12 月演进路线图
| 模块 | 内容 |
|------|------|
| **后端入口** | `rcs/rcs/service.py` 真实路径（注意：不是 router.py）|
| **REST 鉴权** | 所有端点需 `X-API-Key` Header（`require_api_key`） |
| **WebSocket** | `ws_overview`（全量）+ `ws_device(id)`（单设备），鉴权方案待定 |
| **任务 API** | 后端未实现，TasksView M1 用历史命令日志兜底 |
- `rcs/rcs/service.py` — 后端 REST/WebSocket 真实路由清单
- `rcs/rcs/state/command.py` — Command 数据结构
- `rcs/rcs/hal/base.py` — HALState 数据结构
