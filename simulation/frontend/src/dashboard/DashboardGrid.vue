<template>
  <div class="dashboard" @dragover.prevent>
    <div
      v-for="(key, idx) in order"
      :key="key"
      class="slot"
      :class="{ dragging: draggingKey === key, 'drag-over': dropTarget === key }"
      draggable="true"
      @dragstart="onDragStart(key, $event)"
      @dragover="onDragOver(key, $event)"
      @dragleave="onDragLeave(key)"
      @drop="onDrop(key, idx)"
      @dragend="onDragEnd"
    >
      <div class="slot-handle" :title="dragHint">⋮⋮</div>
      <component :is="resolveComponent(key)" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, markRaw, computed } from 'vue'
import DeviceStatusPanel from './DeviceStatus.vue'
import TaskQueueChart from './TaskQueue.vue'
import KpiPanel from './Kpi.vue'
import AlertPanel from './Alerts.vue'
import StatsPanel from './Stats.vue'
import SiteManagerPanel from './SiteManager.vue'
import { useI18n } from '../i18n'

const { t } = useI18n()

const STORAGE_KEY = 'robot-logic.dashboard-order'

const REGISTRY: Record<string, ReturnType<typeof markRaw>> = {
  devices: markRaw(DeviceStatusPanel),
  tasks: markRaw(TaskQueueChart),
  kpi: markRaw(KpiPanel),
  alerts: markRaw(AlertPanel),
  stats: markRaw(StatsPanel),
  sites: markRaw(SiteManagerPanel),
}
const DEFAULT_ORDER = ['devices', 'sites', 'tasks', 'kpi'] as const

function detectInitial(): string[] {
  if (typeof localStorage === 'undefined') return [...DEFAULT_ORDER]
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return [...DEFAULT_ORDER]
  try {
    const arr = JSON.parse(raw)
    if (Array.isArray(arr) && arr.every((k) => typeof k === 'string') && arr.every((k) => k in REGISTRY)) {
      return arr
    }
  } catch { /* ignore */ }
  return [...DEFAULT_ORDER]
}

const order = ref<string[]>(detectInitial())

function resolveComponent(key: string) {
  return REGISTRY[key] ?? REGISTRY.devices
}

const draggingKey = ref<string | null>(null)
const dropTarget = ref<string | null>(null)

function onDragStart(key: string, e: DragEvent) {
  draggingKey.value = key
  e.dataTransfer?.setData('text/plain', key)
  if (e.dataTransfer) e.dataTransfer.effectAllowed = 'move'
}
function onDragOver(key: string, e: DragEvent) {
  if (!draggingKey.value || draggingKey.value === key) return
  dropTarget.value = key
  if (e.dataTransfer) e.dataTransfer.dropEffect = 'move'
}
function onDragLeave(key: string) {
  if (dropTarget.value === key) dropTarget.value = null
}
function onDrop(key: string, _idx: number) {
  const from = draggingKey.value
  if (!from || from === key) return
  const next = [...order.value]
  const fromIdx = next.indexOf(from)
  const toIdx = next.indexOf(key)
  if (fromIdx < 0 || toIdx < 0) return
  next.splice(fromIdx, 1)
  next.splice(toIdx, 0, from)
  order.value = next
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(next)) } catch { /* ignore */ }
  dropTarget.value = null
}
function onDragEnd() {
  draggingKey.value = null
  dropTarget.value = null
}

const dragHint = computed(() => t.value.hotkey_help)
</script>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) minmax(0, 1fr);
  gap: 12px;
  align-items: stretch;
  min-height: 0;
}
@media (max-width: 1400px) {
  .dashboard { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
}
@media (max-width: 720px) {
  .dashboard { grid-template-columns: 1fr; }
}
.slot {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0;
  position: relative;
  transition: box-shadow 0.18s ease, transform 0.18s ease, opacity 0.18s ease;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.slot :deep(> .card) { flex: 1; min-height: 0; }
.slot.dragging { opacity: 0.5; }
.slot.drag-over {
  box-shadow: 0 0 0 2px var(--accent);
  transform: scale(1.01);
}
.slot-handle {
  position: absolute;
  top: 4px;
  right: 6px;
  font-size: 12px;
  color: var(--fg-soft);
  cursor: grab;
  user-select: none;
  z-index: 2;
  opacity: 0.5;
}
.slot:hover .slot-handle { opacity: 1; }
.slot-handle:active { cursor: grabbing; }
</style>
