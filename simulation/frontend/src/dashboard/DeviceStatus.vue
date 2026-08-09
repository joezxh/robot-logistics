<template>
  <div class="card">
    <div class="head">
      <h3>{{ t.devices }}</h3>
      <button class="add" @click="adding = true">+ 设备</button>
      <label class="multisel" v-if="devices.length">
        <input type="checkbox" v-model="multiMode" />
        <span>{{ t.multi_select.hint }}</span>
      </label>
    </div>
    <div class="search" v-if="devices.length">
      <input
        v-model="query"
        type="search"
        placeholder="🔍 过滤设备…"
        :aria-label="t.devices"
      />
      <span class="count">{{ filtered.length }} / {{ devices.length }}</span>
    </div>
    <div class="chips" v-if="devices.length">
      <button
        v-for="c in typeChips"
        :key="c.value"
        class="chip"
        :class="{ active: typeFilter === c.value }"
        @click="typeFilter = c.value"
      >
        {{ c.icon }} {{ c.label }}
      </button>
    </div>
    <div class="fleet" v-if="devices.length">
      <div
        v-for="bucket in fleetSummary"
        :key="bucket.label"
        class="bucket"
        :style="{ width: bucket.percent + '%', background: bucket.color }"
        :title="`${bucket.label}: ${bucket.count}`"
      ></div>
    </div>
    <div class="legend" v-if="devices.length">
      <span><span class="dot running"></span>{{ t.fleet.running }} {{ fleetCounts.running }}</span>
      <span><span class="dot idle"></span>{{ t.fleet.idle }} {{ fleetCounts.idle }}</span>
      <span><span class="dot charging"></span>{{ t.fleet.charging }} {{ fleetCounts.charging }}</span>
      <span><span class="dot fault"></span>{{ t.fleet.fault }} {{ fleetCounts.fault }}</span>
    </div>
    <div class="device-grid">
      <div
        v-for="d in filtered"
        :key="d.device_id"
        class="device"
        :class="[d.status, { selected: selected.has(d.device_id) }]"
        tabindex="0"
        role="button"
        @click="onClick($event, d.device_id)"
        @keyup.enter="openSingle(d.device_id)"
      >
        <div class="device-name">
          <input
            v-if="multiMode"
            type="checkbox"
            class="check"
            :checked="selected.has(d.device_id)"
            @click.stop="toggle(d.device_id)"
          />
          <span class="icon">{{ iconFor(d.device_type) }}</span>
          {{ d.name }}
        </div>
        <div class="device-id">{{ d.device_id }}</div>
        <div class="bar">
          <span :style="{ width: (d.battery ?? 100) + '%' }" :class="batteryClass(d.battery ?? 100)"></span>
        </div>
        <svg class="spark" viewBox="0 0 60 14" preserveAspectRatio="none">
          <polyline
            :points="sparkPoints(d.device_id)"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linejoin="round"
          />
        </svg>
        <div class="meta">
          <span class="status-pill" :class="d.status">{{ statusLabel(d.status) }}</span>
          <span class="battery-num">⚡ {{ Math.round(d.battery ?? 0) }}%</span>
        </div>
      </div>
    </div>
    <div v-if="multiMode && selected.size > 0" class="bulkbar">
      <span class="count">{{ tf(t.multi_select.count, { n: selected.size }) }}</span>
      <button class="danger" :disabled="busy" @click="confirmBulkRollback">
        {{ t.multi_select.bulk_rollback }}
      </button>
      <button class="ghost" @click="selected = new Set()" :disabled="busy">×</button>
    </div>

    <div v-if="adding" class="modal" @click.self="adding = false">
      <div class="dialog">
        <h4>新增设备</h4>
        <label>
          <span>device_id</span>
          <input v-model="form.device_id" placeholder="agv-99" />
        </label>
        <label>
          <span>类型</span>
          <select v-model="form.device_type">
            <option value="container_robot">集装箱机器人</option>
            <option value="agv">AGV 转运车</option>
            <option value="stacker">立体堆垛机</option>
          </select>
        </label>
        <label>
          <span>名称</span>
          <input v-model="form.name" />
        </label>
        <div class="grid2">
          <label>
            <span>X</span>
            <input type="number" step="0.5" v-model.number="form.x" />
          </label>
          <label>
            <span>Z</span>
            <input type="number" step="0.5" v-model.number="form.z" />
          </label>
        </div>
        <div class="actions">
          <button @click="adding = false">取消</button>
          <button class="primary" :disabled="busy" @click="confirmAdd">创建</button>
        </div>
      </div>
    </div>

    <div v-if="askCount > 0" class="modal" @click.self="askCount = 0">
      <div class="dialog">
        <h4>{{ tf(t.multi_select.confirm, { n: askCount }) }}</h4>
        <div class="actions">
          <button @click="askCount = 0">{{ t.cancel }}</button>
          <button class="danger" :disabled="busy" @click="doBulkRollback">{{ t.confirm }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useI18n, tf } from '../i18n'
