<template>
  <div id="wt-top">
    <div id="wt-search-wrap">
      <span id="wt-search-ico">🔍</span>
      <input
        id="wt-search"
        type="text"
        :placeholder="t.search_placeholder"
        v-model="searchQuery"
        @input="onSearch"
      />
      <button v-if="searchQuery" id="wt-search-clear" @click="clearSearch">✕</button>
    </div>

    <div id="wt-switcher">
      <div class="wt-sw-group">
        <button
          class="wt-sw-btn"
          :class="{ act: store.curView === '3d' }"
          @click="store.setView('3d')"
        >
          {{ t.view_3d }}
        </button>
        <button
          class="wt-sw-btn"
          :class="{ act: store.curView === '2d' }"
          @click="store.setView('2d')"
        >
          {{ t.view_2d }}
        </button>
      </div>
    </div>

    <!-- Which backend supplied the data (geometry + inventory layer). -->
    <div class="wt-shell-src" :class="store.shellOrigin" :title="shellTitle">
      {{ shellLabel }}
    </div>

    <button class="wt-theme-btn" @click="toggleTheme">
      {{ store.isDark ? '☀️' : '🌙' }}
    </button>

    <div class="wt-pills">
      <div class="wt-pill occ">
        <div class="wt-pv">{{ store.hudStats.occ }}</div>
        <div class="wt-pl">{{ t.bins }}</div>
      </div>
      <div class="wt-pill free">
        <div class="wt-pv">{{ store.hudStats.free }}</div>
        <div class="wt-pl">{{ t.active }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'
import { useAppStore } from '@/stores/app'

const store = useWarehouseStore()
const app = useAppStore()
const searchQuery = ref('')

const t = computed(() => ({
  search_placeholder: store.lang === 'zh' ? '搜索商品编码...' : 'Search item code...',
  view_3d: '3D',
  view_2d: '2D',
  bins: store.lang === 'zh' ? '库位' : 'Bins',
  active: store.lang === 'zh' ? '在用' : 'Active',
}))

function onSearch() {
  store.setSearch(searchQuery.value)
}

function clearSearch() {
  searchQuery.value = ''
  store.setSearch('')
}

function toggleTheme() {
  // Delegate to the global console theme so the whole app switches together.
  app.toggleTheme()
}

// Geometry + inventory together decide the badge. Both from RCS → green RCS;
// only geometry persisted (inventory still sim) → amber RCS*; everything sim → SIM.
// (inventoryOrigin is only ever 'rcs' | 'simulation' — it never has a 'preview' state.)
const combinedOrigin = computed<'rcs' | 'preview' | 'simulation'>(() => {
  if (store.shellOrigin === 'simulation' || store.inventoryOrigin === 'simulation') return 'simulation'
  if (store.shellOrigin === 'preview') return 'preview'
  return 'rcs'
})

const shellLabel = computed(() =>
  combinedOrigin.value === 'rcs' ? 'RCS' : combinedOrigin.value === 'preview' ? 'RCS*' : 'SIM',
)

const shellTitle = computed(() => {
  const zh = store.lang === 'zh'
  if (combinedOrigin.value === 'rcs') {
    return zh
      ? '几何与库存均来自 RCS（已持久化）'
      : 'Geometry and inventory from RCS (persisted)'
  }
  if (combinedOrigin.value === 'preview') {
    return zh
      ? '几何来自 RCS 内置蓝图 / 库存来自仿真后端（站点尚未导入）'
      : 'Geometry from RCS blueprint / inventory from simulation (site not imported)'
  }
  return zh ? '几何与库存来自仿真后端（RCS 不可用）' : 'Geometry and inventory from simulation backend (RCS unavailable)'
})
</script>

<style scoped>
.wt-shell-src {
  pointer-events: all;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  padding: 3px 7px;
  border-radius: 4px;
  border: 1px solid rgba(203, 213, 225, 0.35);
  color: #cbd5e1;
  cursor: default;
  white-space: nowrap;
}
/* Persisted RCS shell — the desired state. */
.wt-shell-src.rcs {
  border-color: rgba(74, 163, 255, 0.55);
  color: #7cc0ff;
}
/* Built-in blueprint converted on the fly (site never imported). */
.wt-shell-src.preview {
  border-color: rgba(250, 204, 21, 0.5);
  color: #facc15;
}
/* Fallback: RCS unreachable, simulation backend geometry in use. */
.wt-shell-src.simulation {
  border-color: rgba(148, 163, 184, 0.4);
  color: #94a3b8;
}

#wt-top {
  position: absolute;
  top: 0;
  left: 148px;
  right: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  background: linear-gradient(to bottom, rgba(12, 14, 20, 0.97) 55%, transparent);
  z-index: 10;
  pointer-events: none;
}

