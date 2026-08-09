<template>
  <div class="card stats">
    <h3>系统统计</h3>
    <div v-if="!loaded" class="loading">loading…</div>
    <template v-else>
      <div class="row">
        <div class="metric">
          <span class="lbl">uptime</span>
          <span class="val">{{ formatUptime(stats.uptime_seconds) }}</span>
        </div>
        <div class="metric">
          <span class="lbl">running</span>
          <span class="val" :class="{ on: stats.running }">{{ stats.running ? 'YES' : 'NO' }}</span>
        </div>
        <div class="metric">
          <span class="lbl">reverted</span>
          <span class="val">{{ stats.reverted_count }}</span>
        </div>
      </div>
      <h4>by status</h4>
      <ul class="bars">
        <li v-for="(count, status) in stats.by_status" :key="status">
          <span class="lbl">{{ status }}</span>
          <span class="bar"><span :style="{ width: pct(count, maxStatus) + '%', background: statusColor(status) }"></span></span>
          <span class="cnt">{{ count }}</span>
        </li>
        <li v-if="Object.keys(stats.by_status).length === 0" class="empty">暂无任务</li>
      </ul>
      <h4>by type</h4>
      <ul class="bars">
        <li v-for="(count, type) in stats.by_type" :key="type">
          <span class="lbl">{{ type }}</span>
          <span class="bar"><span :style="{ width: pct(count, maxType) + '%' }"></span></span>
          <span class="cnt">{{ count }}</span>
        </li>
        <li v-if="Object.keys(stats.by_type).length === 0" class="empty">—</li>
      </ul>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

interface Stats {
  by_status: Record<string, number>
  by_type: Record<string, number>
  per_device_battery: Record<string, number>
  uptime_seconds: number
  running: boolean
  reverted_count: number
}

const stats = ref<Stats>({
  by_status: {}, by_type: {}, per_device_battery: {},
  uptime_seconds: 0, running: false, reverted_count: 0,
})
const loaded = ref(false)

let timer: number | undefined

async function refresh() {
  try {
    const res = await axios.get<Stats>('/api/stats')
    stats.value = res.data
    loaded.value = true
  } catch { /* backend may be down */ }
}

const maxStatus = computed(() => Math.max(1, ...Object.values(stats.value.by_status)))
const maxType = computed(() => Math.max(1, ...Object.values(stats.value.by_type)))

function pct(c: number, m: number): number {
  return Math.round((c / Math.max(1, m)) * 100)
}

function statusColor(status: string): string {
  switch (status) {
    case 'running': return '#5eb0ff'
    case 'completed': return '#1f8a4c'
    case 'failed': return '#c0392b'
    case 'pending': return '#5b6478'
    case 'reverted': return '#d68910'
    default: return '#8a98ad'
  }
}

function formatUptime(sec: number): string {
  if (sec < 60) return `${sec.toFixed(0)}s`
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  if (m < 60) return `${m}m ${s}s`
  const h = Math.floor(m / 60)
  return `${h}h ${m % 60}m`
}

onMounted(() => {
  refresh()
  timer = window.setInterval(refresh, 3000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
.card h3 { margin: 0 0 8px; font-size: 14px; color: var(--fg); }
.card h4 { margin: 12px 0 4px; font-size: 11px; color: var(--fg-soft); text-transform: uppercase; letter-spacing: 0.5px; }
.loading { color: var(--fg-soft); font-size: 12px; padding: 12px 0; }
.row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
.metric { background: var(--bg-sub); border-radius: 4px; padding: 6px 8px; display: flex; flex-direction: column; }
.metric .lbl { font-size: 10px; color: var(--fg-soft); text-transform: uppercase; }
.metric .val { font-size: 14px; font-weight: 700; color: var(--fg); margin-top: 2px; font-variant-numeric: tabular-nums; }
.metric .val.on { color: var(--good); }
.bars { list-style: none; padding: 0; margin: 0; font-size: 12px; }
.bars li { display: grid; grid-template-columns: 80px 1fr 32px; gap: 6px; align-items: center; padding: 2px 0; }
.bars .lbl { color: var(--fg-soft); font-size: 11px; }
.bars .cnt { color: var(--fg); font-variant-numeric: tabular-nums; text-align: right; font-weight: 600; }
.bars .bar { background: var(--bg-sub); border-radius: 2px; height: 6px; overflow: hidden; }
.bars .bar span { display: block; height: 100%; background: var(--accent); transition: width 0.4s ease; }
.bars .empty { color: var(--fg-soft); font-style: italic; }
</style>
