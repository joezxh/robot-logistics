# Task 6 Brief — useSceneAPI composable

## Project Context

工程 `d:\projects\robot-logic\` Top 3 仿真模块前端。Task 5 完成 Vue Router（HEAD = `e734c47`）。Task 6 是 composable 层，封装对 `/api/scenes/*` 的 HTTP 调用。

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\composables\useSceneAPI.ts`

## Requirements

### Step 1: 创建文件（verbatim from plan）

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

### Step 2: 类型检查

```bash
cd "d:/projects/robot-logic/simulation/frontend"
npx vue-tsc --noEmit
```

期望：0 new errors（pre-existing WarehouseScene.vue:122 错误仍可存在，不影响）。

### Step 3: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/composables/useSceneAPI.ts
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add useSceneAPI composable"
```

## Acceptance Checklist

- [ ] `src/scenes/composables/useSceneAPI.ts` 创建
- [ ] 文件 verbatim 与 brief 一致
- [ ] 导出 `ScenePreset` / `SceneKPI` 接口
- [ ] 导出 `useSceneAPI()` 工厂函数
- [ ] 返回 5 个键：`currentScene` / `list` / `load` / `getCurrent` / `getKPI`
- [ ] `load` 成功后设置 `currentScene.value = name`
- [ ] `npx vue-tsc --noEmit` 0 new errors
- [ ] 仅 commit 这 1 个文件

## Global Constraints

- Vue 3 Composition API + `<script setup>` 风格
- TypeScript strict 模式（与 tsconfig.json 一致）
- 不要写单元测试（Task 16 处理）
- 不要修改其他文件

## Report Contract

写入 `d:\projects\robot-logic\.superpowers\sdd\task-6-report.md`，含：
1. 状态
2. commit hash（7 位）
3. Step 2 输出
4. Acceptance checklist 勾选
5. concerns

返回仅含：状态 + commit + 一行测试摘要 + concerns。