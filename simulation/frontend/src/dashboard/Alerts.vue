<template>
  <div class="card">
    <div class="header">
      <h3>告警</h3>
      <span class="counts">
        <span class="badge critical" v-if="counts.critical">{{ counts.critical }}</span>
        <span class="badge warning" v-if="counts.warning">{{ counts.warning }}</span>
        <span class="badge info" v-if="counts.info">{{ counts.info }}</span>
      </span>
    </div>

    <div class="charts">
      <v-chart :option="donutOption" autoresize class="donut" />
      <ul class="alerts">
        <li v-for="a in alerts" :key="a.id" :class="[a.severity, { selected: selected.has(a.id) }]">
          <div class="meta">
            <input
              v-if="a.state === 'firing'"
              type="checkbox"
              class="check"
              :checked="selected.has(a.id)"
              @click="toggle(a.id)"
              @change="toggle(a.id)"
            />
            <span class="sev">{{ a.severity }}</span>
            <span class="rule">{{ a.rule }}</span>
            <span class="time">{{ formatRelative(a.created_at) }}</span>
          </div>
          <div class="title">{{ a.title }}</div>
          <div class="msg">{{ a.message }}</div>
          <button v-if="a.state === 'firing'" @click="ack(a)">确认</button>
          <span v-else class="state">{{ a.state }}</span>
        </li>
        <li v-if="!alerts.length" class="empty">无活跃告警</li>
      </ul>
      <div v-if="selected.size > 0" class="bulkbar">
        <span class="count">{{ selected.size }} selected</span>
        <button class="danger" :disabled="busy" @click="bulkAck">批量确认</button>
        <button class="ghost" @click="selected = new Set()" :disabled="busy">×</button>
      </div>
    </div>
    <v-chart :option="trendOption" autoresize class="trend" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, LineChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { useI18n } from '../i18n'
import { success, info, warn, error as toastError } from '../composables/toast'

const { t } = useI18n()

use([CanvasRenderer, PieChart, LineChart, TooltipComponent, LegendComponent, GridComponent])

interface Alert {
  id: string
  severity: 'info' | 'warning' | 'critical'
  rule: string
  title: string
  message: string
  state: 'firing' | 'acknowledged' | 'resolved'
  created_at: string
}

const alerts = ref<Alert[]>([])
const selected = ref<Set<string>>(new Set())
const busy = ref(false)

function toggle(id: string) {
  const next = new Set(selected.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selected.value = next
}

async function bulkAck() {
  if (busy.value || selected.value.size === 0) return
  busy.value = true
  try {
    let ok = 0
    for (const id of selected.value) {
      try {
        await axios.post(`/api/alerts/${id}/ack`, { by: 'ui' })
        ok += 1
      } catch { /* ignore */ }
    }
    success(`acknowledged ${ok}`)
    selected.value = new Set()
    await refresh()
  } finally {
    busy.value = false
  }
}
const counts = ref({ info: 0, warning: 0, critical: 0 })
const trend = ref<Record<'critical' | 'warning' | 'info', number[]>>({ critical: [], warning: [], info: [] })
const TREND_LEN = 40
let es: EventSource | null = null
let timer: number | undefined

async function refresh() {
  try {
    const res = await axios.get<{ firing: Alert[]; count_by_severity: { info: number; warning: number; critical: number } }>('/api/alerts')
    alerts.value = res.data.firing
    counts.value = res.data.count_by_severity
    for (const sev of ['critical', 'warning', 'info'] as const) {
      trend.value[sev].push(counts.value[sev])
      if (trend.value[sev].length > TREND_LEN) trend.value[sev].shift()
    }
    trend.value = { ...trend.value }
  } catch { /* ignore */ }
}

async function ack(a: Alert) {
  try {
    await axios.post(`/api/alerts/${a.id}/ack`, { by: 'ui' })
    success(t.value.toast.ack_done, a.title)
    await refresh()
  } catch { /* ignore */ }
}

function connectSSE() {
  es?.close()
  let firstMessage = true
  es = new EventSource('/api/alerts/stream')
  es.onmessage = async (evt) => {
    try {
      const payload = JSON.parse(evt.data) as Alert
      if (!firstMessage && payload.state === 'firing') {
        const kind = payload.severity === 'critical' ? 'error' : payload.severity === 'warning' ? 'warning' : 'info'
        if (kind === 'error') toastError(payload.title, payload.message)
        else if (kind === 'warning') warn(payload.title, payload.message)
        else info(payload.title, payload.message)
      }
    } catch { /* ignore parse */ }
    firstMessage = false
    await refresh()
  }
  es.onerror = () => {
    es?.close()
    setTimeout(connectSSE, 2000)
  }
}

function formatRelative(ts: string) {
  const diff = Date.now() - new Date(ts).getTime()
  const sec = Math.floor(diff / 1000)
  if (sec < 60) return `${sec}s 前`
  const min = Math.floor(sec / 60)
  if (min < 60) return `${min}m 前`
  const hr = Math.floor(min / 60)
  return `${hr}h 前`
}

const donutOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { show: false },
  series: [{
    type: 'pie',
    radius: ['55%', '75%'],
    avoidLabelOverlap: false,
    label: { show: false },
    data: [
      { name: 'critical', value: counts.value.critical, itemStyle: { color: '#c0392b' } },
      { name: 'warning',  value: counts.value.warning,  itemStyle: { color: '#d68910' } },
      { name: 'info',     value: counts.value.info,     itemStyle: { color: '#5eb0ff' } },
    ],
  }],
}))

