<template>
  <div id="app">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { startTaskWatcher } from './composables/taskWatcher'

// Global keyboard listener (Ctrl+K palette, Ctrl+R refresh, Esc close drawers)
function onKey(e: KeyboardEvent) {
  const mod = e.ctrlKey || e.metaKey
  if (mod && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    window.dispatchEvent(new CustomEvent('robot-logic:toggle-palette'))
  } else if (mod && e.key.toLowerCase() === 'r') {
    e.preventDefault()
    window.dispatchEvent(new CustomEvent('robot-logic:refresh'))
  } else if (e.key === 'Escape') {
    window.dispatchEvent(new CustomEvent('robot-logic:close-drawers'))
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  startTaskWatcher()
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
})
</script>

<style>
:root[data-theme="light"] {
  --bg-app: #f4f6fb;
  --bg-card: #ffffff;
  --bg-card-alt: #eef1f8;
  --bg-grid: #d3d9e7;
  --bg-hover: #e0e6f1;
  --fg: #1c2333;
  --fg-muted: #4b5566;
  --fg-soft: #6c7891;
  --border: #d3d9e7;
  --accent: #2a72d8;
  --accent-soft: #5a8eea;
  --good: #1f8a4c;
  --warn: #d68910;
  --bad: #c0392b;
  --shadow: 0 6px 20px rgba(31, 41, 60, 0.08);
}

:root, :root[data-theme="dark"] {
  --bg-app: #0b1220;
  --bg-card: #111a2e;
  --bg-card-alt: #0e1730;
  --bg-grid: #1d2740;
  --bg-hover: #14213d;
  --fg: #e6e9ef;
  --fg-muted: #c7d2e0;
  --fg-soft: #8a98ad;
  --border: #1d2740;
  --accent: #5eb0ff;
  --accent-soft: #58c47e;
  --good: #1f8a4c;
  --warn: #d68910;
  --bad: #c0392b;
  --shadow: none;
}

* { box-sizing: border-box; }
html, body, #app { margin: 0; padding: 0; height: 100%; font-family: -apple-system, "Segoe UI", "Helvetica Neue", "PingFang SC", "Microsoft YaHei", Arial, sans-serif; background: var(--bg-app); color: var(--fg); transition: background 0.4s ease, color 0.4s ease; }
body, .card, .topbar, .modal, .drawer, .dialog, .menu, .modal, .scene, .timeline, .hud, .dashboard, .panel, .palette { transition: background 0.4s ease, color 0.4s ease, border-color 0.4s ease; }
.topbar { display: flex; align-items: center; gap: 12px; padding: 10px 24px; background: var(--bg-card); border-bottom: 1px solid var(--border); position: sticky; top: 0; z-index: 5; }
.brand { display: flex; align-items: center; gap: 8px; }
.brand .logo { font-size: 20px; }
.topbar h1 { font-size: 16px; margin: 0; font-weight: 600; letter-spacing: 0.3px; }
.topbar .subtitle { margin: 0; font-size: 12px; color: var(--fg-soft); }
.topbar .grow { flex: 1; }
.topbar .badge { padding: 2px 10px; border-radius: 999px; background: var(--good); color: white; font-size: 11px; font-weight: 600; }
.topbar .docs { font-size: 11px; color: var(--accent); text-decoration: none; padding: 4px 10px; border: 1px solid var(--border); border-radius: 4px; }
.topbar .docs:hover { background: var(--bg-card-alt); }
.topbar .iconbtn { background: var(--bg-card-alt); border: 1px solid var(--border); color: var(--fg); width: 32px; height: 28px; border-radius: 4px; cursor: pointer; font-size: 14px; display: inline-flex; align-items: center; justify-content: center; }
.topbar .iconbtn:hover { background: var(--bg-hover); }

main { display: grid; grid-template-columns: minmax(0, 1fr) 360px; grid-template-rows: minmax(440px, auto) 320px auto; gap: 12px; padding: 12px; height: calc(100% - 52px); }
main.has-drawer { grid-template-columns: minmax(0, 1fr) 320px 360px; }
.dashboard { grid-column: 1 / 2; grid-row: 1 / 2; display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 1fr); gap: 12px; align-items: stretch; min-height: 0; }
.dashboard .stack { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.dashboard .stack > * { flex: 1 1 0; min-height: 0; }
.scene { grid-column: 1 / 2; grid-row: 2 / 3; min-height: 0; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; overflow: hidden; position: relative; }
.scene::before { content: attr(data-caption); position: absolute; top: 8px; left: 12px; font-size: 11px; color: var(--fg-soft); z-index: 1; pointer-events: none; }
.timeline { grid-column: 1 / 2; grid-row: 3 / 4; min-height: 0; }
.drawer { grid-column: 2 / 3; grid-row: 1 / 4; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; overflow-y: auto; }
.panel { grid-column: 3 / 4; grid-row: 1 / 4; display: flex; flex-direction: column; gap: 12px; min-height: 0; }
main:not(.has-drawer) .panel { grid-column: 2 / 3; }

@media (max-width: 1100px) {
  main, main.has-drawer { grid-template-columns: 1fr; grid-template-rows: auto auto auto auto; }
  .panel, .scene, .dashboard, .drawer { grid-column: 1 / 2; grid-row: auto; }
  .topbar .subtitle { display: none; }
}

.fade-enter-from { opacity: 0; transform: translateY(6px); }
.fade-enter-active { transition: opacity 0.35s ease, transform 0.35s ease; }
.fade-leave-active { transition: opacity 0.2s ease; }
.fade-leave-to { opacity: 0; }
</style>
