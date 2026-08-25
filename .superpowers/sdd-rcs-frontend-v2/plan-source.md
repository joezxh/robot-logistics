# RCS Frontend v2.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `robot-logic/rcs/frontend/` 下创建独立前端工程（Vite + Vue 3 + TypeScript），实现 6 场景（电商/制造/冷链/港口/退货/多层）物流地图的可视化与交互。

**Architecture:** 单页 Vue 3 + Pinia。`stores/scenario.ts` 管理当前场景与配置；`views/SiteMapView.vue` 协调 2D/3D 切换、6 个场景组件的渲染；`components/map/scenarios/` 下 6 个场景组件复用 `DeviceMap2D.vue` 与 `DeviceMap3D.vue`。通过 Vite proxy 调用后端（`/api/rcs` → `:8100`，`/api` → `:8000`）。

**Tech Stack:** Vite 5 / Vue 3.4 / TypeScript 5.4 / Pinia 2.1 / vue-router 4.3 / Ant Design Vue 3.2 / ECharts 5.5 / Three.js 0.165 / axios 1.7 / vitest 1.6

**Spec Reference:** `docs/superpowers/specs/2026-08-23-rcs-frontend-design.md` §13.3, §13.5

**Depends On:** Backend plan `2026-08-23-rcs-backend-v2-implementation.md`（rcs/backend/ 必须先完成，否则 6 场景组件无后端数据）

## Global Constraints

- **Node.js 版本**：20 LTS（对齐 `rcs/frontend/Dockerfile`）
- **包管理**：pnpm（corepack enable）
- **TypeScript**：strict mode，所有 props 必须有类型
- **组件命名**：PascalCase，文件名 PascalCase.vue
- **Pinia store**：每个 store 一个文件，defineStore 组合式 API
- **HTTP 客户端**：统一用 `src/api/http.ts` 的 axios 实例
- **依赖管理**：使用 `rcs/frontend/package.json`，新增依赖必须带版本号
- **不修改**：`rcs/rcs/`、`rcs/backend/`、`shared/`、`simulation/`、`deploy/`、`docs/`
- **可修改**：`rcs/frontend/`（新建）、`deploy/docker-compose.yml`（追加服务）
- **响应式**：所有视图必须 1280×800 最小可用
- **国际化**：`vue-i18n`，中英文双语，中文为主
- **无障碍**：所有交互元素必须可键盘访问，aria-label 必需

---

## File Structure

```
rcs/frontend/
├── package.json
├── pnpm-lock.yaml
├── tsconfig.json
├── vite.config.ts
├── index.html
├── Dockerfile
├── nginx.conf
├── README.md
├── src/
│   ├── main.ts
│   ├── App.vue
│   ├── router/
│   │   └── index.ts
│   ├── api/
│   │   ├── http.ts
│   │   ├── topologyShell.ts
│   │   ├── topologyGrid.ts
│   │   ├── topologyImport.ts
│   │   ├── topologyExport.ts
│   │   ├── topologyTemplates.ts
│   │   └── orders.ts
│   ├── stores/
│   │   ├── scenario.ts
│   │   ├── floorShell.ts
│   │   ├── siteGrid.ts
│   │   └── topology.ts
│   ├── types/
│   │   ├── floorShell.ts
│   │   ├── siteGrid.ts
│   │   └── scenario.ts
│   ├── i18n/
│   │   ├── index.ts
│   │   ├── zh-CN.ts
│   │   └── en-US.ts
│   ├── views/
│   │   └── SiteMapView.vue
│   ├── components/
│   │   ├── map/
│   │   │   ├── DeviceMap2D.vue
│   │   │   ├── DeviceMap3D.vue
│   │   │   ├── ShellScene.ts
│   │   │   ├── DevicePool.ts
│   │   │   ├── DxfOverlay.vue
│   │   │   └── scenarios/
│   │   │       ├── EcommerceScenario.vue
│   │   │       ├── ManufacturingScenario.vue
│   │   │       ├── ColdChainScenario.vue
│   │   │       ├── PortLogisticsScenario.vue
│   │   │       ├── ReverseLogisticsScenario.vue
│   │   │       └── MultiFloorScenario.vue
│   │   └── panels/
│   │       ├── ScenarioPanel.vue
│   │       └── AlertBanner.vue
│   └── styles/
│       └── tokens.css
└── tests/
    ├── unit/
    │   ├── scenario.test.ts
    │   ├── topologyShell.test.ts
    │   └── ShellScene.test.ts
    └── component/
        ├── DeviceMap2D.test.ts
        └── EcommerceScenario.test.ts
```

---

## Task 1: Vite + Vue 3 工程骨架

**Files:**
- Create: `rcs/frontend/package.json`
- Create: `rcs/frontend/tsconfig.json`
- Create: `rcs/frontend/vite.config.ts`
- Create: `rcs/frontend/index.html`
- Create: `rcs/frontend/src/main.ts`
- Create: `rcs/frontend/src/App.vue`
- Create: `rcs/frontend/src/styles/tokens.css`
- Create: `rcs/frontend/src/router/index.ts`

**Interfaces:**
- Produces: `app = createApp(...)`，router 实例，`/map` 路由到 SiteMapView

- [ ] **Step 1: 创建 `rcs/frontend/package.json`**

```json
{
  "name": "rcs-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite --port 5173",
    "build": "vue-tsc --noEmit && vite build",
    "preview": "vite preview --port 5173",
    "test": "vitest run",
    "test:watch": "vitest",
    "type-check": "vue-tsc --noEmit"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0",
    "pinia": "^2.1.7",
    "ant-design-vue": "^3.2.0",
    "@ant-design/icons-vue": "^7.0.0",
    "vue-i18n": "^9.13.0",
    "echarts": "^5.5.0",
    "three": "^0.165.0",
    "axios": "^1.7.0",
    "dayjs": "^1.11.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.2.0",
    "typescript": "^5.4.0",
    "vue-tsc": "^2.0.0",
    "vitest": "^1.6.0",
    "@vue/test-utils": "^2.4.0",
    "jsdom": "^24.0.0",
    "@types/three": "^0.165.0",
    "@types/node": "^20.0.0"
  },
  "packageManager": "pnpm@9.0.0"
}
```

- [ ] **Step 2: 创建 `rcs/frontend/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": false,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    },
    "types": ["vite/client", "node"]
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue", "tests/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

- [ ] **Step 3: 创建 `rcs/frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') }
  },
  server: {
    port: 5173,
    proxy: {
      '/api/rcs': { target: 'http://127.0.0.1:8100', changeOrigin: true },
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true }
    }
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['tests/**/*.test.ts']
  }
})
```

- [ ] **Step 4: 创建 `rcs/frontend/index.html`**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RCS Frontend v2.2</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 5: 创建 `rcs/frontend/src/styles/tokens.css`**

```css
:root {
  --color-bg: #0f172a;
  --color-surface: #1e293b;
  --color-border: #334155;
  --color-text: #f1f5f9;
  --color-text-dim: #94a3b8;
  --color-accent: #3b82f6;
  --color-warn: #f59e0b;
  --color-danger: #ef4444;
  --color-success: #10b981;
  --scenario-warm: #f59e0b;
  --scenario-cold: #3b82f6;
  --scenario-industrial: #64748b;
  --scenario-harbor: #0ea5e9;
  --scenario-warning: #ef4444;
  --scenario-neutral: #475569;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --radius-sm: 4px;
  --radius-md: 8px;
}
```

- [ ] **Step 6: 创建 `rcs/frontend/src/main.ts`**

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import App from './App.vue'
import { router } from './router'
import { i18n } from './i18n'
import './styles/tokens.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(Antd)
app.mount('#app')
```

- [ ] **Step 7: 创建 `rcs/frontend/src/App.vue`**

```vue
<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <a-config-provider>
    <RouterView />
  </a-config-provider>
</template>
```

- [ ] **Step 8: 创建 `rcs/frontend/src/router/index.ts`**

```typescript
import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import SiteMapView from '@/views/SiteMapView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/map' },
  { path: '/map', name: 'map', component: SiteMapView },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
```

- [ ] **Step 9: 创建空的 `src/views/SiteMapView.vue`（task 9 完整实现）**