const trendOption = computed(() => {
  const labels = trend.value.critical.map((_, i) => i)
  return {
    grid: { top: 8, bottom: 8, left: 4, right: 4 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: labels, show: false },
    yAxis: { type: 'value', show: false, minInterval: 1 },
    series: [
      { name: 'critical', type: 'line', smooth: true, showSymbol: false, data: trend.value.critical, lineStyle: { color: '#c0392b', width: 2 }, stack: 's', areaStyle: { color: 'rgba(192,57,43,0.25)' } },
      { name: 'warning',  type: 'line', smooth: true, showSymbol: false, data: trend.value.warning,  lineStyle: { color: '#d68910', width: 2 }, stack: 's', areaStyle: { color: 'rgba(214,137,16,0.25)' } },
      { name: 'info',     type: 'line', smooth: true, showSymbol: false, data: trend.value.info,     lineStyle: { color: '#5eb0ff', width: 2 }, stack: 's', areaStyle: { color: 'rgba(94,176,255,0.25)' } },
    ],
  }
})

onMounted(() => {
  refresh()
  connectSSE()
  timer = window.setInterval(refresh, 3000)
})
onUnmounted(() => {
  if (es) es.close()
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.card { background: #111a2e; border: 1px solid #1d2740; border-radius: 8px; padding: 12px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card h3 { margin: 0; font-size: 14px; color: #c7d2e0; }
.counts { display: flex; gap: 4px; }
.badge { font-size: 11px; font-weight: 700; padding: 2px 6px; border-radius: 3px; }
.critical { background: #c0392b; color: white; }
.warning { background: #d68910; color: white; }
.info { background: #5eb0ff; color: white; }
.charts { display: grid; grid-template-columns: 130px 1fr; gap: 8px; align-items: stretch; }
.donut { width: 130px; height: 130px; }
.alerts { list-style: none; margin: 0; padding: 0; font-size: 12px; max-height: 200px; overflow-y: auto; }
.alerts li { background: #0e1730; border-radius: 4px; padding: 6px; margin-bottom: 4px; border-left: 3px solid #5eb0ff; }
.alerts li.critical { border-left-color: #c0392b; }
.alerts li.warning { border-left-color: #d68910; }
.alerts li.info { border-left-color: #5eb0ff; }
.meta { display: flex; gap: 6px; font-size: 10px; color: #8a98ad; text-transform: uppercase; }
.sev { font-weight: 700; }
.sev.critical { color: #c0392b; }
.sev.warning { color: #d68910; }
.sev.info { color: #5eb0ff; }
.time { margin-left: auto; }
.title { font-weight: 600; color: #e6e9ef; margin: 2px 0; }
.msg { color: #c7d2e0; }
button { margin-top: 4px; background: #1f8a4c; color: white; border: none; border-radius: 3px; padding: 3px 8px; font-size: 11px; cursor: pointer; }
button:hover { background: #2aa15c; }
.state { font-size: 11px; color: #8a98ad; font-style: italic; }
.empty { text-align: center; color: #8a98ad; padding: 8px 0; }
.trend { width: 100%; height: 60px; margin-top: 8px; }
.alerts li.selected { background: rgba(94,176,255,0.12); border-radius: 4px; }
.alerts .check { margin-right: 6px; }
.bulkbar {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-top: 6px;
  background: var(--bg-sub);
  padding: 5px 10px;
  border-radius: 6px;
  border: 1px solid var(--border);
}
.bulkbar .count { flex: 1; font-size: 12px; color: var(--fg); }
.bulkbar button { padding: 3px 10px; border-radius: 4px; border: 1px solid var(--border); background: var(--bg-card); color: var(--fg); cursor: pointer; font-size: 11px; }
.bulkbar button.danger { background: var(--bad); color: white; border-color: var(--bad); }
.bulkbar button.ghost { background: transparent; }
.bulkbar button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>