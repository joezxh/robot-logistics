# Plan Gap: Dashboard Layout Split

## Issue

plan 的 Task 5（Vue Router）将 `/` 路由的 component 设为 `Dashboard = () => import('../App.vue')`。但 `App.vue` 当前含有：
- `<template>` (header topbar + main slot)
- `<style scoped>`（全局样式）
- 业务组件引用（UserMenu 等）

这意味着 App.vue 同时是 layout shell + business content + route leaf。这违反 single responsibility，Task 11 (ScenesPage 完整实现) 后需要拆分。

## Recommended Follow-up Task (before Task 11)

**新建 Task N+1：Dashboard Layout / Page 拆分**

1. 创建 `src/dashboard/DashboardLayout.vue`（布局 + topbar + user menu）
2. 创建 `src/dashboard/DashboardPage.vue`（业务内容）
3. 修改 `App.vue` → 仅保留 `<router-view>` + 全局 `<style>` + setup 时 mount
4. 修改 `src/router/index.ts`：
   - `/` → DashboardPage（嵌套在 DashboardLayout 中）
   - `/scenes` → ScenesPage（可能也用 App.vue layout 或独立）

## Status

- 当前 Task 5 已 Approved with Minor note
- 本 gap 不阻塞后续 Task 6-16，但 Task 11 后强烈建议拆分
- 后续我会在适当 Task 中追加或并行建议