```vue
<script setup lang="ts">
// Will be filled in Task 9
</script>

<template>
  <div class="site-map-placeholder">
    <h1>RCS Site Map</h1>
  </div>
</template>
```

- [ ] **Step 10: 创建空的 `src/i18n/index.ts`（task 2 填充）**

```typescript
// Placeholder, will be filled in Task 2
import { createI18n } from 'vue-i18n'
export const i18n = createI18n({ legacy: false, locale: 'zh-CN', messages: {} })
```

- [ ] **Step 11: 安装依赖**

Run:
```bash
cd rcs/frontend
corepack enable
pnpm install --no-frozen-lockfile
```
Expected: 安装成功，无 error

- [ ] **Step 12: 跑类型检查**

Run: `cd rcs/frontend && pnpm type-check`
Expected: PASS（无类型错误）

- [ ] **Step 13: Commit**

```bash
git add rcs/frontend
git commit -m "feat(rcs-frontend): scaffold Vite + Vue 3 + TS project"
```

---

## Task 2: TypeScript 类型定义（floorShell / siteGrid / scenario）

**Files:**
- Create: `rcs/frontend/src/types/floorShell.ts`
- Create: `rcs/frontend/src/types/siteGrid.ts`
- Create: `rcs/frontend/src/types/scenario.ts`
- Create: `rcs/frontend/tests/unit/types.test.ts`

**Interfaces:**
- Produces:
  - `FloorShell`, `WallSegment`, `Zone`, `Facility`, `Dock`, `Corridor`, `Marking`, `Floor`
  - `SiteGrid`, `Cell`, `CellType`
  - `ScenarioType = 'ecommerce' | 'manufacturing' | 'cold_chain' | 'port' | 'reverse_logistics' | 'multi_floor'`
  - `ScenarioConfig`

- [ ] **Step 1: 写失败的测试 `tests/unit/types.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'
import type { FloorShell, Zone } from '@/types/floorShell'
import type { SiteGrid, Cell } from '@/types/siteGrid'
import { SCENARIO_IDS } from '@/types/scenario'

describe('types', () => {
  it('SCENARIO_IDS has exactly 6 entries', () => {
    expect(SCENARIO_IDS).toHaveLength(6)
    expect(SCENARIO_IDS).toContain('ecommerce')
    expect(SCENARIO_IDS).toContain('multi_floor')
  })

  it('FloorShell accepts all v2.2 zone types', () => {
    const types: Array<Zone['type']> = [
      'flow_rack', 'high_rack', 'mezzanine', 'automated',
      'temp', 'temp_bagged', 'returns',
      'production_line', 'wip_buffer', 'parts_storage', 'staging',
      'cold_zone', 'frozen_zone', 'ambient_zone', 'loading_bay',
      'container_yard', 'customs_area',
      'returns_received', 'qc_staging', 'reshelving', 'disposal',
      'floor_1', 'floor_2', 'floor_3', 'elevator_shaft',
    ]
    expect(types.length).toBe(23)
  })

  it('SiteGrid with empty cells is valid', () => {
    const grid: SiteGrid = { bounds: { w: 50, d: 30 }, cell_size: 1.0, cells: [] }
    expect(grid.cells).toEqual([])
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/frontend && pnpm test`
Expected: FAIL with module not found

- [ ] **Step 3: 创建 `src/types/floorShell.ts`**

```typescript
export type Bounds = { w: number; d: number; h?: number }

export type WallKind = 'wall' | 'glass' | 'rack' | 'fence'

export interface WallSegment {
  id: string
  x0: number; z0: number
  x1: number; z1: number
  h: number
  kind: WallKind
}

export type ZoneType =
  | 'flow_rack' | 'high_rack' | 'mezzanine' | 'automated'
  | 'temp' | 'temp_bagged' | 'returns'
  | 'production_line' | 'wip_buffer' | 'parts_storage' | 'staging'
  | 'cold_zone' | 'frozen_zone' | 'ambient_zone' | 'loading_bay'
  | 'container_yard' | 'customs_area'
  | 'returns_received' | 'qc_staging' | 'reshelving' | 'disposal'
  | 'floor_1' | 'floor_2' | 'floor_3' | 'elevator_shaft'

export interface Zone {
  id: string
  ref: string
  type: ZoneType
  x: number; z: number
  w: number; d: number
  name?: string
  siteNodeIds?: string[]
  temperature_range?: { min: number; max: number }
  batch_tracking?: boolean
  hazard_level?: 'none' | 'low' | 'medium' | 'high'
  customs_regulated?: boolean
  current_load_pct?: number
}

export interface Facility {
  id: string
  ref: string
  type: string
  x: number; z: number
  w: number; d: number
  h: number
}

export interface Dock {
  id: string
  ref: string
  x: number; z: number
  direction: 'N' | 'S' | 'E' | 'W'
  door_w: number
}

export interface Corridor {
  id: string
  from_zone: string
  to_zone: string
  w: number
  bidirectional: boolean
}

export interface Marking {
  id: string
  kind: 'lane' | 'stop' | 'crossing' | 'work_zone' | 'evac'
  points: Array<[number, number]>
  color: string
}

export interface Floor {
  id: string
  z: number
  bounds: Bounds
  walls: WallSegment[]
  zones: Zone[]
  facilities: Facility[]
}

export interface FloorShell {
  bounds: Bounds
  walls: WallSegment[]
  zones: Zone[]
  facilities: Facility[]
  docks: Dock[]
  corridors: Corridor[]
  markings: Marking[]
  metadata: Record<string, unknown>
  floors: Floor[]
}
```

- [ ] **Step 4: 创建 `src/types/siteGrid.ts`**

```typescript
export type CellType =
  | 'free' | 'blocked' | 'preferred' | 'no_agv'
  | 'shuttle_only' | 'loading' | 'unloading'

export interface Cell {
  x: number; z: number
  type: CellType
  speed_scale: number
  note: string
}

export interface SiteGrid {
  bounds: { w: number; d: number }
  cell_size: number
  cells: Cell[]
}
```

- [ ] **Step 5: 创建 `src/types/scenario.ts`**

```typescript
import type { ZoneType } from './floorShell'

export type ScenarioType =
  | 'ecommerce'
  | 'manufacturing'
  | 'cold_chain'
  | 'port'
  | 'reverse_logistics'
  | 'multi_floor'

export const SCENARIO_IDS: ScenarioType[] = [
  'ecommerce', 'manufacturing', 'cold_chain',
  'port', 'reverse_logistics', 'multi_floor',
]

export type ScenarioTheme = 'warm' | 'cold' | 'industrial' | 'harbor' | 'warning' | 'neutral'

export type AlertType =
  | 'overstock' | 'stockout'
  | 'material_shortage' | 'line_stop'
  | 'temp_exceed' | 'humidity_exceed'
  | 'customs_hold' | 'container_stuck'
  | 'return_surge' | 'disposal_exceeded'
  | 'elevator_fault'

export interface ScenarioConfig {
  id: ScenarioType
  name: string
  zoneTypes: ZoneType[]
  theme: ScenarioTheme
  highlightColor: string
  alertTypes: AlertType[]
}

export const SCENARIO_CONFIGS: Record<ScenarioType, ScenarioConfig> = {
  ecommerce: {
    id: 'ecommerce',
    name: '电商/零售仓储',
    zoneTypes: ['flow_rack', 'high_rack', 'mezzanine', 'automated', 'temp', 'temp_bagged', 'returns', 'staging'],
    theme: 'warm',
    highlightColor: '#f59e0b',
    alertTypes: ['overstock', 'stockout'],
  },
  manufacturing: {
    id: 'manufacturing',
    name: '制造业产线',
    zoneTypes: ['production_line', 'wip_buffer', 'parts_storage', 'staging'],
    theme: 'industrial',
    highlightColor: '#64748b',
    alertTypes: ['material_shortage', 'line_stop'],
  },
  cold_chain: {
    id: 'cold_chain',
    name: '冷链/医药仓储',
    zoneTypes: ['cold_zone', 'frozen_zone', 'ambient_zone', 'loading_bay'],
    theme: 'cold',
    highlightColor: '#3b82f6',
    alertTypes: ['temp_exceed', 'humidity_exceed'],
  },
  port: {
    id: 'port',
    name: '跨境/港口物流',
    zoneTypes: ['container_yard', 'loading_bay', 'customs_area', 'staging', 'cold_zone'],
    theme: 'harbor',
    highlightColor: '#0ea5e9',
    alertTypes: ['customs_hold', 'container_stuck'],
  },
  reverse_logistics: {
    id: 'reverse_logistics',
    name: '逆向物流/退货',
    zoneTypes: ['returns_received', 'qc_staging', 'reshelving', 'disposal'],
    theme: 'warning',
    highlightColor: '#ef4444',
    alertTypes: ['return_surge', 'disposal_exceeded'],
  },
  multi_floor: {
    id: 'multi_floor',
    name: '多层/跨楼层仓储',
    zoneTypes: ['floor_1', 'floor_2', 'floor_3', 'elevator_shaft', 'staging'],
    theme: 'neutral',
    highlightColor: '#475569',
    alertTypes: ['elevator_fault'],
  },
}
```

