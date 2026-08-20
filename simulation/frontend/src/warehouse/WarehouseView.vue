<template>
  <div id="wt-app" :class="store.isDark ? 'dark' : 'light'">
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
import TopBar from './components/TopBar.vue'
import BottomBar from './components/BottomBar.vue'
import Sidebar from './components/Sidebar.vue'
import DetailPanel from './components/DetailPanel.vue'
import View2D from './components/View2D.vue'
import AislePicker from './components/AislePicker.vue'
import AGVGridModal from './components/AGVGridModal.vue'
import FloorPlanModal from './components/FloorPlanModal.vue'

const store = useWarehouseStore()
const canvasRef = ref<HTMLCanvasElement | null>(null)
let engine: ThreeEngine | null = null

async function loadData() {
  store.setLoading(true)
  try {
    const data = await fetchWarehouseData()
    store.setGroups(data.groups)
    store.setSlots(data.slots)
    store.setFloorFull(data.floorFull)
    if (data.groups.length > 0) {
      store.setGroup(data.groups[0])
    }
    if (engine) {
      engine.buildScene(data.slots, data.floorFull ?? undefined)
    }
  } catch (e) {
    console.error('Failed to load warehouse data:', e)
  } finally {
    store.setLoading(false)
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
  () => store.isDark,
  (dark) => {
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
/* Warehouse Theatre 3D Styles */
#wt-app.dark {
  --wt-bg: #0c0e14;
  --wt-bg2: #13151e;
  --wt-bg3: #1a1e2a;
  --wt-border: rgba(255, 255, 255, 0.08);
  --wt-text: #fff;
  --wt-text2: rgba(255, 255, 255, 0.6);
  --wt-text3: rgba(255, 255, 255, 0.3);
  --wt-sb: rgba(10, 12, 18, 0.96);
  --wt-card: rgba(255, 255, 255, 0.04);
  --wt-cb: rgba(255, 255, 255, 0.08);
  --wt-accent: #3b82f6;
  --wt-accent2: #60a5fa;
  --wt-pill: rgba(255, 255, 255, 0.06);
  --wt-pillb: rgba(255, 255, 255, 0.1);
  --wt-floor: #0a0c12;
  --wt-grid: #181c28;
}

#wt-app.light {
  --wt-bg: #f0f2f5;
  --wt-bg2: #fff;
  --wt-bg3: #f7f9fc;
  --wt-border: #e2e8f0;
  --wt-text: #1a202c;
  --wt-text2: #4a5568;
  --wt-text3: #a0aec0;
  --wt-sb: #fff;
  --wt-card: #fff;
  --wt-cb: #e2e8f0;
  --wt-accent: #2563eb;
  --wt-accent2: #3b82f6;
  --wt-pill: #eff6ff;
  --wt-pillb: #dbeafe;
  --wt-floor: #f0f2f5;
  --wt-grid: #dde1e7;
}

#wt-app {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--wt-bg);
  font-family: -apple-system, "Inter", sans-serif;
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
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #3b82f6;
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
