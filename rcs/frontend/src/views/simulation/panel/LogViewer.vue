<template>
  <div class="card log">
    <div class="header">
      <h3>实时日志</h3>
      <div class="status">
        <span class="dot" :class="{ on: connected }"></span>
        {{ connected ? 'SSE 已连接' : '重新连接中…' }}
        <span class="follow" v-if="!autoScroll">⏸ 暂停</span>
        <span class="follow on" v-else>▶ 跟随</span>
        <span class="count">{{ filtered.length }} / {{ entries.length }}</span>
      </div>
    </div>
    <div class="filters">
      <input v-model="filter" placeholder="按 trace / module / message 过滤" />
      <select v-model="level">
        <option value="">全部级别</option>
        <option value="INFO">INFO</option>
        <option value="WARN">WARN</option>
        <option value="ERROR">ERROR</option>
      </select>
    </div>
    <ul class="entries" ref="listEl" @scroll="onScroll">
      <li v-for="(e, i) in filtered" :key="i + e.trace_id" :class="e.level">
        <span class="time">{{ formatTime(e.timestamp) }}</span>
        <span class="level">{{ e.level || 'INFO' }}</span>
        <span class="module">{{ e.module }}</span>
        <button class="trace" :class="{ ok: copied === e.trace_id }" :title="`复制 trace id: ${e.trace_id}`" @click="copyTrace(e.trace_id)">{{ copied === e.trace_id ? '✓ copied' : e.trace_id.slice(0, 12) }}</button>
        <span class="msg" v-html="highlight(e.message, filter)" :title="e.message"></span>
      </li>
      <li v-if="filtered.length === 0" class="empty">{{ entries.length === 0 ? '加载中…' : '没有匹配的日志' }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

interface Entry {
  trace_id: string
  task_id: string | null
  module: string
  message: string
  level?: string
  timestamp: string
}

const entries = ref<Entry[]>([])
const filter = ref('')
const level = ref('')
const connected = ref(false)
const autoScroll = ref(true)
const copied = ref('')
const listEl = ref<HTMLUListElement | null>(null)
let es: EventSource | null = null
let initialTimer: number | undefined

async function loadInitial() {
  try {
    const res = await axios.get<Entry[]>('/api/logs')
    entries.value = res.data.slice(-100).reverse()
  } catch { /* backend may be down */ }
}

function connectSSE() {
  es?.close()
  es = new EventSource('/api/logs/stream')
  es.onopen = () => { connected.value = true }
  es.onerror = () => {
    connected.value = false
    es?.close()
    setTimeout(connectSSE, 1500)
  }
  es.onmessage = (ev) => {
    try {
      const entry = JSON.parse(ev.data) as Entry
      entries.value = [entry, ...entries.value].slice(0, 200)
      // Auto-scroll the list to top, but only if the user hasn't scrolled
      // up to read history.
      if (autoScroll.value && listEl.value) {
        listEl.value.scrollTop = 0
      }
    } catch { /* ignore malformed */ }
  }
}

function onScroll() {
  if (!listEl.value) return
  // The list is newest-first; top means "following". When the user scrolls
  // away from the top, freeze the auto-scroll until they return.
  autoScroll.value = listEl.value.scrollTop <= 4
}

const filtered = computed(() => {
  const text = filter.value.trim().toLowerCase()
  return entries.value.filter(e => {
    if (level.value && e.level !== level.value) return false
    if (!text) return true
    return e.trace_id.toLowerCase().includes(text)
        || e.module.toLowerCase().includes(text)
        || e.message.toLowerCase().includes(text)
  })
})

function formatTime(ts: string) {
  return new Date(ts).toLocaleTimeString()
}

function escapeHtml(s: string) {
  return s.replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]!))
}
function highlight(text: string, query: string) {
  const safe = escapeHtml(text)
  if (!query) return safe
  const q = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return safe.replace(new RegExp(q, 'gi'), m => `<mark>${m}</mark>`)
}

async function copyTrace(id: string) {
  try {
    await navigator.clipboard.writeText(id)
    copied.value = id
    setTimeout(() => { copied.value = '' }, 1200)
  } catch { /* ignore */ }
}

onMounted(() => {
  loadInitial()
  connectSSE()
  initialTimer = window.setInterval(loadInitial, 8000)
})
onUnmounted(() => {
  if (es) es.close()
  if (initialTimer) clearInterval(initialTimer)
})
</script>

<style scoped>
.card.log { background: #111a2e; border: 1px solid #1d2740; border-radius: 8px; padding: 12px; flex: 1; display: flex; flex-direction: column; min-height: 0; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.card h3 { margin: 0; font-size: 14px; color: #c7d2e0; }
.status { font-size: 11px; color: #8a98ad; display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #4b5566; }
.dot.on { background: #1f8a4c; }
.follow { padding: 1px 5px; border-radius: 3px; background: #2a3f5f; color: #8a98ad; font-size: 10px; }
.follow.on { background: #5eb0ff; color: #0b1220; }
.count { color: #5b6478; }
.filters { display: grid; grid-template-columns: 1fr 110px; gap: 6px; margin-bottom: 6px; }
.filters input, .filters select { background: #0e1730; color: #e6e9ef; border: 1px solid #1d2740; border-radius: 4px; padding: 4px 8px; font-size: 12px; }
.entries { list-style: none; margin: 0; padding: 0; font-family: "SF Mono", "Consolas", "Cascadia Mono", monospace; font-size: 11px; overflow-y: auto; flex: 1; }
.entries li { padding: 2px 0; border-bottom: 1px dashed #1d2740; display: grid; grid-template-columns: 70px 50px 80px 1fr; gap: 6px; }
.time { color: #8a98ad; }
.level { color: #8a98ad; }
.INFO .level { color: #5eb0ff; }
.ERROR .level { color: #c0392b; }
.WARN .level { color: #d68910; }
.module { color: #58c47e; }
.trace { background: transparent; border: none; color: #5eb0ff; font-family: monospace; font-size: 11px; cursor: pointer; padding: 0 4px; text-decoration: underline dashed transparent; transition: color 0.18s ease, text-decoration 0.18s ease; }
.trace:hover { color: #58c47e; text-decoration-color: #58c47e; }
.trace.ok { color: #1f8a4c; }
.msg { color: #e6e9ef; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
:deep(mark) { background: rgba(94,176,255,0.4); color: #fff; padding: 0 1px; border-radius: 2px; }
.empty { color: #8a98ad; text-align: center; padding: 12px 0; grid-column: span 4; }
</style>