- [ ] **Step 6: 跑测试确认通过**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（3 tests）

- [ ] **Step 7: Commit**

```bash
git add rcs/frontend/src/types rcs/frontend/tests/unit/types.test.ts
git commit -m "feat(rcs-frontend): TS types for FloorShell/SiteGrid/Scenario (23 zone types, 6 scenarios)"
```

---

## Task 3: API 客户端层（axios + 6 个 endpoint 模块）

**Files:**
- Create: `rcs/frontend/src/api/http.ts`
- Create: `rcs/frontend/src/api/topologyShell.ts`
- Create: `rcs/frontend/src/api/topologyTemplates.ts`
- Create: `rcs/frontend/src/api/orders.ts`
- Create: `rcs/frontend/tests/unit/api.test.ts`

**Interfaces:**
- Produces:
  - `http` — axios 实例，baseURL='/api/rcs'，超时 10s
  - `getShell(siteId)` / `putShell(siteId, shell)` / `listShells()`
  - `listTemplates()` / `getTemplate(scenarioId)`
  - `createOrder(req)` / `getOrder(orderId)`

- [ ] **Step 1: 写失败的测试 `tests/unit/api.test.ts`**

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { listTemplates, getTemplate } from '@/api/topologyTemplates'
import { createOrder, getOrder } from '@/api/orders'

describe('api/topologyTemplates', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('listTemplates calls /topology/templates', async () => {
    const spy = vi.fn().mockResolvedValue({ data: [{ scenario_id: 'ecommerce' }] })
    vi.spyOn(await import('@/api/http'), 'http', 'get').mockReturnValue({ get: spy } as any)

    const out = await listTemplates()
    expect(spy).toHaveBeenCalledWith('/topology/templates')
    expect(out).toEqual([{ scenario_id: 'ecommerce' }])
  })

  it('getTemplate returns full bundle', async () => {
    const spy = vi.fn().mockResolvedValue({
      data: { scenario_id: 'cold_chain', shell: { bounds: { w: 80, d: 60 } }, grid: { bounds: { w: 80, d: 60 } } },
    })
    vi.spyOn(await import('@/api/http'), 'http', 'get').mockReturnValue({ get: spy } as any)

    const out = await getTemplate('cold_chain')
    expect(spy).toHaveBeenCalledWith('/topology/templates/cold_chain')
    expect(out.scenario_id).toBe('cold_chain')
  })
})

