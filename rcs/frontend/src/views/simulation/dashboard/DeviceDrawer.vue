<template>
  <div class="drawer-inner">
    <div v-if="loading" class="empty">loading…</div>
    <div v-else-if="device">
      <div class="head">
        <div class="title-row">
          <h3>{{ device.name }}</h3>
          <button class="close" @click="$emit('close')">×</button>
        </div>
        <div class="meta">
          <code>{{ device.device_id }}</code>
          <span class="pill" :class="device.status">{{ device.status }}</span>
        </div>
      </div>

      <div class="grid">
        <div class="cell">
          <div class="label">battery</div>
          <div class="value">{{ Math.round(device.battery ?? 0) }}%</div>
          <div class="bar"><span :style="{ width: (device.battery ?? 0) + '%' }" :class="batteryClass(device.battery ?? 0)"></span></div>
        </div>
        <div class="cell">
          <div class="label">speed</div>
          <div class="value">{{ device.speed }}</div>
        </div>
        <div class="cell">
          <div class="label">position</div>
          <div class="value small">{{ formatPos(device.position) }}</div>
        </div>
        <div class="cell">
          <div class="label">task</div>
          <div class="value small">{{ device.current_task ?? '—' }}</div>
        </div>
      </div>

      <h4 class="section">task history</h4>
      <ul v-if="history.length" class="history">
        <li v-for="tk in history" :key="tk.task_id">
          <span class="type">{{ tk.type }}</span>
          <span class="progress"><ProgressRing :value="tk.progress ?? 0" :state="(tk.status as any)" :size="28" :stroke="3" /></span>
          <span class="status" :class="tk.status">{{ tk.status }}</span>
          <span class="when">{{ formatTime(tk.created_at) }}</span>
        </li>
      </ul>
      <p v-else class="empty">no tasks yet</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import ProgressRing from '../components/ProgressRing.vue'

interface Device {
  device_id: string; device_type: string; name: string;
  status: string; battery: number; speed: number; position: number[];
  current_task: string | null;
}
interface Task { task_id: string; type: string; status: string; progress?: number; created_at: string; device_id: string }

const props = defineProps<{ deviceId: string }>()
defineEmits<{ close: [] }>()

const device = ref<Device | null>(null)
const history = ref<Task[]>([])
const loading = ref(true)
let timer: number | undefined

async function refresh() {
  try {
    const devices = (await axios.get<Device[]>('/api/devices')).data
    const fresh = devices.find(d => d.device_id === props.deviceId)
    device.value = fresh ?? null
    loading.value = false
    const tasks = (await axios.get<Task[]>('/api/tasks')).data
    history.value = tasks.filter(t => t.device_id === props.deviceId).slice(-12).reverse()
  } catch { /* ignore */ }
}

function formatPos(p: number[] | undefined): string {
  if (!p) return '—'
  return `x ${p[0].toFixed(1)} · z ${p[2].toFixed(1)}`
}
function formatTime(ts: string): string {
  return new Date(ts).toLocaleTimeString()
}
function batteryClass(b: number) {
  if (b < 20) return 'low'
  if (b < 50) return 'mid'
  return 'ok'
}

watch(() => props.deviceId, refresh)
onMounted(() => { refresh(); timer = window.setInterval(refresh, 2000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.drawer-inner { color: var(--fg); }
.head { margin-bottom: 12px; }
.title-row { display: flex; justify-content: space-between; align-items: center; }
.title-row h3 { margin: 0; font-size: 14px; color: var(--fg-muted); }
.close { background: transparent; border: none; color: var(--fg-soft); font-size: 22px; cursor: pointer; line-height: 1; padding: 0 4px; }
.close:hover { color: var(--fg); }
.meta { display: flex; gap: 6px; margin-top: 4px; align-items: center; font-size: 12px; color: var(--fg-soft); }
.meta code { color: var(--accent); background: var(--bg-card-alt); padding: 1px 6px; border-radius: 3px; font-size: 11px; }
.pill { padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; }
.pill.running { background: var(--good); color: white; }
.pill.idle { background: var(--bg-grid); color: var(--fg-muted); }
.pill.charging { background: var(--accent); color: var(--bg-app); }
.pill.fault { background: var(--bad); color: white; }

.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.cell { background: var(--bg-card-alt); border-radius: 6px; padding: 8px; }
.cell .label { font-size: 10px; color: var(--fg-soft); text-transform: uppercase; letter-spacing: 0.5px; }
.cell .value { font-size: 18px; font-weight: 700; color: var(--accent); line-height: 1.1; margin-top: 2px; }
.cell .value.small { font-size: 12px; font-weight: 500; color: var(--fg); }
.bar { background: var(--bg-grid); height: 4px; border-radius: 2px; margin-top: 4px; overflow: hidden; }
.bar span { display: block; height: 100%; transition: width 0.4s ease; }
.bar span.ok { background: linear-gradient(90deg, var(--good), #58c47e); }
.bar span.mid { background: linear-gradient(90deg, var(--warn), #f0b840); }
.bar span.low { background: linear-gradient(90deg, var(--bad), #f07070); }

.section { margin: 12px 0 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--fg-soft); }
.history { list-style: none; margin: 0; padding: 0; font-size: 12px; }
.history li { display: grid; grid-template-columns: 100px 36px 80px 1fr; gap: 6px; padding: 4px 0; border-bottom: 1px solid var(--border); align-items: center; }
.history .type { color: var(--accent); }
.history .status { font-size: 11px; }
.history .status.running { color: var(--accent); }
.history .status.completed { color: var(--good); }
.history .status.reverted { color: var(--warn); }
.history .status.failed { color: var(--bad); }
.history .status.pending { color: var(--fg-soft); }
.history .when { font-size: 10px; color: var(--fg-soft); text-align: right; }
.empty { color: var(--fg-soft); font-size: 12px; }
</style>