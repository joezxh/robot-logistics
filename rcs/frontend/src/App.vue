<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <nav class="app-nav">
      <span class="brand">RCS</span>
      <RouterLink to="/devices" class="navlink">设备</RouterLink>
      <RouterLink to="/admin/maps" class="navlink">地图</RouterLink>
      <RouterLink to="/admin/orders" class="navlink">订单</RouterLink>
      <RouterLink to="/admin/scheduler" class="navlink">调度</RouterLink>
      <RouterLink to="/admin/logs" class="navlink">日志</RouterLink>
      <span class="sep"></span>
      <RouterLink to="/sitemap" class="navlink">站点地图</RouterLink>
      <RouterLink to="/control" class="navlink">设备控制</RouterLink>
    </nav>
    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell { display: flex; flex-direction: column; height: 100%; }
.app-nav { display: flex; align-items: center; gap: 8px; padding: 8px 16px; background: var(--bg-card); border-bottom: 1px solid var(--border); flex-wrap: wrap; }
.brand { font-weight: 700; color: var(--accent); letter-spacing: 1px; margin-right: 12px; }
.navlink { color: var(--fg-soft); text-decoration: none; font-size: 14px; padding: 4px 8px; border-radius: 6px; }
.navlink.router-link-active { color: var(--accent); background: var(--bg-card-alt); }
.sep { width: 1px; height: 18px; background: var(--border); margin: 0 8px; }
.app-main { flex: 1; min-height: 0; overflow: auto; }
</style>

<style>
:root { color-scheme: dark; }
html, body, #app { height: 100%; margin: 0; }
body { background: var(--bg); color: var(--fg); font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif; }
#app { display: flex; flex-direction: column; }
</style>