describe('api/orders', () => {
  it('createOrder posts payload', async () => {
    const post = vi.fn().mockResolvedValue({ data: { order_id: 'ORD-X', dag: [] } })
    vi.spyOn(await import('@/api/http'), 'http', 'get').mockReturnValue({ post } as any)

    const out = await createOrder({
      scenario_id: 'ecommerce',
      items: [{ ref: 'A1', quantity: 1 }],
      priority: 5,
    })
    expect(post).toHaveBeenCalledWith('/orders', expect.objectContaining({ scenario_id: 'ecommerce' }))
    expect(out.order_id).toBe('ORD-X')
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/frontend && pnpm test`
Expected: FAIL with module not found

- [ ] **Step 3: 创建 `src/api/http.ts`**

```typescript
import axios from 'axios'

export const http = axios.create({
  baseURL: '/api/rcs',
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
})

http.interceptors.response.use(
  (r) => r,
  (err) => {
    console.error('[api]', err.response?.status, err.config?.url, err.message)
    return Promise.reject(err)
  }
)
```

- [ ] **Step 4: 创建 `src/api/topologyShell.ts`**

```typescript
import { http } from './http'
import type { FloorShell } from '@/types/floorShell'

export async function listShells(): Promise<Array<{ site_id: string; bounds: { w: number; d: number }; zone_count: number }>> {
  const r = await http.get('/topology/shell')
  return r.data
}

export async function getShell(siteId: string): Promise<FloorShell> {
  const r = await http.get(`/topology/shell/${siteId}`)
  return r.data
}

export async function putShell(siteId: string, shell: FloorShell): Promise<{ ok: boolean; warnings: string[] }> {
  const r = await http.put(`/topology/shell/${siteId}`, shell)
  return r.data
}
```

- [ ] **Step 5: 创建 `src/api/topologyTemplates.ts`**

```typescript
import { http } from './http'
import type { FloorShell } from '@/types/floorShell'
import type { SiteGrid } from '@/types/siteGrid'
import type { ScenarioType } from '@/types/scenario'

export interface TemplateInfo {
  scenario_id: string
  name: string
  bounds: { w: number; d: number }
  zone_count: number
}

export interface TemplateBundle {
  scenario_id: string
  shell: FloorShell
  grid: SiteGrid
  metadata: Record<string, unknown>
}

export async function listTemplates(): Promise<TemplateInfo[]> {
  const r = await http.get('/topology/templates')
  return r.data
}

export async function getTemplate(scenarioId: ScenarioType): Promise<TemplateBundle> {
  const r = await http.get(`/topology/templates/${scenarioId}`)
  return r.data
}
```

- [ ] **Step 6: 创建 `src/api/orders.ts`**

```typescript
import { http } from './http'

export interface OrderItem { ref: string; quantity: number }
export interface OrderCreateRequest {
  scenario_id: string
  items: OrderItem[]
  priority?: number
  deadline?: number
}
export interface OrderResponse {
  order_id: string
  status: string
  dag: Array<{ node_id: string; depends_on: string[] }>
  created_at: number
}

export async function createOrder(req: OrderCreateRequest): Promise<OrderResponse> {
  const r = await http.post('/orders', req)
  return r.data
}

export async function getOrder(orderId: string): Promise<OrderResponse> {
  const r = await http.get(`/orders/${orderId}`)
  return r.data
}
```

- [ ] **Step 7: 跑测试确认通过**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（3 tests）

- [ ] **Step 8: Commit**

```bash
git add rcs/frontend/src/api rcs/frontend/tests/unit/api.test.ts
git commit -m "feat(rcs-frontend): API client (http + topologyShell + topologyTemplates + orders)"
```

---

## Task 4: Pinia stores（scenario / floorShell / siteGrid）

**Files:**
- Create: `rcs/frontend/src/stores/floorShell.ts`
- Create: `rcs/frontend/src/stores/siteGrid.ts`
- Create: `rcs/frontend/src/stores/scenario.ts`
- Create: `rcs/frontend/tests/unit/scenario.test.ts`

**Interfaces:**
- Produces:
  - `useFloorShellStore()` — `shell: ref<FloorShell|null>`，`load(siteId)`，`save(siteId)`，`applyShell(s)`
  - `useSiteGridStore()` — `grid: ref<SiteGrid|null>`，`applyGrid(g)`
  - `useScenarioStore()` — `current: ref<ScenarioType>`，`applyTemplate(scenario)` 拉取并设置 shell + grid

- [ ] **Step 1: 写失败的测试 `tests/unit/scenario.test.ts`**

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useScenarioStore } from '@/stores/scenario'

describe('useScenarioStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('default scenario is ecommerce', () => {
    const s = useScenarioStore()
    expect(s.current).toBe('ecommerce')
  })

  it('filteredZones returns empty when shell is null', () => {
    const s = useScenarioStore()
    expect(s.filteredZones).toEqual([])
  })

  it('filteredZones returns only zones of allowed types', () => {
    const s = useScenarioStore()
    s.applyShell({
      bounds: { w: 100, d: 80 },
      walls: [], facilities: [], docks: [], corridors: [], markings: [], metadata: {}, floors: [],
      zones: [
        { id: 'z1', ref: 'A', type: 'flow_rack', x: 0, z: 0, w: 10, d: 10 },
        { id: 'z2', ref: 'B', type: 'cold_zone', x: 20, z: 0, w: 10, d: 10 },
      ],
    })
    const fz = s.filteredZones
    expect(fz.length).toBe(1)
    expect(fz[0].type).toBe('flow_rack')
  })

  it('applyTemplate sets current scenario', () => {
    const s = useScenarioStore()
    s.setCurrent('cold_chain')
    expect(s.current).toBe('cold_chain')
    expect(s.config.theme).toBe('cold')
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/frontend && pnpm test`
Expected: FAIL with module not found

- [ ] **Step 3: 创建 `src/stores/floorShell.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { FloorShell } from '@/types/floorShell'
import * as api from '@/api/topologyShell'

export const useFloorShellStore = defineStore('floorShell', () => {
  const shell = ref<FloorShell | null>(null)

  async function load(siteId: string) {
    shell.value = await api.getShell(siteId)
  }

  async function save(siteId: string) {
    if (!shell.value) throw new Error('no shell to save')
    return await api.putShell(siteId, shell.value)
  }

  function applyShell(s: FloorShell) {
    shell.value = s
  }

  return { shell, load, save, applyShell }
})
```

- [ ] **Step 4: 创建 `src/stores/siteGrid.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { SiteGrid } from '@/types/siteGrid'

export const useSiteGridStore = defineStore('siteGrid', () => {
  const grid = ref<SiteGrid | null>(null)
  function applyGrid(g: SiteGrid) { grid.value = g }
  return { grid, applyGrid }
})
```

- [ ] **Step 5: 创建 `src/stores/scenario.ts`**

```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ScenarioType } from '@/types/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import * as api from '@/api/topologyTemplates'
import { useFloorShellStore } from './floorShell'
import { useSiteGridStore } from './siteGrid'

export const useScenarioStore = defineStore('scenario', () => {
  const current = ref<ScenarioType>('ecommerce')

  const config = computed(() => SCENARIO_CONFIGS[current.value])

  const filteredZones = computed(() => {
    const shellStore = useFloorShellStore()
    const shell = shellStore.shell
    if (!shell) return []
    return shell.zones.filter((z) => config.value.zoneTypes.includes(z.type))
  })

  function setCurrent(s: ScenarioType) {
    current.value = s
  }

  async function applyTemplate(scenario: ScenarioType) {
    current.value = scenario
    const bundle = await api.getTemplate(scenario)
    useFloorShellStore().applyShell(bundle.shell)
    useSiteGridStore().applyGrid(bundle.grid)
  }

  return { current, config, filteredZones, setCurrent, applyTemplate }
})
```

- [ ] **Step 6: 跑测试确认通过**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（4 tests）

- [ ] **Step 7: Commit**

```bash
git add rcs/frontend/src/stores rcs/frontend/tests/unit/scenario.test.ts
git commit -m "feat(rcs-frontend): Pinia stores (floorShell + siteGrid + scenario)"
```

---

## Task 5: 国际化（vue-i18n 中英文）

**Files:**
- Create: `rcs/frontend/src/i18n/index.ts`
- Create: `rcs/frontend/src/i18n/zh-CN.ts`
- Create: `rcs/frontend/src/i18n/en-US.ts`
- Modify: `rcs/frontend/src/main.ts`（使用真实 i18n）

**Interfaces:**
- Produces: `i18n` 实例，locale 默认 `zh-CN`，6 个场景的中英文名

- [ ] **Step 1: 创建 `src/i18n/zh-CN.ts`**

```typescript
export default {
  app: {
    title: 'RCS 站点地图',
    loading: '加载中…',
  },
  scenario: {
    ecommerce: '电商/零售仓储',
    manufacturing: '制造业产线',
    cold_chain: '冷链/医药仓储',
    port: '跨境/港口物流',
    reverse_logistics: '逆向物流/退货',
    multi_floor: '多层/跨楼层仓储',
  },
  view: {
    mode_2d: '2D 拓扑',
    mode_3d: '3D 场景',
    import_dxf: '导入 DXF',
    export_dxf: '导出 DXF',
  },
  alerts: {
    overstock: '库存积压',
    stockout: '缺货',
    temp_exceed: '温度超限',
    customs_hold: '海关滞留',
    elevator_fault: '电梯故障',
  },
}
```

- [ ] **Step 2: 创建 `src/i18n/en-US.ts`**

```typescript
export default {
  app: {
    title: 'RCS Site Map',
    loading: 'Loading…',
  },
  scenario: {
    ecommerce: 'E-commerce / Retail Warehouse',
    manufacturing: 'Manufacturing Production Line',
    cold_chain: 'Cold-Chain / Pharma Warehouse',
    port: 'Cross-border / Port Logistics',
    reverse_logistics: 'Reverse Logistics / Returns',
    multi_floor: 'Multi-floor Warehouse',
  },
  view: {
    mode_2d: '2D Topology',
    mode_3d: '3D Scene',
    import_dxf: 'Import DXF',
    export_dxf: 'Export DXF',
  },
  alerts: {
    overstock: 'Overstock',
    stockout: 'Stockout',
    temp_exceed: 'Temperature Exceed',
    customs_hold: 'Customs Hold',
    elevator_fault: 'Elevator Fault',
  },
}
```

- [ ] **Step 3: 替换 `src/i18n/index.ts`**

```typescript
import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import enUS from './en-US'

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
  },
})
```

- [ ] **Step 4: 跑类型检查**

Run: `cd rcs/frontend && pnpm type-check`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/src/i18n
git commit -m "feat(rcs-frontend): vue-i18n (zh-CN + en-US, 6 scenarios + alerts)"
```

---

## Task 6: 2D 渲染层（DeviceMap2D + ECharts）

**Files:**
- Create: `rcs/frontend/src/components/map/DeviceMap2D.vue`
- Create: `rcs/frontend/tests/component/DeviceMap2D.test.ts`

**Interfaces:**
- Produces: `<DeviceMap2D />` — 用 ECharts 渲染 floorShell 的 walls/zones/facilities，支持 hover tooltip

- [ ] **Step 1: 写失败的测试 `tests/component/DeviceMap2D.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'
import { useFloorShellStore } from '@/stores/floorShell'

describe('DeviceMap2D', () => {
  it('renders empty state when shell is null', () => {
    setActivePinia(createPinia())
    const w = mount(DeviceMap2D)
    expect(w.find('[data-test="empty-state"]').exists()).toBe(true)
  })

  it('renders canvas when shell is present', async () => {
    setActivePinia(createPinia())
    const store = useFloorShellStore()
    store.applyShell({
      bounds: { w: 100, d: 80 },
      walls: [{ id: 'w1', x0: 0, z0: 0, x1: 50, z1: 0, h: 3, kind: 'wall' }],
      zones: [{ id: 'z1', ref: 'A1', type: 'flow_rack', x: 0, z: 0, w: 10, d: 10 }],
      facilities: [], docks: [], corridors: [], markings: [], metadata: {}, floors: [],
    })
    const w = mount(DeviceMap2D)
    expect(w.find('canvas').exists() || w.find('[data-test="map-container"]').exists()).toBe(true)
  })
})
```

- [ ] **Step 2: 跑测试确认失败**

Run: `cd rcs/frontend && pnpm test`
Expected: FAIL

- [ ] **Step 3: 创建 `src/components/map/DeviceMap2D.vue`**

```vue
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, computed } from 'vue'
import * as echarts from 'echarts/core'
import { useFloorShellStore } from '@/stores/floorShell'
import { useScenarioStore } from '@/stores/scenario'
import type { FloorShell, Zone } from '@/types/floorShell'

const container = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

const floorShellStore = useFloorShellStore()
const scenarioStore = useScenarioStore()

const allowedTypes = computed(() => scenarioStore.config.zoneTypes)

const filteredZones = computed(() => {
  const shell = floorShellStore.shell
  if (!shell) return []
  return shell.zones.filter((z) => allowedTypes.value.includes(z.type))
})

function buildOption(shell: FloorShell) {
  const { bounds } = shell
  const walls = shell.walls.map((w) => ({
    coords: [[w.x0, w.z0], [w.x1, w.z1]],
  }))
  const zones = filteredZones.value.map((z: Zone) => ({
    name: z.ref,
    value: [z.x + z.w / 2, z.z + z.d / 2, z.w, z.d, z.current_load_pct ?? 0],
    itemStyle: {
      color: scenarioStore.config.highlightColor,
      opacity: 0.4 + ((z.current_load_pct ?? 0) / 100) * 0.5,
    },
  }))

  return {
    grid: { left: 40, right: 20, top: 20, bottom: 30 },
    xAxis: { type: 'value', min: 0, max: bounds.w, name: 'X (m)' },
    yAxis: { type: 'value', min: 0, max: bounds.d, name: 'Z (m)', inverse: false },
    series: [
      { type: 'lines', data: walls, lineStyle: { width: 2, color: '#94a3b8' }, silent: true },
      {
        type: 'custom',
        renderItem: (_params: any, api: any) => {
          const [cx, , w, d] = api.value(0)
          const cz = api.value(1)
          return {
            type: 'rect',
            shape: { x: cx - w / 2, y: cz - d / 2, width: w, height: d },
            style: api.style(),
          }
        },
        data: zones,
        encode: { x: 0, y: 1 },
      },
    ],
  }
}

function render() {
  if (!container.value) return
  if (!chart) chart = echarts.init(container.value)
  const shell = floorShellStore.shell
  if (!shell) return
  chart.setOption(buildOption(shell), { notMerge: true })
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  chart?.dispose()
  chart = null
})

watch(() => floorShellStore.shell, render, { deep: true })
watch(() => scenarioStore.current, render)
</script>

<template>
  <div class="device-map-2d">
    <div v-if="!floorShellStore.shell" data-test="empty-state" class="empty-state">
      暂无可显示的地图。请选择场景或导入 DXF。
    </div>
    <div ref="container" data-test="map-container" class="map-container"></div>
  </div>
</template>

<style scoped>
.device-map-2d { width: 100%; height: 100%; min-height: 480px; position: relative; }
.empty-state {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--color-text-dim); font-size: 14px;
}
.map-container { width: 100%; height: 100%; }
</style>
```

- [ ] **Step 4: 跑测试**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（2 tests）

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/src/components/map/DeviceMap2D.vue rcs/frontend/tests/component/DeviceMap2D.test.ts
git commit -m "feat(rcs-frontend): DeviceMap2D (ECharts custom render of walls + zones)"
```

---

## Task 7: 3D 渲染层（DeviceMap3D + Three.js）

**Files:**
- Create: `rcs/frontend/src/components/map/ShellScene.ts`
- Create: `rcs/frontend/src/components/map/DeviceMap3D.vue`
- Create: `rcs/frontend/tests/component/DeviceMap3D.test.ts`

**Interfaces:**
- Produces:
  - `class ShellScene` — Three.js 场景封装（`mount(el)` / `dispose()` / `update(shell)`）
  - `<DeviceMap3D />` — 包装 ShellScene，挂载到 canvas

- [ ] **Step 1: 创建 `src/components/map/ShellScene.ts`**

```typescript
import * as THREE from 'three'

export class ShellScene {
  private renderer: THREE.WebGLRenderer
  private scene: THREE.Scene
  private camera: THREE.PerspectiveCamera
  private wallMesh: THREE.LineSegments | null = null
  private zoneMeshes: THREE.Mesh[] = []
  private animId: number | null = null

  constructor(private container: HTMLDivElement, private highlightColor: string = '#3b82f6') {
    const w = container.clientWidth
    const h = container.clientHeight

    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    this.renderer.setSize(w, h)
    this.renderer.setPixelRatio(window.devicePixelRatio)
    container.appendChild(this.renderer.domElement)

    this.scene = new THREE.Scene()
    this.scene.background = new THREE.Color(0x0f172a)

    this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 2000)
    this.camera.position.set(80, 80, 80)
    this.camera.lookAt(0, 0, 0)

    // Ground plane (receive shadow)
    const ground = new THREE.Mesh(
      new THREE.PlaneGeometry(500, 500),
      new THREE.MeshStandardMaterial({ color: 0x1e293b }),
    )
    ground.rotation.x = -Math.PI / 2
    ground.receiveShadow = true
    this.scene.add(ground)

    // Lights
    const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6)
    this.scene.add(hemi)
    const dir = new THREE.DirectionalLight(0xffffff, 0.8)
    dir.position.set(50, 100, 50)
    this.scene.add(dir)

    this.animate()
  }

  update(shell: { walls: Array<{ x0: number; z0: number; x1: number; z1: number; h: number }>; zones: Array<{ x: number; z: number; w: number; d: number }> }, bounds: { w: number; d: number }) {
    // Re-center camera
    this.camera.lookAt(bounds.w / 2, 0, bounds.d / 2)
    this.camera.position.set(bounds.w / 2 + 60, 80, bounds.d / 2 + 60)

    // Clear previous
    if (this.wallMesh) {
      this.scene.remove(this.wallMesh)
      this.wallMesh.geometry.dispose()
    }
    this.zoneMeshes.forEach((m) => {
      this.scene.remove(m)
      m.geometry.dispose()
      if (m.material instanceof THREE.Material) m.material.dispose()
    })
    this.zoneMeshes = []

    // Walls as line segments
    const points: number[] = []
    for (const w of shell.walls) {
      points.push(w.x0, 0, w.z0, w.x1, w.h, w.z1)
    }
    const geom = new THREE.BufferGeometry()
    geom.setAttribute('position', new THREE.Float32BufferAttribute(points, 3))
    const mat = new THREE.LineBasicMaterial({ color: 0x94a3b8 })
    this.wallMesh = new THREE.LineSegments(geom, mat)
    this.scene.add(this.wallMesh)

    // Zones as flat boxes
    const color = new THREE.Color(this.highlightColor)
    for (const z of shell.zones) {
      const box = new THREE.Mesh(
        new THREE.BoxGeometry(z.w, 0.1, z.d),
        new THREE.MeshStandardMaterial({ color, transparent: true, opacity: 0.5 }),
      )
      box.position.set(z.x + z.w / 2, 0.05, z.z + z.d / 2)
      this.scene.add(box)
      this.zoneMeshes.push(box)
    }
  }

  private animate = () => {
    this.animId = requestAnimationFrame(this.animate)
    this.renderer.render(this.scene, this.camera)
  }

  resize(w: number, h: number) {
    this.renderer.setSize(w, h)
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
  }

  dispose() {
    if (this.animId !== null) cancelAnimationFrame(this.animId)
    this.renderer.dispose()
    this.renderer.domElement.remove()
  }
}
```

- [ ] **Step 2: 创建 `src/components/map/DeviceMap3D.vue`**

```vue
<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { ShellScene } from './ShellScene'
import { useFloorShellStore } from '@/stores/floorShell'
import { useScenarioStore } from '@/stores/scenario'

const container = ref<HTMLDivElement | null>(null)
let scene: ShellScene | null = null

const floorShellStore = useFloorShellStore()
const scenarioStore = useScenarioStore()

onMounted(() => {
  if (!container.value) return
  scene = new ShellScene(container.value, scenarioStore.config.highlightColor)
  const shell = floorShellStore.shell
  if (shell) scene.update(shell, shell.bounds)
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  scene?.dispose()
  scene = null
})

function onResize() {
  if (!container.value || !scene) return
  scene.resize(container.value.clientWidth, container.value.clientHeight)
}

watch(
  () => floorShellStore.shell,
  (shell) => {
    if (!shell || !scene) return
    scene.update(shell, shell.bounds)
  },
  { deep: true },
)

watch(
  () => scenarioStore.current,
  () => {
    const shell = floorShellStore.shell
    if (!shell || !scene) return
    scene = new ShellScene(container.value!, scenarioStore.config.highlightColor)
    scene.update(shell, shell.bounds)
  },
)
</script>

<template>
  <div class="device-map-3d">
    <div v-if="!floorShellStore.shell" data-test="empty-state" class="empty-state">
      3D 渲染未启用 — 请先选择场景。
    </div>
    <div ref="container" data-test="three-container" class="three-container"></div>
  </div>
</template>

<style scoped>
.device-map-3d { width: 100%; height: 100%; min-height: 480px; position: relative; }
.three-container { width: 100%; height: 100%; }
.empty-state {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--color-text-dim);
}
</style>
```

- [ ] **Step 3: 写测试 `tests/component/DeviceMap3D.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import DeviceMap3D from '@/components/map/DeviceMap3D.vue'

describe('DeviceMap3D', () => {
  it('mounts without shell', () => {
    setActivePinia(createPinia())
    const w = mount(DeviceMap3D)
    expect(w.find('[data-test="three-container"]').exists()).toBe(true)
  })

  it('shows empty state when shell is null', () => {
    setActivePinia(createPinia())
    const w = mount(DeviceMap3D)
    expect(w.find('[data-test="empty-state"]').exists()).toBe(true)
  })
})
```

- [ ] **Step 4: 跑测试**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/src/components/map/ShellScene.ts rcs/frontend/src/components/map/DeviceMap3D.vue rcs/frontend/tests/component/DeviceMap3D.test.ts
git commit -m "feat(rcs-frontend): DeviceMap3D (Three.js ShellScene — walls + zones)"
```

---

## Task 8: 场景组件 — EcommerceScenario

**Files:**
- Create: `rcs/frontend/src/components/map/scenarios/EcommerceScenario.vue`
- Create: `rcs/frontend/src/components/map/scenarios/ManufacturingScenario.vue`
- Create: `rcs/frontend/src/components/map/scenarios/ColdChainScenario.vue`
- Create: `rcs/frontend/tests/component/EcommerceScenario.test.ts`

**Interfaces:**
- Produces: 3 个场景组件的基线模式（panel + alert hooks）

- [ ] **Step 1: 创建 `EcommerceScenario.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'

const scenarioStore = useScenarioStore()
const config = computed(() => SCENARIO_CONFIGS.ecommerce)

const stockoutZones = computed(() => {
  const shell = scenarioStore.filteredZones
  return shell.filter((z) => (z.current_load_pct ?? 0) < 10)
})
const overstockZones = computed(() => {
  const shell = scenarioStore.filteredZones
  return shell.filter((z) => (z.current_load_pct ?? 0) > 90)
})
</script>

<template>
  <div class="scenario-panel">
    <h3>{{ config.name }}</h3>
    <p class="theme">主题：暖色调（{{ config.highlightColor }}）</p>

    <section class="metrics">
      <div class="metric">
        <span class="label">SKU 总数</span>
        <span class="value">{{ scenarioStore.filteredZones.length }}</span>
      </div>
      <div class="metric">
        <span class="label">缺货告警</span>
        <span class="value danger">{{ stockoutZones.length }}</span>
      </div>
      <div class="metric">
        <span class="label">积压告警</span>
        <span class="value warn">{{ overstockZones.length }}</span>
      </div>
    </section>

    <section class="alerts" v-if="stockoutZones.length + overstockZones.length > 0">
      <h4>告警</h4>
      <ul>
        <li v-for="z in stockoutZones" :key="z.id" class="alert danger">
          {{ z.ref }} 缺货（填充 {{ z.current_load_pct }}%）
        </li>
        <li v-for="z in overstockZones" :key="z.id" class="alert warn">
          {{ z.ref }} 积压（填充 {{ z.current_load_pct }}%）
        </li>
      </ul>
    </section>

    <DeviceMap2D />
  </div>
</template>

<style scoped>
.scenario-panel { padding: var(--space-4); }
.metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-2); }
.metric { background: var(--color-surface); padding: var(--space-2); border-radius: var(--radius-sm); }
.metric .value { display: block; font-size: 24px; font-weight: bold; }
.metric .value.danger { color: var(--color-danger); }
.metric .value.warn { color: var(--color-warn); }
.alerts { margin-top: var(--space-4); }
.alert { padding: var(--space-2); margin: var(--space-1) 0; border-left: 3px solid; }
.alert.danger { border-color: var(--color-danger); }
.alert.warn { border-color: var(--color-warn); }
</style>
```

- [ ] **Step 2: 创建 `ManufacturingScenario.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'

