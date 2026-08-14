# Task 5 Brief — Vue Router + /scenes entry link

## Project Context

工程 `d:\projects\robot-logic\` Top 3 仿真模块。后端 4 个 Task 已完成（HEAD = `1a49897`）。本 Task 起进入前端实现。

## Plan Defects to Correct

1. **路径别名 `@/` 未配置**：`tsconfig.json` 没有 `compilerOptions.paths` 别名，plan 中 `import('@/scenes/ScenesPage.vue')` **不能**解析。**修正**：用相对路径 `import('@/scenes/...')` → `import('./scenes/ScenesPage.vue')` 等。

2. **`vue-router` 不在依赖中**：`package.json` 当前只有 vue/three/echarts/vue-echarts/axios。**修正**：需先 `npm install vue-router` 才能 import。

3. **`main.ts` 当前无 `app` 变量**：plan 中 `import { router } from './router'; app.use(router)` 失败。**修正**：先 `const app = createApp(App)`，再 `app.use(router)`。

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\router\index.ts`
- **Modify**: `d:\projects\robot-logic\simulation\frontend\src\main.ts`
- **Modify**: `d:\projects\robot-logic\simulation\frontend\src\App.vue`（在 topbar 区域）
- **Modify**: `d:\projects\robot-logic\simulation\frontend\package.json`（自动由 npm install 写入）
- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\ScenesPage.vue`（占位 stub，否则 router 动态 import 解析报错）

## Requirements

### Step 1: npm install vue-router

```bash
cd "d:/projects/robot-logic/simulation/frontend"
npm install vue-router@^4.3.0
```

**注意**：vue 3.4 对应 vue-router 4.x。`vue-router@^4.3.0` 是合理版本。

### Step 2: 创建 `router/index.ts`

完整内容（verbatim，**注意用相对路径**）：

```typescript
import { createRouter, createWebHistory } from 'vue-router'

const ScenesPage = () => import('../scenes/ScenesPage.vue')
const Dashboard = () => import('../App.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/scenes', name: 'scenes', component: ScenesPage },
  ],
})
```

### Step 3: 修改 `main.ts`

将整个文件替换为：

```typescript
import { createApp } from 'vue'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(router)
app.mount('#app')
```

### Step 4: 修改 `App.vue` 增加 /scenes 入口链接

在 `<header class="topbar">` 区域（`UserMenu` 之前）插入 router-link：

```html
<router-link to="/scenes" class="iconbtn" title="场景仿真">🚛 场景仿真</router-link>
```

**不要**用 `class="iconbtn"` 是为了让 `<router-link>` 与现有 `<button class="iconbtn">` 视觉一致（全局 CSS 已定义 `.iconbtn` 样式）。

### Step 5: 创建 ScenesPage.vue 占位 stub

`src/scenes/ScenesPage.vue` 必须先创建（最小 stub），否则 router 动态 import 虽不会阻塞 type check，但 vue-tsc 可能报错 "Cannot find module"。

最小 stub：

```vue
<template>
  <div class="scenes-placeholder">
    <h1>场景仿真</h1>
    <p>场景组件待 Task 11 实现。</p>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.scenes-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background: var(--bg-app);
  color: var(--fg);
}
.scenes-placeholder h1 {
  font-size: 18px;
  margin-bottom: 8px;
}
</style>
```

### Step 6: 类型检查

```bash
cd "d:/projects/robot-logic/simulation/frontend"
npx vue-tsc --noEmit
```

期望：0 errors（如果出现 "Cannot find module 'vue-router'"，说明 Step 1 npm install 失败，需重试）。

### Step 7: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/router/index.ts
git add simulation/frontend/src/main.ts
git add simulation/frontend/src/App.vue
git add simulation/frontend/src/scenes/ScenesPage.vue
git add simulation/frontend/package.json
git add simulation/frontend/package-lock.json
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add Vue Router config + /scenes entry link"
```

## Acceptance Checklist

- [ ] `npm install vue-router` 成功
- [ ] `package.json` 含 `vue-router` 依赖（自动写入）
- [ ] `package-lock.json` 更新
- [ ] `router/index.ts` 创建，使用相对路径（不用 `@/`）
- [ ] `main.ts` 修改：`const app = createApp(App); app.use(router); app.mount('#app')`
- [ ] `App.vue` topbar 含 `<router-link to="/scenes">🚛 场景仿真</router-link>`
- [ ] `scenes/ScenesPage.vue` 占位 stub 创建
- [ ] `npx vue-tsc --noEmit` 返回 0 errors
- [ ] 现有 Dashboard 不被破坏（`/` 路由仍指向 App.vue）

## Global Constraints

- 使用相对路径（不用 `@/` 别名，因 tsconfig 未配置）
- vue-router 4.x（与 vue 3.4 兼容）
- 不引入新的 npm 包（仅 vue-router）
- 不要修改 tsconfig.json（避免影响其他 Task 的路径策略）
- 现有 Vue/Vite 配置不修改（vue / three / echarts / axios 不变）

## Report Contract

写入 `d:\projects\robot-logic\.superpowers\sdd\task-5-report.md`，含：
1. 状态
2. commit hash（7 位）
3. `npx vue-tsc --noEmit` 输出（成功或报错）
4. acceptance checklist 勾选
5. npm install 输出概要（如版本）
6. concerns

返回仅含：状态 + commit + 一行测试结果 + concerns。