#wt-app.light #wt-top {
  background: rgba(240, 242, 245, 0.95);
  backdrop-filter: blur(4px);
}

#wt-search-wrap {
  position: relative;
  pointer-events: all;
  flex: 1;
  max-width: 280px;
}

#wt-search {
  width: 100%;
  height: 28px;
  border-radius: 7px;
  border: 1px solid var(--wt-border);
  background: var(--wt-card);
  color: var(--wt-text);
  font-size: 11px;
  padding: 0 28px 0 28px;
  outline: none;
  transition: border-color 0.15s;
}

#wt-search::placeholder {
  color: var(--wt-text3);
}

#wt-search:focus {
  border-color: var(--wt-accent);
}

#wt-search-ico {
  position: absolute;
  left: 8px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: var(--wt-text3);
  pointer-events: none;
}

#wt-search-clear {
  position: absolute;
  right: 7px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 11px;
  color: var(--wt-text3);
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
  line-height: 1;
}

#wt-search-clear:hover {
  color: var(--wt-text);
}

#wt-switcher {
  display: flex;
  align-items: center;
  gap: 6px;
  pointer-events: all;
  margin-left: 8px;
}

.wt-sw-group {
  display: flex;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 2px;
  gap: 2px;
}

#wt-app.light .wt-sw-group {
  background: rgba(0, 0, 0, 0.06);
  border-color: rgba(0, 0, 0, 0.1);
}

.wt-sw-btn {
  height: 24px;
  padding: 0 9px;
  border-radius: 5px;
  border: none;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.18s;
  display: flex;
  align-items: center;
  gap: 3px;
  white-space: nowrap;
  line-height: 1;
}

#wt-app.light .wt-sw-btn {
  color: rgba(0, 0, 0, 0.45);
}

.wt-sw-btn.act {
  background: #3b82f6;
  color: #fff;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.wt-sw-btn:not(.act):hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

#wt-app.light .wt-sw-btn:not(.act):hover {
  background: rgba(0, 0, 0, 0.08);
  color: #1a202c;
}

.wt-theme-btn {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  transition: all 0.18s;
  padding: 0;
  line-height: 1;
  pointer-events: all;
}

#wt-app.light .wt-theme-btn {
  border-color: rgba(0, 0, 0, 0.12);
  background: rgba(0, 0, 0, 0.05);
}

.wt-theme-btn:hover {
  background: rgba(255, 255, 255, 0.18);
}

#wt-app.light .wt-theme-btn:hover {
  background: rgba(0, 0, 0, 0.1);
}

.wt-pills {
  display: flex;
  gap: 5px;
  margin-left: auto;
  pointer-events: all;
}

.wt-pill {
  background: var(--wt-pill);
  border: 1px solid var(--wt-pillb);
  border-radius: 7px;
  padding: 3px 9px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 46px;
  transition: all 0.3s;
}

.wt-pv {
  font-size: 13px;
  font-weight: 800;
  line-height: 1.1;
  color: var(--wt-text);
}

.wt-pl {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.35);
  font-weight: 600;
  letter-spacing: 0.4px;
  margin-top: 1px;
}

.wt-pill.occ .wt-pv {
  color: #fb923c;
}
.wt-pill.free .wt-pv {
  color: #4ade80;
}
</style>