const scenarioStore = useScenarioStore()
const config = computed(() => SCENARIO_CONFIGS.manufacturing)

const productionLines = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'production_line')
)
const wipBuffers = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'wip_buffer')
)
</script>

<template>
  <div class="scenario-panel">
    <h3>{{ config.name }}</h3>
    <p class="theme">主题：工业（节拍驱动）</p>

    <section class="metrics">
      <div class="metric">
        <span class="label">产线数</span>
        <span class="value">{{ productionLines.length }}</span>
      </div>
      <div class="metric">
        <span class="label">WIP 缓冲区</span>
        <span class="value">{{ wipBuffers.length }}</span>
      </div>
    </section>

    <DeviceMap2D />
  </div>
</template>

<style scoped>
.scenario-panel { padding: var(--space-4); }
.metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-2); }
.metric { background: var(--color-surface); padding: var(--space-2); border-radius: var(--radius-sm); }
.metric .value { display: block; font-size: 24px; font-weight: bold; }
</style>
```

- [ ] **Step 3: 创建 `ColdChainScenario.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'

const scenarioStore = useScenarioStore()
const config = computed(() => SCENARIO_CONFIGS.cold_chain)

const frozenZones = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'frozen_zone')
)
const coldZones = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'cold_zone')
)
const ambientZones = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'ambient_zone')
)
</script>

