<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="state.open.value" class="overlay" @click.self="close">
        <div class="modal" role="dialog" :aria-label="state.label.value">
          <header>
            <h3>{{ state.label.value }}</h3>
            <div class="filters">
              <label>
                <span>{{ t.kpi_zoom.range }}</span>
                <select v-model="state.range.value">
                  <option value="30m">{{ t.kpi_zoom.range_30m }}</option>
                  <option value="2h">{{ t.kpi_zoom.range_2h }}</option>
                  <option value="all">{{ t.kpi_zoom.range_all }}</option>
                </select>
              </label>
              <button class="close" @click="close">×</button>
            </div>
          </header>
          <v-chart :option="option" autoresize class="chart" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { useI18n } from '../i18n'
import { kpiBus } from '../composables/kpiBus'
import { kpiZoomState as state, closeKpiZoom } from '../composables/kpiZoomBus'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])
const { t } = useI18n()

const filteredHistory = computed(() => {
  const history = kpiBus.history
  if (state.range.value === 'all' || history.length === 0) return history
  const now = Date.now()
  const windowMs = state.range.value === '30m' ? 30 * 60 * 1000 : 2 * 60 * 60 * 1000
  const cutoff = now - windowMs
  return history.filter((h) => h.ts >= cutoff)
})

const option = computed(() => {
  const data = filteredHistory.value
  const key = state.metricKey.value
  if (!key || data.length === 0) return { series: [] }
  return {
    backgroundColor: 'transparent',
    grid: { top: 24, bottom: 40, left: 60, right: 24 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20,30,50,0.92)',
      borderColor: '#3b82f6',
      textStyle: { color: '#c7d2e0' },
      formatter: (params: Array<{ axisValueLabel: string; value: number; marker: string }>) => {
        const p = params[0]
        const suffix = key === 'success_rate' ? '%' : ''
        return `${p.axisValueLabel}<br/>${p.marker}${state.label.value}: ${p.value}${suffix}`
      },
    },
    xAxis: {
      type: 'time',
      data: data.map((h) => new Date(h.ts)),
      axisLabel: { color: '#8a98ad' },
      axisLine: { lineStyle: { color: '#1d2740' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#8a98ad', formatter: (v: number) => key === 'success_rate' ? `${v}%` : `${v}` },
      splitLine: { lineStyle: { color: '#1d2740' } },
    },
    series: [{
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: data.map((h) => [h.ts, h[key as keyof typeof h]]),
      lineStyle: { width: 2, color: '#5eb0ff' },
      areaStyle: {
        color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(94,176,255,0.45)' },
            { offset: 1, color: 'rgba(94,176,255,0.02)' },
          ] },
      },
    }],
  }
})

function close() { closeKpiZoom() }

// Esc to close
function onKey(e: KeyboardEvent) {
  if (state.open.value && e.key === 'Escape') close()
}
watch(() => state.open.value, (v) => {
  if (v) window.addEventListener('keydown', onKey)
  else window.removeEventListener('keydown', onKey)
})
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  z-index: 1500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.modal {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  width: min(720px, 96vw);
  max-height: 80vh;
  padding: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
}
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
h3 { margin: 0; font-size: 16px; color: var(--fg); }
.filters { display: flex; gap: 12px; align-items: center; }
.filters label { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--fg-soft); }
.filters select { background: var(--bg-sub); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 3px 8px; font-size: 12px; }
.close {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--fg);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}
.chart { width: 100%; height: 360px; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active, .modal-leave-active { transition: opacity 0.18s ease; }
</style>
