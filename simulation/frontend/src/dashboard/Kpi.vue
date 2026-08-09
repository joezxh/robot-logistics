<template>
  <div class="card kpi">
    <h3>{{ t.kpi }}</h3>
    <div class="grid">
      <button
        v-for="m in metrics"
        :key="m.key"
        class="metric"
        type="button"
        @click="open(m.key)"
      >
        <div class="label">{{ m.label }}</div>
        <div class="value">{{ format(m.key, latest[m.key]) }}</div>
        <v-chart :option="spark(m.key)" autoresize class="spark" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { useI18n } from '../i18n'
import { kpiBus, type KpiSnapshot } from '../composables/kpiBus'
import { openKpiZoom } from '../composables/kpiZoomBus'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent])
const { t } = useI18n()

interface Metrics {
  throughput_per_hour: number
  success_rate: number
  active_tasks: number
  energy_kwh: number
}

const latest = ref<Metrics>({
  throughput_per_hour: 0,
  success_rate: 0,
  active_tasks: 0,
  energy_kwh: 0,
})
const metrics = computed(() => [
  { key: 'throughput_per_hour' as const, label: t.value.kpi_throughput },
  { key: 'success_rate' as const, label: t.value.kpi_success },
  { key: 'active_tasks' as const, label: t.value.kpi_active },
  { key: 'energy_kwh' as const, label: t.value.kpi_energy },
])

let timer: number | undefined

async function refresh() {
  try {
    const res = await axios.get<Metrics>('/api/metrics')
    latest.value = res.data
    const snap: KpiSnapshot = { ts: Date.now(), ...res.data }
    kpiBus.push(snap)
  } catch { /* backend may be down */ }
}

function spark(metric: keyof Metrics) {
  const data = kpiBus.history.map((h) => h[metric])
  return {
    grid: { top: 4, bottom: 4, left: 4, right: 4 },
    xAxis: { type: 'category', show: false, data: data.map((_, i) => i) },
    yAxis: { type: 'value', show: false },
    tooltip: { trigger: 'axis', show: false },
    series: [{
      type: 'line',
      smooth: true,
      showSymbol: false,
      data,
      lineStyle: { width: 2, color: '#5eb0ff' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [ { offset: 0, color: 'rgba(94,176,255,0.4)' }, { offset: 1, color: 'rgba(94,176,255,0)' } ] },
      },
    }],
  }
}

function format(key: keyof Metrics, v: number | undefined): string {
  const num = v ?? 0
  if (key === 'success_rate') return `${num}%`
  if (key === 'energy_kwh') return num.toFixed(2)
  return String(Math.round(num))
}

function open(key: keyof Metrics) {
  const m = metrics.value.find((x) => x.key === key)
  if (m) openKpiZoom(m.key, m.label)
}

onMounted(() => {
  refresh()
  timer = window.setInterval(refresh, 3000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.card.kpi { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; height: 100%; }
.card h3 { margin: 0 0 8px; font-size: 14px; color: var(--fg); }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.metric {
  background: var(--bg-sub);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px;
  text-align: left;
  cursor: pointer;
  color: inherit;
  font: inherit;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}
.metric:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.18); }
.label { font-size: 11px; color: var(--fg-soft); }
.value { font-size: 22px; font-weight: 700; color: var(--accent); line-height: 1.1; }
.spark { width: 100%; height: 28px; margin-top: 4px; }
</style>
