<template>
  <div class="card">
    <header>
      <h3>场地布局</h3>
      <button class="add" @click="openAdd('dock')">+ Dock</button>
      <button class="add" @click="openAdd('warehouse')">+ Rack</button>
    </header>
    <div class="filter">
      <button class="chip" :class="{ active: filter === 'all' }" @click="filter = 'all'">全部 ({{ sites.length }})</button>
      <button class="chip" :class="{ active: filter === 'dock' }" @click="filter = 'dock'">Dock ({{ dockCount }})</button>
      <button class="chip" :class="{ active: filter === 'warehouse' }" @click="filter = 'warehouse'">Rack ({{ rackCount }})</button>
    </div>
    <ul class="list">
      <li v-for="s in filtered" :key="s.id" :class="[s.kind, { blocked: s.status === 'blocked' }]">
        <div class="row">
          <span class="dot" :style="{ background: s.color }"></span>
          <span class="name">{{ s.name }}</span>
          <span class="kind">{{ s.kind === 'dock' ? 'Dock' : 'Rack' }}</span>
          <span class="status">{{ s.status }}</span>
        </div>
        <div class="row meta">
          <code>{{ s.id }}</code>
          <span>({{ s.position[0].toFixed(1) }}, {{ s.position[2].toFixed(1) }})</span>
        </div>
        <div class="row actions">
          <button class="link" @click="toggleStatus(s)" :title="s.status === 'active' ? '阻塞' : '激活'">
            {{ s.status === 'active' ? 'block' : 'unblock' }}
          </button>
          <button class="link danger" @click="remove(s)">删除</button>
        </div>
      </li>
      <li v-if="!filtered.length" class="empty">暂无场地，点击 + 新增。</li>
    </ul>

    <div v-if="adding" class="modal" @click.self="adding = null">
      <div class="dialog">
        <h4>新增 {{ adding === 'dock' ? 'Dock' : 'Warehouse Rack' }}</h4>
        <label>
          <span>ID</span>
          <input v-model="form.id" placeholder="dock-E / rack-6" />
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
        <div class="grid3">
          <label>
            <span>width</span>
            <input type="number" step="0.5" v-model.number="form.width" />
          </label>
          <label>
            <span>depth</span>
            <input type="number" step="0.5" v-model.number="form.depth" />
          </label>
          <label>
            <span>color</span>
            <input type="color" v-model="form.color" />
          </label>
        </div>
        <div class="actions">
          <button @click="adding = null">取消</button>
          <button class="primary" :disabled="busy" @click="confirmAdd">创建</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { success, error as toastError } from '../composables/toast'

interface Site {
  id: string
  kind: 'dock' | 'warehouse'
  name: string
  position: [number, number, number]
  width: number
  height: number
  depth: number
  rotation: number
  color: string
  status: string
}

const sites = ref<Site[]>([])
const filter = ref<'all' | 'dock' | 'warehouse'>('all')
const adding = ref<'dock' | 'warehouse' | null>(null)
const busy = ref(false)
const form = ref({
  id: '', name: '', x: 0, z: 0, width: 2.5, depth: 2.5, color: '#5eb0ff',
})

let timer: number | undefined

async function refresh() {
  try {
    sites.value = (await axios.get<Site[]>('/api/sites')).data
  } catch { /* ignore */ }
}

const filtered = computed(() => {
  if (filter.value === 'all') return sites.value
  return sites.value.filter((s) => s.kind === filter.value)
})
const dockCount = computed(() => sites.value.filter((s) => s.kind === 'dock').length)
const rackCount = computed(() => sites.value.filter((s) => s.kind === 'warehouse').length)

function openAdd(kind: 'dock' | 'warehouse') {
  adding.value = kind
  form.value = {
    id: kind === 'dock' ? `dock-${String.fromCharCode(65 + dockCount.value)}` : `rack-${rackCount.value + 1}`,
    name: kind === 'dock' ? `Dock ${String.fromCharCode(65 + dockCount.value)}` : `Rack ${rackCount.value + 1}`,
    x: kind === 'dock' ? 0 : 0,
    z: kind === 'dock' ? 7 : -5,
    width: 2.5,
    depth: 2.5,
    color: kind === 'dock' ? '#5eb0ff' : '#8a98ad',
  }
}

