<template>
  <div class="card">
    <h3>任务队列</h3>
    <div class="head">
      <h3>{{ t.tasks }}</h3>
      <label class="multisel" v-if="tasks.length">
        <input type="checkbox" v-model="multiMode" />
        <span>多选</span>
      </label>
    </div>
    <v-chart :option="chartOption" autoresize class="chart" />
    <ul class="task-list">
      <li v-for="t in recent" :key="t.task_id" :class="[t.status, { selected: selected.has(t.task_id) }]" @click="onClick($event, t.task_id)" tabindex="0" @keyup.enter="openTask(t.task_id)">
        <input
          v-if="multiMode"
          type="checkbox"
          class="check"
          :checked="selected.has(t.task_id)"
          @click.stop="toggle(t.task_id)"
        />
        <ProgressRing :value="t.progress ?? 0" :state="(t.status as any)" :size="36" :stroke="4" />
        <span class="type">{{ t.type }}</span>
        <span class="desc">{{ t.description }}</span>
        <span class="priority" :class="priorityClass(t.priority)">P{{ t.priority }}</span>
      </li>
      <li v-if="!recent.length" class="empty">{{ t.queue_empty }}</li>
    </ul>
    <div v-if="multiMode && selected.size > 0" class="bulkbar">
      <span class="count">{{ selected.size }} / {{ tasks.length }} selected</span>
      <button class="danger" :disabled="busy" @click="bulkRollback">批量回滚</button>
      <button class="ghost" @click="selected = new Set()" :disabled="busy">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import ProgressRing from '../components/ProgressRing.vue'
import { useI18n, tf } from '../i18n'
import { openTaskDrawer } from '../composables/taskDrawerBus'
import { success, error as toastError } from '../composables/toast'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent, LegendComponent])

const { t } = useI18n()

interface Task {
  task_id: string
  type: string
  description: string
  priority: number
  status: string
  progress?: number
  device_id?: string
}

const tasks = ref<Task[]>([])

async function refresh() {
  try {
    tasks.value = (await axios.get<Task[]>('/api/tasks')).data
  } catch { /* backend may be down */ }
}

const recent = computed(() => tasks.value.slice(-6).reverse())

const byType = computed(() => {
  const stats: Record<string, Record<string, number>> = {}
  for (const t of tasks.value) {
    if (!stats[t.type]) stats[t.type] = { pending: 0, running: 0, completed: 0, reverted: 0, failed: 0 }
    const s = t.status in stats[t.type] ? t.status : 'completed'
    stats[t.type][s] = (stats[t.type][s] ?? 0) + 1
  }
  return stats
})

const chartOption = computed(() => {
  const types = Object.keys(byType.value)
  return {
    grid: { top: 30, bottom: 30, left: 50, right: 12 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: {
      textStyle: { color: '#c7d2e0', fontSize: 10 },
      top: 4,
    },
    xAxis: { type: 'category', data: types, axisLabel: { color: '#8a98ad', fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { color: '#8a98ad', fontSize: 10 } },
    series: [
      { name: 'pending', type: 'bar', stack: 's', itemStyle: { color: '#5b6478' }, data: types.map(t => byType.value[t]?.pending ?? 0) },
      { name: 'running', type: 'bar', stack: 's', itemStyle: { color: '#5eb0ff' }, data: types.map(t => byType.value[t]?.running ?? 0) },
      { name: 'completed', type: 'bar', stack: 's', itemStyle: { color: '#1f8a4c' }, data: types.map(t => byType.value[t]?.completed ?? 0) },
      { name: 'reverted', type: 'bar', stack: 's', itemStyle: { color: '#d68910' }, data: types.map(t => byType.value[t]?.reverted ?? 0) },
      { name: 'failed', type: 'bar', stack: 's', itemStyle: { color: '#c0392b' }, data: types.map(t => byType.value[t]?.failed ?? 0) },
    ],
  }
})

function priorityClass(p: number) {
  return p === 1 ? 'critical' : p === 2 ? 'high' : 'normal'
}

// Multi-select
const multiMode = ref(false)
const selected = ref<Set<string>>(new Set())
const busy = ref(false)

function toggle(id: string) {
  const next = new Set(selected.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selected.value = next
}
function onClick(e: MouseEvent, id: string) {
  if (multiMode.value || e.shiftKey) {
    multiMode.value = true
    toggle(id)
    return
  }
  openTaskDrawer(id)
}
function openTask(id: string) {
  if (multiMode.value) toggle(id)
  else openTaskDrawer(id)
}
async function bulkRollback() {
  if (busy.value || selected.value.size === 0) return
  busy.value = true
  try {
    let ok = 0
    for (const tid of selected.value) {
      try {
        await axios.post(`/api/tasks/${tid}/rollback`)
        ok += 1
      } catch { /* ignore individual failures */ }
    }
    success(tf(t.value.toast.rollback_done, { n: ok }))
    selected.value = new Set()
    refresh()
  } catch (e) {
    toastError('bulk rollback failed', (e as Error).message)
  } finally {
    busy.value = false
  }
}

let timer: number | undefined
onMounted(() => { refresh(); timer = window.setInterval(refresh, 2000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.card { background: #111a2e; border: 1px solid #1d2740; border-radius: 8px; padding: 12px; }
.card h3 { margin: 0 0 8px; font-size: 14px; color: #c7d2e0; }
.chart { width: 100%; height: 180px; }
.task-list { list-style: none; margin: 8px 0 0; padding: 0; font-size: 12px; max-height: 140px; overflow-y: auto; }
.task-list li { display: grid; grid-template-columns: 44px 80px 1fr 36px; gap: 6px; padding: 4px 0; border-bottom: 1px solid #1d2740; align-items: center; }
.type { color: #5eb0ff; }
.desc { color: #e6e9ef; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.priority { font-size: 10px; padding: 2px 6px; border-radius: 3px; text-align: center; }
.priority.critical { background: #c0392b; }
.priority.high { background: #d68910; }
.priority.normal { background: #1f8a4c; }
.status { font-size: 11px; }
.status.pending { color: #8a98ad; }
.status.running { color: #5eb0ff; }
.status.completed { color: #1f8a4c; }
.status.reverted { color: #d68910; }
.status.failed { color: #c0392b; }
.empty { color: #8a98ad; text-align: center; padding: 12px 0; }
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.multisel { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--fg-soft); cursor: pointer; }
.task-list li { display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 4px 4px; border-radius: 4px; }
.task-list li.selected { background: rgba(94,176,255,0.12); }
.task-list li .check { flex-shrink: 0; }
.task-list li .type { width: 100px; }
.task-list li .desc { flex: 1; }
.task-list li .priority { flex-shrink: 0; }
.bulkbar {
  margin-top: 8px;
  display: flex;
  gap: 8px;
  align-items: center;
  background: var(--bg-sub);
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
}
.bulkbar .count { flex: 1; font-size: 12px; color: var(--fg); }
.bulkbar button { padding: 4px 10px; border-radius: 4px; border: 1px solid var(--border); background: var(--bg-card); color: var(--fg); cursor: pointer; font-size: 12px; }
.bulkbar button.danger { background: #c0392b; color: white; border-color: #c0392b; }
.bulkbar button.ghost { background: transparent; }
.bulkbar button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>