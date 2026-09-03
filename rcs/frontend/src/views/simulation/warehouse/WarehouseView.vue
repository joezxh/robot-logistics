<template>
  <div id="wt-app" :class="appStore.isDark ? 'dark' : 'light'">
    <!-- 3D View -->
    <div id="wt-cw" :style="{ display: store.curView === '3d' ? 'block' : 'none' }">
      <canvas ref="canvasRef" id="wt-c"></canvas>
      <div id="wt-drag-indicator" v-if="store.dragActive">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 11V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v0"/>
          <path d="M14 10V4a2 2 0 0 0-2-2a2 2 0 0 0-2 2v2"/>
          <path d="M10 10.5V6a2 2 0 0 0-2-2a2 2 0 0 0-2 2v8"/>
          <path d="M18 8a2 2 0 1 1 4 0v6a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>
        </svg>
        <span>Drag/Pan</span>
      </div>
    </div>

    <!-- 2D View -->
    <View2D v-if="store.curView === '2d'" />

    <!-- Top Bar -->
    <TopBar />

    <!-- Bottom Bar -->
    <BottomBar />

    <!-- Sidebar -->
    <Sidebar v-if="store.sidebarOpen" />

    <!-- Detail Panel -->
    <DetailPanel v-if="store.dpOpen" />

    <!-- Loading Overlay -->
    <div class="wt-loading" v-if="store.loading">
      <div class="wt-spinner"></div>
      <div class="wt-loading-text">Loading warehouse data...</div>
    </div>

    <!-- Aisle Picker -->
    <AislePicker v-if="store.aislePickerOpen" />

    <!-- AGV Grid Modal -->
    <AGVGridModal v-if="store.agvOpen" />

    <!-- Floor Plan Modal -->
    <FloorPlanModal v-if="store.fpOpen" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ThreeEngine } from './engine/ThreeEngine'
import { useWarehouseStore } from './store/warehouse'
import { fetchWarehouseData } from './api/warehouse'
import { fetchWarehouseShell, type ShellOrigin } from './api/shell'
import {
  fetchRcsGroups,
  fetchRcsSlots,
  fetchRcsTasks,
  fetchRcsStats,
} from './api/inventory'
import type { Slot } from './types'
import { mergeShellIntoFloorFull } from './adapters/floorShell'
import TopBar from './components/TopBar.vue'
import BottomBar from './components/BottomBar.vue'
import Sidebar from './components/Sidebar.vue'
import DetailPanel from './components/DetailPanel.vue'
import View2D from './components/View2D.vue'
import AislePicker from './components/AislePicker.vue'
import AGVGridModal from './components/AGVGridModal.vue'
import FloorPlanModal from './components/FloorPlanModal.vue'
import { useAppStore } from '@/stores/app'

const store = useWarehouseStore()
const appStore = useAppStore()
const canvasRef = ref<HTMLCanvasElement | null>(null)
let engine: ThreeEngine | null = null

async function loadData() {
  store.setLoading(true)
  try {
    // Geometry is owned by RCS (FloorShell). The inventory layer (slots / items /
    // AGV / tasks) now also lives in RCS; we read it from the RCS backend when
    // available and fall back to the simulation backend otherwise.
    const source = await fetchWarehouseShell()
    const shellOrigin: ShellOrigin = source?.origin ?? 'simulation'
    const floorFull = mergeShellIntoFloorFull(null, source?.shell)

    let groups = await safeRcs(fetchRcsGroups)
    let slots: Slot[] = []
    let invOrigin: ShellOrigin = 'simulation'
    if (groups && groups.length > 0) {
      slots = await fetchRcsSlots()
      const [tasks, stats] = await Promise.all([fetchRcsTasks(), fetchRcsStats()])
      store.setLogisticsTasks(tasks)
      store.setLogisticsStats(stats)
      invOrigin = 'rcs'
    } else {
      // RCS has no inventory yet — fall back to the simulation backend.
      const data = await fetchWarehouseData()
      groups = data.groups
      slots = data.slots
      store.setLogisticsTasks(data.tasks)
      store.setLogisticsStats(data.stats)
      invOrigin = 'simulation'
    }

    store.setGroups(groups)
    store.setSlots(slots)
    store.setFloorFull(floorFull)
    store.setShellOrigin(shellOrigin)
    store.setInventoryOrigin(invOrigin)
    if (groups.length > 0) {
      store.setGroup(groups[0])
    }
    if (engine) {
      engine.buildScene(slots, floorFull ?? undefined)
    }
  } catch (e) {
    console.error('Failed to load warehouse data:', e)
  } finally {
    store.setLoading(false)
  }
}