<template>
  <div class="scenario-panel">
    <h3>{{ config.name }}</h3>
    <p class="theme">主题：冷色调（温度监控）</p>

    <section class="zones-summary">
      <div class="zone-row frozen">
        <span class="dot"></span> 冷冻区 ({{ frozenZones.length }})
      </div>
      <div class="zone-row cold">
        <span class="dot"></span> 冷藏区 ({{ coldZones.length }})
      </div>
      <div class="zone-row ambient">
        <span class="dot"></span> 常温区 ({{ ambientZones.length }})
      </div>
    </section>

    <DeviceMap2D />
  </div>
</template>

<style scoped>
.scenario-panel { padding: var(--space-4); }
.zones-summary { display: grid; gap: var(--space-2); margin: var(--space-3) 0; }
.zone-row { display: flex; align-items: center; gap: var(--space-2); padding: var(--space-2); background: var(--color-surface); border-radius: var(--radius-sm); }
.dot { width: 12px; height: 12px; border-radius: 50%; }
.zone-row.frozen .dot { background: #1e40af; }
.zone-row.cold .dot { background: #3b82f6; }
.zone-row.ambient .dot { background: #fbbf24; }
</style>
```

- [ ] **Step 4: 写测试 `tests/component/EcommerceScenario.test.ts`**

```typescript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import EcommerceScenario from '@/components/map/scenarios/EcommerceScenario.vue'
import { useScenarioStore } from '@/stores/scenario'

describe('EcommerceScenario', () => {
  it('renders scenario title', () => {
    setActivePinia(createPinia())
    const w = mount(EcommerceScenario)
    expect(w.text()).toContain('电商')
  })

  it('shows stockout alert when zone load < 10%', () => {
    setActivePinia(createPinia())
    const store = useScenarioStore()
    store.applyShell({
      bounds: { w: 50, d: 30 },
      walls: [], facilities: [], docks: [], corridors: [], markings: [], metadata: {}, floors: [],
      zones: [
        { id: 'z1', ref: 'A1', type: 'flow_rack', x: 0, z: 0, w: 5, d: 5, current_load_pct: 5 },
      ],
    })
    const w = mount(EcommerceScenario)
    expect(w.text()).toContain('缺货')
    expect(w.text()).toContain('A1')
  })
})
```

- [ ] **Step 5: 跑测试**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（2 tests for ecommerce）

- [ ] **Step 6: Commit**

```bash
git add rcs/frontend/src/components/map/scenarios/EcommerceScenario.vue rcs/frontend/src/components/map/scenarios/ManufacturingScenario.vue rcs/frontend/src/components/map/scenarios/ColdChainScenario.vue rcs/frontend/tests/component/EcommerceScenario.test.ts
git commit -m "feat(rcs-frontend): 3 scenario components (Ecommerce/Manufacturing/ColdChain)"
```

---

## Task 9: 场景组件 — PortLogistics + ReverseLogistics + MultiFloor

**Files:**
- Create: `rcs/frontend/src/components/map/scenarios/PortLogisticsScenario.vue`
- Create: `rcs/frontend/src/components/map/scenarios/ReverseLogisticsScenario.vue`
- Create: `rcs/frontend/src/components/map/scenarios/MultiFloorScenario.vue`
- Append to: `rcs/frontend/tests/component/EcommerceScenario.test.ts`

- [ ] **Step 1: 创建 `PortLogisticsScenario.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'

const scenarioStore = useScenarioStore()
const config = computed(() => SCENARIO_CONFIGS.port)

const containerYards = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'container_yard')
)
const customsAreas = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'customs_area')
)
</script>

