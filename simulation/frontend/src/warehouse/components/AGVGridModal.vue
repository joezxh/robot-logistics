<template>
  <div id="wt-agv-ov" class="wt-modal-overlay" @click.self="close">
    <div id="wt-agv-modal" class="wt-modal">
      <div class="wt-modal-hdr">
        <div class="wt-modal-title">{{ t.title }}</div>
        <button class="wt-x-btn" @click="close">✕</button>
      </div>
      <div class="wt-modal-body">
        <div class="wt-agv-tools">
          <button
            v-for="tool in tools"
            :key="tool.type"
            class="wt-agv-tool-btn"
            :class="{ act: store.agvTool === tool.type }"
            :style="{ '--tool-color': tool.color }"
            @click="store.agvTool = tool.type"
          >
            {{ tool.label }}
          </button>
        </div>
        <canvas ref="canvas" class="wt-agv-canvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useWarehouseStore } from '../store/warehouse'
import { AGV_TOOLS } from '../types'

const store = useWarehouseStore()
const canvas = ref<HTMLCanvasElement | null>(null)
const tools = AGV_TOOLS

function close() {
  store.agvOpen = false
}

const t = {
  get title() {
    return store.lang === 'zh' ? 'AGV 路径编辑' : 'AGV Path Editor'
  },
}

onMounted(() => {
  if (canvas.value && store.agvGrid) {
    drawGrid()
  }
})

watch(
  () => store.agvGrid,
  () => {
    if (canvas.value) drawGrid()
  }
)

function drawGrid() {
  const cv = canvas.value
  const g = store.agvGrid
  if (!cv || !g) return

  const SCALE = 6
  cv.width = g.cols * SCALE
  cv.height = g.rows * SCALE

  const ctx = cv.getContext('2d')!
  const fill: Record<number, string> = { 0: '#374151', 1: '#6b7280', 2: '#3b82f6', 3: '#f97316' }

  for (let z = 0; z < g.rows; z++) {
    for (let x = 0; x < g.cols; x++) {
      ctx.fillStyle = fill[g.cells[z * g.cols + x]?.t] || '#6b7280'
      ctx.fillRect(x * SCALE, z * SCALE, SCALE - 1, SCALE - 1)
    }
  }
}
</script>

<style scoped>
.wt-modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 85;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wt-modal {
  background: #13151e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  width: 500px;
  max-width: 90vw;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.6);
  overflow: hidden;
}

.wt-modal-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.wt-modal-title {
  font-size: 13px;
  font-weight: 700;
}

.wt-x-btn {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  border: 1px solid var(--wt-cb);
  background: var(--wt-card);
  color: var(--wt-text2);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}

.wt-x-btn:hover {
  background: rgba(255, 255, 255, 0.14);
}

.wt-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
}

.wt-agv-tools {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.wt-agv-tool-btn {
  height: 28px;
  padding: 0 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: var(--wt-card);
  color: var(--wt-text2);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.wt-agv-tool-btn.act {
  border-color: var(--tool-color);
  background: rgba(var(--tool-color), 0.15);
  color: var(--tool-color);
}

.wt-agv-canvas {
  display: block;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--wt-border);
  border-radius: 8px;
  width: 100%;
}
</style>