async function safeRcs<T>(fn: () => Promise<T>): Promise<T | null> {
  try {
    return await fn()
  } catch {
    return null
  }
}

function initEngine() {
  if (!canvasRef.value) return

  const container = canvasRef.value.parentElement!
  engine = new ThreeEngine()
  engine.init(canvasRef.value, container)

  engine.bindMouse(
    container,
    (result, x, y) => {
      store.ttVisible = !!result
      store.ttData = result
      store.ttX = x
      store.ttY = y
    },
    (result, wasSelected, isDouble) => {
      if (result) {
        if (!isDouble) {
          store.openDetailPanel(result)
        }
      } else if (wasSelected) {
        store.closeDetailPanel()
      }
    }
  )

  store.setThreeReady(true)

  if (store.slots.length > 0) {
    engine.buildScene(store.slots, store.floorFull ?? undefined)
  }
}

watch(
  () => appStore.isDark,
  (dark) => {
    // Keep the warehouse store + 3D engine in sync with the global theme so the
    // whole console (incl. this module) switches skin together.
    store.setTheme(dark)
    if (engine) {
      engine.setDarkMode(dark)
    }
  }
)

watch(
  () => store.showWalls,
  (show) => {
    if (engine) {
      engine.setShowWalls(show)
    }
  }
)

watch(
  () => store.showMarkings,
  (show) => {
    if (engine) {
      engine.setShowMarkings(show)
    }
  }
)

onMounted(async () => {
  await loadData()
  initEngine()
})

onUnmounted(() => {
  if (engine) {
    engine.clearRoot()
    engine = null
  }
})
</script>

<style>
/*
 * Warehouse Theatre 3D Styles — unified with the global explorer design system.
 * The --wt-* tokens are now ALIASES of the shared RCS tokens (defined in
 * tokens.css), so this module inherits the exact same palette, typography and
 * glass treatment as every other console page (incl. RcsLandingView).
 * Only the few values that are scene-specific (floor/grid accents) keep a
 * dedicated shade, still derived from the global accent family.
 */
#wt-app.dark {
  --wt-bg: var(--bg-base);
  --wt-bg2: var(--bg-deep);
  --wt-bg3: var(--bg-elevated);
  --wt-border: var(--border);
  --wt-text: var(--fg);
  --wt-text2: var(--fg-secondary);
  --wt-text3: var(--fg-muted);
  --wt-sb: var(--bg-deep);
  --wt-card: var(--bg-surface);
  --wt-cb: var(--bg-elevated);
  --wt-accent: var(--accent);
  --wt-accent2: var(--accent-hover);
  --wt-pill: var(--bg-surface);
  --wt-pillb: var(--border-strong);
  --wt-floor: var(--bg-deep);
  --wt-grid: var(--hud-grid);
}

#wt-app.light {
  --wt-bg: var(--bg-base);
  --wt-bg2: var(--bg-deep);
  --wt-bg3: var(--bg-elevated);
  --wt-border: var(--border);
  --wt-text: var(--fg);
  --wt-text2: var(--fg-secondary);
  --wt-text3: var(--fg-muted);
  --wt-sb: var(--bg-deep);
  --wt-card: var(--bg-surface);
  --wt-cb: var(--bg-elevated);
  --wt-accent: var(--accent);
  --wt-accent2: var(--accent-hover);
  --wt-pill: var(--bg-surface);
  --wt-pillb: var(--border-strong);
  --wt-floor: var(--bg-deep);
  --wt-grid: var(--hud-grid);
}

#wt-app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--wt-bg);
  font-family: var(--font-sans);
  font-size: 12px;
  color: var(--wt-text);
  position: relative;
  overflow: hidden;
  transition: background 0.3s;
}

#wt-cw {
  flex: 1;
  position: relative;
  min-height: 0;
}

#wt-c {
  display: block;
  width: 100%;
  height: 100%;
}

#wt-drag-indicator {
  position: absolute;
  pointer-events: none;
  z-index: 30;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: var(--wt-accent2);
  opacity: 0.7;
}

#wt-drag-indicator span {
  font-size: 10px;
  font-weight: 600;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}

.wt-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 12px;
  z-index: 5;
  background: var(--wt-bg);
}

.wt-spinner {
  width: 28px;
  height: 28px;
  border: 2px solid var(--border);
  border-top-color: var(--wt-accent);
  border-radius: 50%;
  animation: wtSpin 0.7s linear infinite;
}

@keyframes wtSpin {
  to {
    transform: rotate(360deg);
  }
}

.wt-loading-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
}
</style>