<template>
  <div class="scenario-panel">
    <h3>{{ config.name }}</h3>
    <p class="theme">主题：海港（堆场 + 海关）</p>

    <section class="metrics">
      <div class="metric">
        <span class="label">集装箱堆场</span>
        <span class="value">{{ containerYards.length }}</span>
      </div>
      <div class="metric">
        <span class="label">海关监管区</span>
        <span class="value warn">{{ customsAreas.length }}</span>
      </div>
    </section>

    <DeviceMap2D />
  </div>
</template>

<style scoped>
.scenario-panel { padding: var(--space-4); }
.metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-2); }
.metric { background: var(--color-surface); padding: var(--space-2); border-radius: var(--radius-sm); }
.metric .value { display: block; font-size: 24px; font-weight: bold; }
.metric .value.warn { color: var(--color-warn); }
</style>
```

- [ ] **Step 2: 创建 `ReverseLogisticsScenario.vue`**

```vue
<script setup lang="ts">
import { computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'

const scenarioStore = useScenarioStore()
const config = computed(() => SCENARIO_CONFIGS.reverse_logistics)

const returnsReceived = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'returns_received')
)
const disposal = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'disposal')
)
</script>

<template>
  <div class="scenario-panel">
    <h3>{{ config.name }}</h3>
    <p class="theme">主题：警告（决策流程）</p>

    <section class="flow">
      <div class="flow-stage">退货接收 ({{ returnsReceived.length }})</div>
      <div class="flow-arrow">→</div>
      <div class="flow-stage">质检分拣</div>
      <div class="flow-arrow">→</div>
      <div class="flow-stage">再上架 / 报废 ({{ disposal.length }})</div>
    </section>

    <DeviceMap2D />
  </div>
</template>

<style scoped>
.scenario-panel { padding: var(--space-4); }
.flow { display: flex; align-items: center; gap: var(--space-2); margin: var(--space-3) 0; }
.flow-stage { background: var(--color-surface); padding: var(--space-2) var(--space-3); border-radius: var(--radius-sm); }
.flow-arrow { color: var(--color-warn); }
</style>
```

- [ ] **Step 3: 创建 `MultiFloorScenario.vue`**

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_CONFIGS } from '@/types/scenario'
import DeviceMap2D from '@/components/map/DeviceMap2D.vue'

const scenarioStore = useScenarioStore()
const config = computed(() => SCENARIO_CONFIGS.multi_floor)

const activeFloor = ref<'all' | 'floor_1' | 'floor_2' | 'floor_3'>('all')

const elevators = computed(() =>
  scenarioStore.filteredZones.filter((z) => z.type === 'elevator_shaft')
)

const visibleZones = computed(() => {
  if (activeFloor.value === 'all') return scenarioStore.filteredZones
  return scenarioStore.filteredZones.filter((z) => z.type === activeFloor.value || z.type === 'elevator_shaft')
})
</script>

<template>
  <div class="scenario-panel">
    <h3>{{ config.name }}</h3>
    <p class="theme">主题：中性（跨楼层）</p>

    <section class="floor-tabs">
      <button
        v-for="f in ['all', 'floor_1', 'floor_2', 'floor_3'] as const"
        :key="f"
        :class="['tab', { active: activeFloor === f }]"
        @click="activeFloor = f"
      >
        {{ f === 'all' ? '全部' : `${f.replace('floor_', '')}F` }}
      </button>
    </section>

    <section class="metrics">
      <div class="metric">
        <span class="label">电梯数</span>
        <span class="value">{{ elevators.length }}</span>
      </div>
      <div class="metric">
        <span class="label">可见区</span>
        <span class="value">{{ visibleZones.length }}</span>
      </div>
    </section>

    <DeviceMap2D />
  </div>
</template>

<style scoped>
.scenario-panel { padding: var(--space-4); }
.floor-tabs { display: flex; gap: var(--space-1); margin: var(--space-3) 0; }
.tab { background: var(--color-surface); border: 1px solid var(--color-border); color: var(--color-text); padding: var(--space-1) var(--space-3); border-radius: var(--radius-sm); cursor: pointer; }
.tab.active { background: var(--color-accent); }
.metrics { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-2); }
.metric { background: var(--color-surface); padding: var(--space-2); border-radius: var(--radius-sm); }
.metric .value { display: block; font-size: 24px; font-weight: bold; }
</style>
```

- [ ] **Step 4: 追加测试**

```typescript
// Append to tests/component/EcommerceScenario.test.ts
import PortLogisticsScenario from '@/components/map/scenarios/PortLogisticsScenario.vue'
import ReverseLogisticsScenario from '@/components/map/scenarios/ReverseLogisticsScenario.vue'
import MultiFloorScenario from '@/components/map/scenarios/MultiFloorScenario.vue'

describe('PortLogisticsScenario', () => {
  it('renders title', () => {
    setActivePinia(createPinia())
    const w = mount(PortLogisticsScenario)
    expect(w.text()).toContain('港口')
  })
})

describe('ReverseLogisticsScenario', () => {
  it('shows flow stages', () => {
    setActivePinia(createPinia())
    const w = mount(ReverseLogisticsScenario)
    expect(w.text()).toContain('退货接收')
    expect(w.text()).toContain('质检')
  })
})

describe('MultiFloorScenario', () => {
  it('has floor tabs', () => {
    setActivePinia(createPinia())
    const w = mount(MultiFloorScenario)
    expect(w.findAll('.tab')).toHaveLength(4)
  })
})
```

- [ ] **Step 5: 跑测试**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（2 + 3 = 5 new tests）

- [ ] **Step 6: Commit**

```bash
git add rcs/frontend/src/components/map/scenarios rcs/frontend/tests/component/EcommerceScenario.test.ts
git commit -m "feat(rcs-frontend): 3 more scenario components (Port/Reverse/MultiFloor)"
```

---

## Task 10: 主视图 SiteMapView + 场景切换

**Files:**
- Modify: `rcs/frontend/src/views/SiteMapView.vue`

**Interfaces:**
- Produces: 完整的 SiteMapView — 顶部工具栏（场景选择 + 2D/3D 切换 + DXF 导入）、主视图区、侧边属性面板

- [ ] **Step 1: 替换 `src/views/SiteMapView.vue`**

