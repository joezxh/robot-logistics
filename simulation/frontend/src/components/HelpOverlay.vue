<template>
  <Teleport to="body">
    <Transition name="help">
      <div v-if="open" class="overlay" @click.self="close">
        <div class="card" role="dialog" aria-label="Keyboard shortcuts">
          <header>
            <h3>Keyboard shortcuts</h3>
            <button class="close" @click="close">×</button>
          </header>
          <table>
            <thead>
              <tr><th>Key</th><th>Action</th></tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in shortcuts" :key="idx">
                <td><kbd v-for="(k, i) in row.keys" :key="i">{{ k }}</kbd></td>
                <td>{{ row.action }}</td>
              </tr>
            </tbody>
          </table>
          <p class="footer">按 <kbd>?</kbd> 任意时刻唤起此面板 · 按 <kbd>Esc</kbd> 关闭</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'

const open = ref(false)

const shortcuts = [
  { keys: ['Ctrl', 'K'], action: '打开命令面板 (搜索设备 / 任务)' },
  { keys: ['Ctrl', 'R'], action: '刷新所有面板' },
  { keys: ['Esc'], action: '关闭顶层 overlay (palette / drawer / modal)' },
  { keys: ['?'], action: '打开此快捷键面板' },
  { keys: ['Shift', '+ Click'], action: '设备卡片进入多选' },
  { keys: ['F'], action: '切换全屏模式' },
] as const

function close() { open.value = false }
function toggle() { open.value = !open.value }

function onKey(e: KeyboardEvent) {
  const mod = e.ctrlKey || e.metaKey
  if (e.key === '?' || (e.shiftKey && e.key === '/')) {
    e.preventDefault()
    toggle()
  } else if (mod && e.key.toLowerCase() === 'k') {
    // Already handled by App.vue; let it bubble.
  } else if (open.value && e.key === 'Escape') {
    close()
  }
}

function onFsKey(e: KeyboardEvent) {
  if (e.key.toLowerCase() === 'f' && !e.ctrlKey && !e.metaKey && !e.altKey) {
    const tag = (e.target as HTMLElement)?.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA') return
    e.preventDefault()
    toggleFullscreen()
  }
}

function toggleFullscreen() {
  if (document.fullscreenElement) {
    document.exitFullscreen().catch(() => {})
  } else {
    document.documentElement.requestFullscreen?.().catch(() => {})
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('keydown', onFsKey)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('keydown', onFsKey)
})

watch(open, () => {})
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; z-index: 2200;
  background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
}
.card {
  width: min(540px, 92vw);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 30px 80px rgba(0,0,0,0.5);
  color: var(--fg);
}
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
h3 { margin: 0; font-size: 16px; }
.close { background: transparent; border: 1px solid var(--border); color: var(--fg); width: 28px; height: 28px; border-radius: 50%; cursor: pointer; font-size: 18px; line-height: 1; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { text-align: left; padding: 4px 8px; color: var(--fg-soft); font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid var(--border); }
td { padding: 8px; border-bottom: 1px solid var(--border); vertical-align: middle; }
kbd {
  display: inline-block;
  background: var(--bg-sub);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 6px;
  font-family: monospace;
  font-size: 11px;
  color: var(--fg);
  box-shadow: 0 2px 0 var(--border);
  margin-right: 4px;
}
.footer { font-size: 11px; color: var(--fg-soft); margin: 12px 0 0; text-align: center; }

.help-enter-from, .help-leave-to { opacity: 0; }
.help-enter-active, .help-leave-active { transition: opacity 0.18s ease; }
</style>
