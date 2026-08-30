<template>
  <div class="overlay" @click.self="$emit('close')">
    <div class="palette">
      <input ref="inputEl" v-model="query" placeholder="搜索设备或任务…" @keydown="onKey" />
      <ul v-if="results.length" class="results">
        <li
          v-for="r in results"
          :key="r.id + r.kind"
          :class="{ active: activeIndex === results.indexOf(r) }"
          @mouseenter="activeIndex = results.indexOf(r)"
          @click="pick(r)"
        >
          <span class="kind" :class="r.kind">{{ r.kind }}</span>
          <span class="title">{{ r.title }}</span>
          <span class="hint">{{ r.hint }}</span>
        </li>
      </ul>
      <p v-else class="empty">没有匹配项</p>
      <div class="footer">
        <kbd>↑↓</kbd> 移动 · <kbd>⏎</kbd> 选择 · <kbd>esc</kbd> 关闭
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import axios from 'axios'

const emit = defineEmits<{ close: []; pickDevice: [string] }>()

interface Device { device_id: string; name: string; device_type: string; status: string }
interface Task { task_id: string; type: string; status: string; device_id: string }

const query = ref('')
const activeIndex = ref(0)
const inputEl = ref<HTMLInputElement | null>(null)
const devices = ref<Device[]>([])
const tasks = ref<Task[]>([])

async function load() {
  try {
    devices.value = (await axios.get<Device[]>('/api/devices')).data
    tasks.value = (await axios.get<Task[]>('/api/tasks')).data
  } catch { /* ignore */ }
}

interface Result { id: string; kind: 'device' | 'task'; title: string; hint: string }

const results = computed<Result[]>(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return []
  const devMatches: Result[] = devices.value
    .filter(d => d.device_id.includes(q) || d.name.toLowerCase().includes(q))
    .map(d => ({ id: d.device_id, kind: 'device', title: d.name, hint: d.device_id + ' · ' + d.status }))
  const taskMatches: Result[] = tasks.value
    .filter(t => t.task_id.includes(q) || t.type.includes(q))
    .slice(0, 30)
    .map(t => ({ id: t.task_id, kind: 'task', title: t.task_id, hint: t.type + ' · ' + t.status }))
  return [...devMatches, ...taskMatches].slice(0, 12)
})

function pick(r: Result) {
  if (r.kind === 'device') emit('pickDevice', r.id)
  else emit('close')
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = Math.min(activeIndex.value + 1, results.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = Math.max(activeIndex.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const r = results.value[activeIndex.value]
    if (r) pick(r)
  } else if (e.key === 'Escape') {
    emit('close')
  }
}

onMounted(async () => {
  await load()
  await nextTick()
  inputEl.value?.focus()
})
</script>

<style scoped>
.overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.55); z-index: 100; display: flex; align-items: flex-start; justify-content: center; padding-top: 12vh; }
.palette { width: 560px; max-width: 92vw; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; box-shadow: 0 24px 48px rgba(0,0,0,0.4); overflow: hidden; }
input { width: 100%; background: var(--bg-card-alt); color: var(--fg); border: none; padding: 14px 16px; font-size: 14px; outline: none; border-bottom: 1px solid var(--border); }
.results { list-style: none; margin: 0; padding: 4px; max-height: 360px; overflow-y: auto; }
.results li { display: grid; grid-template-columns: 80px 1fr auto; gap: 10px; align-items: center; padding: 8px 10px; border-radius: 6px; cursor: pointer; font-size: 13px; color: var(--fg); }
.results li.active { background: var(--bg-hover); }
.kind { font-size: 10px; text-transform: uppercase; padding: 2px 6px; border-radius: 3px; background: var(--bg-card-alt); color: var(--fg-soft); text-align: center; font-weight: 600; }
.kind.device { background: var(--accent); color: var(--bg-app); }
.title { font-weight: 600; }
.hint { color: var(--fg-soft); font-size: 11px; }
.empty { padding: 24px; text-align: center; color: var(--fg-soft); margin: 0; }
.footer { padding: 8px 14px; background: var(--bg-card-alt); border-top: 1px solid var(--border); font-size: 11px; color: var(--fg-soft); }
kbd { background: var(--bg-hover); border: 1px solid var(--border); padding: 1px 5px; border-radius: 3px; font-family: inherit; }
</style>