```vue
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useScenarioStore } from '@/stores/scenario'
import { SCENARIO_IDS, type ScenarioType } from '@/types/scenario'
import { useI18n } from 'vue-i18n'
import DeviceMap3D from '@/components/map/DeviceMap3D.vue'
import EcommerceScenario from '@/components/map/scenarios/EcommerceScenario.vue'
import ManufacturingScenario from '@/components/map/scenarios/ManufacturingScenario.vue'
import ColdChainScenario from '@/components/map/scenarios/ColdChainScenario.vue'
import PortLogisticsScenario from '@/components/map/scenarios/PortLogisticsScenario.vue'
import ReverseLogisticsScenario from '@/components/map/scenarios/ReverseLogisticsScenario.vue'
import MultiFloorScenario from '@/components/map/scenarios/MultiFloorScenario.vue'

const { t } = useI18n()
const scenarioStore = useScenarioStore()
const viewMode = ref<'2d' | '3d'>('2d')

const scenarioComponents = {
  ecommerce: EcommerceScenario,
  manufacturing: ManufacturingScenario,
  cold_chain: ColdChainScenario,
  port: PortLogisticsScenario,
  reverse_logistics: ReverseLogisticsScenario,
  multi_floor: MultiFloorScenario,
} as const

const activeScenarioComponent = computed(() => scenarioComponents[scenarioStore.current])

onMounted(async () => {
  // Apply default template on first load
  await scenarioStore.applyTemplate('ecommerce')
})

async function onScenarioChange(s: ScenarioType) {
  await scenarioStore.applyTemplate(s)
}
</script>

<template>
  <div class="site-map-view">
    <header class="toolbar">
      <h1>{{ t('app.title') }}</h1>
      <a-select
        :value="scenarioStore.current"
        @change="onScenarioChange"
        style="width: 200px"
        aria-label="选择场景"
      >
        <a-select-option v-for="s in SCENARIO_IDS" :key="s" :value="s">
          {{ t(`scenario.${s}`) }}
        </a-select-option>
      </a-select>

      <a-radio-group v-model="viewMode" aria-label="视图模式">
        <a-radio-button value="2d">{{ t('view.mode_2d') }}</a-radio-button>
        <a-radio-button value="3d">{{ t('view.mode_3d') }}</a-radio-button>
      </a-radio-group>
    </header>

    <main class="view-container">
      <component :is="activeScenarioComponent" v-if="viewMode === '2d'" />
      <DeviceMap3D v-else />
    </main>

    <aside class="property-panel" v-if="viewMode === '3d'">
      <h3>3D 属性</h3>
      <p>当前场景：{{ t(`scenario.${scenarioStore.current}`) }}</p>
      <p>主题色：<span :style="{ color: scenarioStore.config.highlightColor }">●</span></p>
    </aside>
  </div>
</template>

<style scoped>
.site-map-view {
  display: grid;
  grid-template-rows: 60px 1fr;
  grid-template-columns: 1fr 280px;
  grid-template-areas: 'toolbar toolbar' 'main aside';
  height: 100vh;
}
.toolbar {
  grid-area: toolbar;
  display: flex; align-items: center; gap: var(--space-3);
  background: var(--color-surface);
  padding: 0 var(--space-4);
  border-bottom: 1px solid var(--color-border);
}
.toolbar h1 { margin: 0; font-size: 18px; }
.view-container {
  grid-area: main;
  overflow: auto;
}
.property-panel {
  grid-area: aside;
  background: var(--color-surface);
  padding: var(--space-4);
  border-left: 1px solid var(--color-border);
}
</style>
```

- [ ] **Step 2: 跑类型检查**

Run: `cd rcs/frontend && pnpm type-check`
Expected: PASS

- [ ] **Step 3: 跑所有测试**

Run: `cd rcs/frontend && pnpm test`
Expected: PASS（所有 unit + component tests）

- [ ] **Step 4: Commit**

```bash
git add rcs/frontend/src/views/SiteMapView.vue
git commit -m "feat(rcs-frontend): SiteMapView with scenario switcher + 2D/3D toggle + side panel"
```

---

## Task 11: Dockerfile + nginx.conf + docker-compose 集成

**Files:**
- Create: `rcs/frontend/Dockerfile`
- Create: `rcs/frontend/nginx.conf`
- Modify: `deploy/docker-compose.yml`

- [ ] **Step 1: 创建 `rcs/frontend/Dockerfile`**

```dockerfile
# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder
WORKDIR /app
RUN corepack enable
COPY rcs/frontend/package.json rcs/frontend/pnpm-lock.yaml* ./
RUN pnpm install --no-frozen-lockfile
COPY rcs/frontend/ ./
RUN pnpm build

FROM nginx:1.25-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY rcs/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1
CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 2: 创建 `rcs/frontend/nginx.conf`**

```nginx
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  # SPA fallback
  location / {
    try_files $uri $uri/ /index.html;
  }

  # Proxy /api → rcs-backend container
  location /api/rcs/ {
    proxy_pass http://rcs-backend:8100;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 60s;
  }

  # Proxy /api (non-rcs) → simulation-backend
  location /api/ {
    proxy_pass http://simulation-backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }

  # WebSocket proxy
  location /ws/ {
    proxy_pass http://simulation-backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

- [ ] **Step 3: 在 `deploy/docker-compose.yml` 末尾追加**

```yaml
  rcs-frontend:
    build:
      context: .
      dockerfile: rcs/frontend/Dockerfile
    container_name: rcs-frontend
    ports:
      - "5173:80"
    depends_on:
      - rcs-backend
      - simulation-backend
    restart: unless-stopped
```

- [ ] **Step 4: 验证 docker-compose 语法**

Run: `docker compose -f deploy/docker-compose.yml config --quiet 2>&1 | head -20`
Expected: 无错误

- [ ] **Step 5: Commit**

```bash
git add rcs/frontend/Dockerfile rcs/frontend/nginx.conf deploy/docker-compose.yml
git commit -m "feat(rcs-frontend): Docker + nginx proxy (api/rcs→rcs-backend, api→simulation-backend) + compose"
```

---

## Task 12: README + 收尾

**Files:**
- Create: `rcs/frontend/README.md`

- [ ] **Step 1: 创建 `rcs/frontend/README.md`**

```markdown
# rcs/frontend

RCS 独立前端工程（Vite + Vue 3 + TypeScript）。

## 开发

```bash
cd rcs/frontend
corepack enable
pnpm install
pnpm dev          # http://localhost:5173
pnpm test
pnpm build
```

## 6 个场景

| 场景 ID | 主题色 | 关键交互 |
|---------|-------|---------|
| `ecommerce` | #f59e0b | 库存热力图 / 拣货路径 / 缺货积压告警 |
| `manufacturing` | #64748b | 产线节拍 / WIP 状态 / 物料配送 |
| `cold_chain` | #3b82f6 | 温湿度监控 / 批次追踪 / 温区颜色 |
| `port` | #0ea5e9 | 堆场布局 / 海关监管 / 多式联运 |
| `reverse_logistics` | #ef4444 | 退货量趋势 / 质检决策 / 再上架比例 |
| `multi_floor` | #475569 | 楼层切换 / 电梯联动 / 跨层路径 |

## 后端代理

开发：`vite.config.ts` 中 `/api/rcs → :8100`，`/api → :8000`

生产：`nginx.conf` 代理 `rcs-backend:8100` 与 `simulation-backend:8000`

## 目录结构

- `src/views/` — 主视图
- `src/components/map/` — 2D/3D 渲染 + 6 场景组件
- `src/stores/` — Pinia stores
- `src/types/` — TypeScript 类型
- `src/api/` — 后端 HTTP 客户端
- `src/i18n/` — vue-i18n 国际化
```

- [ ] **Step 2: 跑所有测试**

Run: `cd rcs/frontend && pnpm test && pnpm type-check && pnpm build`
Expected: 全部通过，dist/ 生成

- [ ] **Step 3: Commit**

```bash
git add rcs/frontend/README.md
git commit -m "docs(rcs-frontend): README with dev instructions and 6-scenario matrix"
```

---

## Self-Review Checklist

✅ 12 个明确任务，每个独立可测试
✅ TDD：每个 task 都是「写测试 → 跑 → 实现 → 验证 → commit」
✅ 不破坏 Global Constraints（不修改 rcs/backend/、rcs/rcs/、simulation/、docs/）
✅ 接口契约逐任务声明（`Consumes` / `Produces`）
✅ 6 场景组件完整（spec §13.5）
✅ 23 Zone 类型覆盖（spec §13.3.2）
✅ 2D + 3D 双视图（ECharts + Three.js）
✅ Pinia scenario store（spec §13.3.3）
✅ vue-i18n 中英文（Global Constraint）
✅ Docker + nginx proxy 集成（spec §13.6）
✅ DRY / YAGNI / TDD / 频繁 commit

**已知局限**：
- Task 6/7 渲染层当前未做设备动画（AGV/AMR 移动轨迹），留给后续任务
- Task 8/9 场景组件的告警数据当前使用 mock `current_load_pct`，未来对接 simulation/backend 实时数据
- Task 11 nginx proxy 假设后端服务已启动并加入同一 docker network；本地 dev 仍用 vite proxy

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-23-rcs-frontend-v2-implementation.md`. Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**