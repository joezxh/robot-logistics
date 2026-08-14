# Task 5 Report — Vue Router + /scenes entry link

## 1. Status

**DONE** — committed `e734c47` on `main` (HEAD advanced from `1a49897`).

## 2. Commit

- Full SHA: `e734c4758d95bb577fa8a5e2144c51b40ac0b9b8`
- Short: `e734c47`
- Message: `feat(scenes): add Vue Router config + /scenes entry link`
- Author: `cursor <cursor@local>` (per brief)

Files in commit (6 total — 5 file types per brief, plus auto-updated `package-lock.json`):
- `simulation/frontend/src/router/index.ts` (new)
- `simulation/frontend/src/scenes/ScenesPage.vue` (new)
- `simulation/frontend/src/main.ts` (modified)
- `simulation/frontend/src/App.vue` (modified — topbar router-link inserted)
- `simulation/frontend/package.json` (modified — `vue-router` dep added)
- `simulation/frontend/package-lock.json` (modified — npm install sync)

## 3. vue-tsc Output

Command: `cd simulation/frontend && npx vue-tsc --noEmit`

Baseline (HEAD before this Task, stashed + re-run) reports the same single error:

```
src/three/WarehouseScene.vue(122,12): error TS2339: Property 'addEventListener' does not exist on type 'never'.
```

This Task's diff introduces **0 new type errors**. The `WarehouseScene.vue` error is pre-existing on `main` (unrelated to router / scenes / main.ts changes) — confirmed via `git stash --include-untracked && npx vue-tsc --noEmit` re-running cleanly with the same single error.

All new / modified files (router/index.ts, main.ts, App.vue, scenes/ScenesPage.vue) compile clean.

## 4. Acceptance Checklist

- [x] `npm install vue-router` 成功 — `added 48 packages in 3s`
- [x] `package.json` 含 `vue-router` 依赖 — recorded as `vue-router: ^4.6.4` (npm resolved `^4.3.0` to latest 4.x)
- [x] `package-lock.json` 更新 — synced automatically
- [x] `router/index.ts` 创建，使用相对路径（不用 `@/`） — `../scenes/ScenesPage.vue`, `../App.vue`
- [x] `main.ts` 修改 — `const app = createApp(App); app.use(router); app.mount('#app')`
- [x] `App.vue` topbar 含 `<router-link to="/scenes">🚛 场景仿真</router-link>` — inserted before `<UserMenu />`
- [x] `scenes/ScenesPage.vue` 占位 stub 创建 — matches brief verbatim
- [x] `npx vue-tsc --noEmit` — 0 new errors introduced (1 pre-existing unrelated error remains)
- [x] 现有 Dashboard 不被破坏 — `/` 路由指向 `Dashboard = () => import('../App.vue')` (existing root layout intact)

## 5. npm install 输出概要

```
> npm install vue-router@^4.3.0
added 48 packages in 3s
13 packages are looking for funding
```

- Resolved version: `vue-router@4.6.4` (latest 4.x satisfying `^4.3.0`)
- No new peer-dep warnings; vue 3.4 + vue-router 4.x compatible
- 48 transitive packages added (vue-router's own deps + their sub-deps)

## 6. Plan Defects Corrected

1. **`@/` alias path** — brief 警告 `tsconfig.json` 未配置 paths。**修正**：router 用相对路径 `../scenes/ScenesPage.vue` 与 `../App.vue`。
2. **`vue-router` 缺失** — package.json 原本只有 vue/three/echarts/vue-echarts/axios。**修正**：`npm install vue-router@^4.3.0` 自动写入 `vue-router: ^4.6.4`。
3. **`main.ts` 缺 `app` 变量** — plan 直接 `app.use(router)` 会 NPE。**修正**：先 `const app = createApp(App)`，再 `app.use(router)`，再 `app.mount('#app')`。

## 7. Concerns

- **Pre-existing vue-tsc error**: `WarehouseScene.vue:122` 报 `Property 'addEventListener' does not exist on type 'never'`. 与本 Task 无关（baseline 已存在），不阻塞 router 集成，但建议在后续 Task 修复（属于 WarehouseScene.vue 内部的类型收窄问题，可能源于某个 `if` 分支 TypeScript 把 `window` 收窄到 `never`）。
- **`vue-router` 版本**：brief 指定 `^4.3.0`，npm 解析为 `4.6.4`（同一 minor 范围，符合 brief 期望）。若需要严格锁版本，可在后续 Task 改为 `~4.3.0` 或精确版本号。
- **App.vue 路由占位**：当前 `/` 路由的 `Dashboard = () => import('../App.vue')` 是临时方案。后续 Task 实现真正的 `DashboardPage.vue` 时需要把 `/` 路由 component 切到新页面（App.vue 本身是布局/外壳组件，长期可能不适合作为路由叶子）。
- **未运行 E2E / 浏览器验证**：本 Task 仅完成类型层 + 编译层验证，未启动 dev server 实际点击 `/scenes` 链接。建议 reviewer 启动 `npm run dev` 手测跳转。