import { success, error as toastError } from '../composables/toast'
import { recordDeviceSnapshot, deviceSparkline } from '../composables/deviceHistory'

const { t } = useI18n()
const emit = defineEmits<{ openDrawer: [string] }>()

interface Device { device_id: string; device_type: string; name: string; status: string; battery: number }
const devices = ref<Device[]>([])

async function refresh() {
  try {
    const res = await axios.get<Device[]>('/api/devices')
    devices.value = res.data
    let taskCount = 0
    try {
      const tk = await axios.get<unknown[]>('/api/tasks')
      taskCount = tk.data.length
    } catch { /* ignore */ }
    for (const d of res.data) {
      recordDeviceSnapshot(d.device_id, d.battery ?? 0, taskCount)
    }
  } catch {
    /* backend may not be up yet */
  }
}

const query = ref('')
const typeFilter = ref<'all' | 'container_robot' | 'agv' | 'stacker'>('all')

const typeChips = [
  { value: 'all', label: '全部', icon: '📦' },
  { value: 'container_robot', label: '集装箱', icon: '🧱' },
  { value: 'agv', label: 'AGV', icon: '🛞' },
  { value: 'stacker', label: '堆垛机', icon: '🗄️' },
] as const

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  let list = devices.value
  if (typeFilter.value !== 'all') {
    list = list.filter((d) => d.device_type === typeFilter.value)
  }
  if (!q) return list
  return list.filter((d) =>
    d.name.toLowerCase().includes(q) ||
    d.device_id.toLowerCase().includes(q) ||
    d.device_type.toLowerCase().includes(q),
  )
})