async function confirmAdd() {
  if (!adding.value) return
  if (!form.value.id || !form.value.name) {
    toastError('id / name 不能为空')
    return
  }
  busy.value = true
  try {
    await axios.post('/api/sites', {
      ...form.value,
      kind: adding.value,
      height: adding.value === 'dock' ? 1.5 : 2.0,
    })
    success(`已创建 ${form.value.id}`)
    adding.value = null
    refresh()
  } catch (e) {
    toastError('创建失败', (e as Error).message)
  } finally {
    busy.value = false
  }
}

async function toggleStatus(s: Site) {
  const next = s.status === 'active' ? 'blocked' : 'active'
  try {
    await axios.patch(`/api/sites/${s.id}`, { status: next })
    success(`${s.id} → ${next}`)
    refresh()
  } catch (e) {
    toastError('更新失败', (e as Error).message)
  }
}

async function remove(s: Site) {
  if (!confirm(`确定删除 ${s.id}?`)) return
  try {
    await axios.delete(`/api/sites/${s.id}`)
    success(`已删除 ${s.id}`)
    refresh()
  } catch (e) {
    toastError('删除失败', (e as Error).message)
  }
}

onMounted(() => {
  refresh()
  timer = window.setInterval(refresh, 5000)
})
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; height: 100%; display: flex; flex-direction: column; min-height: 0; }
header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
header h3 { margin: 0; font-size: 14px; color: var(--fg); flex: 1; }
header .add { background: var(--bg-sub); border: 1px solid var(--border); color: var(--fg); padding: 3px 8px; border-radius: 4px; font-size: 11px; cursor: pointer; }
header .add:hover { background: var(--accent); color: white; border-color: var(--accent); }
.filter { display: flex; gap: 4px; margin-bottom: 8px; }
.filter .chip { background: var(--bg-sub); border: 1px solid var(--border); color: var(--fg-soft); padding: 3px 8px; border-radius: 999px; font-size: 10px; cursor: pointer; }
.filter .chip.active { background: var(--accent); color: white; border-color: var(--accent); }
.list { list-style: none; margin: 0; padding: 0; font-size: 12px; flex: 1; overflow-y: auto; min-height: 0; }
.list li { background: var(--bg-sub); border: 1px solid var(--border); border-left: 3px solid var(--accent); border-radius: 6px; padding: 8px; margin-bottom: 6px; }
.list li.dock { border-left-color: var(--accent); }
.list li.warehouse { border-left-color: #8a98ad; }
.list li.blocked { opacity: 0.6; border-left-color: var(--bad); }
.list li .row { display: flex; align-items: center; gap: 6px; }
.list li .row + .row { margin-top: 4px; }
.list li .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.list li .name { font-weight: 600; color: var(--fg); flex: 1; }
.list li .kind { font-size: 10px; color: var(--fg-soft); padding: 1px 6px; border-radius: 999px; background: var(--bg-card); border: 1px solid var(--border); text-transform: uppercase; letter-spacing: 0.5px; }
.list li .status { font-size: 10px; color: var(--good); text-transform: uppercase; letter-spacing: 0.5px; }
.list li.blocked .status { color: var(--bad); }
.list li .meta { font-size: 11px; color: var(--fg-soft); }
.list li .meta code { font-family: monospace; color: var(--accent); }
.list li .actions { gap: 8px; }
.list li .link { background: transparent; border: none; color: var(--accent); cursor: pointer; font-size: 11px; padding: 0; }
.list li .link.danger { color: var(--bad); }
.empty { color: var(--fg-soft); padding: 12px 0; text-align: center; }

.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1500; }
.dialog { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 18px; width: 360px; max-width: 92vw; }
.dialog h4 { margin: 0 0 12px; font-size: 14px; color: var(--fg); }
.dialog label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--fg-soft); margin-bottom: 8px; }
.dialog label input { background: var(--bg-sub); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; font-size: 13px; }
.dialog .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.dialog .grid3 { display: grid; grid-template-columns: 1fr 1fr 80px; gap: 8px; align-items: end; }
.dialog .actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
.dialog .actions button { padding: 6px 12px; border-radius: 4px; border: 1px solid var(--border); background: var(--bg-sub); color: var(--fg); cursor: pointer; font-size: 12px; }
.dialog .actions .primary { background: var(--accent); color: white; border-color: var(--accent); }
.dialog .actions button:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
