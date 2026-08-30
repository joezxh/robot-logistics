<template>
  <div class="card">
    <h3>任务时间线</h3>
    <v-chart :option="option" autoresize class="chart" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CustomChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, CustomChart, GridComponent, TooltipComponent])

interface Task {
  task_id: string
  type: string
  device_id: string
  status: string
  created_at: string
  started_at?: string | null
  completed_at?: string | null
}

const tasks = ref<Task[]>([])
let timer: number | undefined

async function refresh() {
  try {
    tasks.value = (await axios.get<Task[]>('/api/tasks')).data
  } catch { /* ignore */ }
}

const STATUS_COLOR: Record<string, string> = {
  pending: '#8a98ad',
  running: '#5eb0ff',
  completed: '#1f8a4c',
  reverted: '#d68910',
  failed: '#c0392b',
}

const option = computed(() => {
  const recent = tasks.value
    .filter(t => t.status !== 'pending')
    .slice(-40)
  const renderData: Array<[number, number, number, string]> = []
  // `params` is required positionally by ECharts' renderItem signature but is
  // unused here — the index comes from `api.value(0)`.
  const renderItem = (_params: { dataIndex?: number }, api: any) => {
    const idx = api.value(0) as number
    const start = api.coord([renderData[idx][0], api.value(0)])
    const end = api.coord([renderData[idx][1], api.value(0)])
    const height = api.size([0, 1])[1] * 0.6
    const rect = {
      x: start[0],
      y: start[1] - height / 2,
      width: Math.max(2, end[0] - start[0]),
      height,
    }
    return {
      type: 'rect',
      transition: ['shape'],
      shape: { ...rect, r: 3 },
      style: { fill: api.value(3), stroke: '#0b1220', lineWidth: 1 },
    }
  }
  const baseTime = recent.length ? new Date(recent[0].created_at).getTime() : Date.now()
  const deviceSet = Array.from(new Set(recent.map(t => t.device_id))).sort()
  recent.forEach((t) => {
    const start = t.started_at ? new Date(t.started_at).getTime() : new Date(t.created_at).getTime()
    const end = t.completed_at ? new Date(t.completed_at).getTime() : start + 4000
    renderData.push([start - baseTime, end - baseTime, deviceSet.indexOf(t.device_id), STATUS_COLOR[t.status] ?? '#888'])
  })
  return {
    grid: { top: 8, bottom: 24, left: 70, right: 12 },
    tooltip: { formatter: (p: { dataIndex: number }) => {
      const t = recent[p.dataIndex]
      return `<b>${t.task_id}</b><br/>${t.type} · ${t.device_id}<br/>${t.status}`
    } },
    xAxis: { type: 'value', min: 0, axisLabel: { color: '#8a98ad', fontSize: 10, formatter: (v: number) => `${(v / 1000).toFixed(0)}s` } },
    yAxis: { type: 'category', data: deviceSet, axisLabel: { color: '#c7d2e0', fontSize: 11 } },
    series: [{
      type: 'custom',
      encode: { x: [0, 1], y: 2 },
      renderItem,
      data: renderData.map((_, i) => i),
    }],
  }
})

onMounted(() => { refresh(); timer = window.setInterval(refresh, 4000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; color: var(--fg); }
.card h3 { margin: 0 0 8px; font-size: 14px; color: var(--fg-muted); }
.chart { width: 100%; height: 220px; }
</style>