function sparkPoints(deviceId: string): string {
  const data = deviceSparkline(deviceId)
  if (data.length === 0) return ''
  const max = 100
  const min = 0
  const range = max - min || 1
  return data
    .map((v, i) => {
      const x = (i / Math.max(1, data.length - 1)) * 60
      const y = 14 - ((v - min) / range) * 14
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
}

const ICONS: Record<string, string> = {
  container_robot: '🧱',
  agv: '🛞',
  stacker: '🗄️',
}
function iconFor(type: string) { return ICONS[type] ?? '📦' }
function statusLabel(status: string) {
  return (t.value.fleet as Record<string, string>)[status] ?? status
}
function batteryClass(b: number) {
  if (b < 20) return 'low'
  if (b < 50) return 'mid'
  return 'ok'
}

let timer: number | undefined
onMounted(() => {
  refresh()
  timer = window.setInterval(refresh, 1500)
})
onUnmounted(() => { if (timer) clearInterval(timer) })

const FLEET_COLORS: Record<string, string> = {
  running: '#1f8a4c',
  idle: '#5b6478',
  charging: '#5eb0ff',
  fault: '#c0392b',
}
const FLEET_ORDER = ['running', 'idle', 'charging', 'fault']

const fleetCounts = computed(() => {
  const c: Record<string, number> = { running: 0, idle: 0, charging: 0, fault: 0 }
  for (const d of devices.value) c[d.status] = (c[d.status] ?? 0) + 1
  return c
})
const fleetSummary = computed(() => {
  const total = devices.value.length || 1
  return FLEET_ORDER.map(label => ({
    label,
    count: fleetCounts.value[label] ?? 0,
    color: FLEET_COLORS[label],
    percent: ((fleetCounts.value[label] ?? 0) / total) * 100,
  }))
})

// Multi-select state
const multiMode = ref(false)
const selected = ref<Set<string>>(new Set())
const busy = ref(false)
const askCount = ref(0)

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
  emit('openDrawer', id)
}
function openSingle(id: string) {
  if (multiMode.value) toggle(id)
  else emit('openDrawer', id)
}

function confirmBulkRollback() {
  askCount.value = selected.value.size
}
async function doBulkRollback() {
  if (busy.value || selected.value.size === 0) return
  busy.value = true
  try {
    const r = await axios.post('/api/devices/rollback', {
      device_ids: Array.from(selected.value),
      limit_per_device: 2,
    })
    const total = r.data?.total ?? 0
    success(tf(t.value.toast.rollback_done, { n: total }))
    selected.value = new Set()
    refresh()
  } catch (e) {
    toastError('rollback failed', (e as Error).message)
  } finally {
    busy.value = false
    askCount.value = 0
  }
}

// Add device
const adding = ref(false)
const form = ref({ device_id: '', device_type: 'agv', name: '', x: 0, z: 0 })
async function confirmAdd() {
  if (!form.value.device_id || !form.value.name) {
    toastError('device_id / name 不能为空')
    return
  }
  busy.value = true
  try {
    await axios.post('/api/devices/register', form.value)
    success(`已注册 ${form.value.device_id}`)
    adding.value = false
    form.value = { device_id: '', device_type: 'agv', name: '', x: 0, z: 0 }
    refresh()
  } catch (e) {
    toastError('注册失败', (e as Error).message)
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; height: 100%; display: flex; flex-direction: column; min-height: 0; }
.card h3 { margin: 0; font-size: 14px; color: var(--fg); }
.head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 6px; }
.head .add { background: var(--bg-sub); border: 1px solid var(--border); color: var(--fg); padding: 3px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; }
.head .add:hover { background: var(--accent); color: white; border-color: var(--accent); }
.multisel { display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--fg-soft); cursor: pointer; }
.search { display: flex; gap: 6px; align-items: center; margin-bottom: 6px; }
.search input { flex: 1; background: var(--bg-sub); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 5px 8px; font-size: 12px; }
.search input:focus { outline: none; border-color: var(--accent); }
.search .count { font-size: 10px; color: var(--fg-soft); white-space: nowrap; }
.chips { display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 6px; }
.chip { background: var(--bg-sub); border: 1px solid var(--border); color: var(--fg-soft); padding: 3px 8px; border-radius: 999px; font-size: 10px; cursor: pointer; transition: all 0.18s ease; }
.chip:hover { color: var(--fg); border-color: var(--accent); }
.chip.active { background: var(--accent); color: white; border-color: var(--accent); }
.fleet { height: 6px; border-radius: 3px; display: flex; overflow: hidden; background: var(--border); margin-bottom: 6px; }
.fleet .bucket { transition: width 0.4s ease; }
.legend { display: flex; gap: 10px; flex-wrap: wrap; font-size: 10px; color: var(--fg-soft); margin-bottom: 8px; }
.legend .dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 4px; vertical-align: middle; }
.legend .dot.running { background: #1f8a4c; }
.legend .dot.idle { background: #5b6478; }
.legend .dot.charging { background: #5eb0ff; }
.legend .dot.fault { background: #c0392b; }
.device-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 8px; overflow-y: auto; flex: 1; min-height: 0; padding-right: 4px; }
.device { background: var(--bg-sub); border-radius: 6px; padding: 10px; cursor: pointer; transition: box-shadow 0.18s ease, transform 0.18s ease; min-height: 96px; }
.device:hover { transform: translateY(-1px); }
.device.selected { box-shadow: 0 0 0 2px var(--accent); }
.device.running { border-left: 3px solid #1f8a4c; animation: pulse-running 2.4s ease-in-out infinite; }
.device.idle { border-left: 3px solid #5b6478; }
.device.charging { border-left: 3px solid #5eb0ff; }
.device.fault { border-left: 3px solid #c0392b; animation: pulse-fault 1.2s ease-in-out infinite; }
@keyframes pulse-running {
  0%, 100% { box-shadow: 0 0 0 0 rgba(31,138,76,0.0); }
  50% { box-shadow: 0 0 0 4px rgba(31,138,76,0.18); }
}
@keyframes pulse-fault {
  0%, 100% { box-shadow: 0 0 0 0 rgba(192,57,43,0.0); }
  50% { box-shadow: 0 0 0 4px rgba(192,57,43,0.32); }
}
.device-name { font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 6px; }
.device-name .icon { font-size: 16px; }
.device-name .check { margin: 0; }
.device-id { font-size: 11px; color: var(--fg-soft); margin: 2px 0; }
.bar { background: var(--border); height: 4px; border-radius: 2px; margin: 4px 0; overflow: hidden; }
.bar span { display: block; height: 100%; transition: width 0.4s ease, background 0.4s ease; }
.bar span.ok { background: linear-gradient(90deg, #1f8a4c, #58c47e); }
.bar span.mid { background: linear-gradient(90deg, #d68910, #f0b840); }
.bar span.low { background: linear-gradient(90deg, #c0392b, #f07070); }
.spark { width: 100%; height: 14px; color: var(--accent); opacity: 0.6; }
.meta { font-size: 11px; color: var(--fg-soft); display: flex; justify-content: space-between; align-items: center; margin-top: 2px; }
.status-pill { padding: 1px 6px; border-radius: 3px; font-size: 10px; font-weight: 600; }
.status-pill.running { background: #1f8a4c; color: white; }
.status-pill.idle { background: #2a3f5f; color: var(--fg); }
.status-pill.charging { background: #5eb0ff; color: #0b1220; }
.status-pill.fault { background: #c0392b; color: white; }
.battery-num { font-size: 10px; color: #5eb0ff; }

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

.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.dialog { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 18px; max-width: 380px; width: 92vw; }
.dialog h4 { margin: 0 0 12px; font-size: 14px; color: var(--fg); }
.dialog label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--fg-soft); margin-bottom: 8px; }
.dialog label input, .dialog label select { background: var(--bg-sub); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; font-size: 13px; }
.dialog .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.dialog .actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 12px; }
.dialog button { padding: 6px 12px; border-radius: 4px; border: 1px solid var(--border); background: var(--bg-sub); color: var(--fg); cursor: pointer; font-size: 12px; }
.dialog button.primary { background: var(--accent); color: white; border-color: var(--accent); }
.dialog button.danger { background: #c0392b; color: white; border-color: #c0392b; }
.dialog button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
