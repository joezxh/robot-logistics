<template>
  <div class="status">
    <span class="dot" :class="{ online }"></span>
    <span class="text">{{ online ? 'online' : 'offline' }}</span>
    <span class="sep">·</span>
    <span class="time">{{ time }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

const time = ref(formatTime(new Date()))
const online = ref(true)

let timer: number | undefined
let poll: number | undefined

async function checkHealth() {
  try {
    await axios.get('/api/status', { timeout: 2000 })
    online.value = true
  } catch {
    online.value = false
  }
}

function formatTime(d: Date) {
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
}

onMounted(() => {
  timer = window.setInterval(() => { time.value = formatTime(new Date()) }, 1000)
  poll = window.setInterval(checkHealth, 5000)
  checkHealth()
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
  if (poll) clearInterval(poll)
})
</script>

<style scoped>
.status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 11px;
  color: var(--fg-soft);
  font-variant-numeric: tabular-nums;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--bad);
  box-shadow: 0 0 6px currentColor;
  transition: background 0.3s ease;
}
.dot.online { background: var(--good); }
.text { font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.sep { color: var(--border); }
.time { font-family: monospace; }
</style>
