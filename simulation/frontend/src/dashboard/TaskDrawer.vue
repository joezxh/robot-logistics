<template>
  <Teleport to="body">
    <Transition name="tdrawer">
      <div v-if="state.open.value" class="overlay" @click.self="close">
        <aside class="drawer" role="dialog" :aria-label="state.task.value?.task_id">
          <header v-if="state.task.value">
            <h3>任务 {{ state.task.value.task_id }}</h3>
            <button class="close" @click="close">×</button>
          </header>
          <div v-if="!state.task.value" class="loading">loading…</div>
          <div v-else class="content">
            <div class="meta">
              <span class="badge" :class="state.task.value.status">{{ state.task.value.status }}</span>
              <span class="meta-item">{{ state.task.value.type }}</span>
              <span class="meta-item">{{ state.task.value.device_id }}</span>
              <span class="meta-item">P{{ state.task.value.priority }}</span>
            </div>
            <p class="desc">{{ state.task.value.description }}</p>

            <h4>进度</h4>
            <div class="progress-bar"><span :style="{ width: (state.task.value.progress ?? 0) + '%' }"></span></div>
            <div class="trace-info">
              <code>{{ state.task.value.trace_id }}</code>
              <span class="time">{{ formatTime(state.task.value.created_at) }}</span>
            </div>

            <h4>事件</h4>
            <ul class="events">
              <li v-for="(e, i) in state.events.value" :key="i">
                <span class="ev-time">{{ formatTime(e.timestamp) }}</span>
                <span class="ev-module">{{ e.module }}</span>
                <span class="ev-msg">{{ e.message }}</span>
              </li>
              <li v-if="!state.events.value.length" class="empty">暂无事件</li>
            </ul>

            <div class="actions" v-if="canRollback">
              <button class="danger" @click="rollbackOne(state.task.value.task_id)" :disabled="state.busy.value">
                回滚此任务
              </button>
            </div>
          </div>
        </aside>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import axios from 'axios'
import { success, error as toastError } from '../composables/toast'
import { taskDrawerState as state, closeTaskDrawer, openTaskDrawer, type DrawerTask } from '../composables/taskDrawerBus'

const canRollback = computed(() => {
  const t = state.task.value
  return t && (t.status === 'completed' || t.status === 'failed')
})

function close() { closeTaskDrawer() }

async function rollbackOne(taskId: string) {
  if (state.busy.value) return
  state.busy.value = true
  try {
    await axios.post(`/api/tasks/${taskId}/rollback`)
    success('task rolled back')
    await openTaskDrawer(taskId)
  } catch (e) {
    toastError('rollback failed', (e as Error).message)
  } finally {
    state.busy.value = false
  }
}

function formatTime(ts: string) {
  if (!ts) return ''
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ts
  return d.toLocaleTimeString()
}

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
  position: fixed; inset: 0; z-index: 1300;
  background: rgba(0,0,0,0.4);
  display: flex; justify-content: flex-end;
}
.drawer {
  width: min(420px, 92vw);
  height: 100%;
  background: var(--bg-card);
  border-left: 1px solid var(--border);
  padding: 16px;
  overflow-y: auto;
  box-shadow: -10px 0 30px rgba(0,0,0,0.4);
  color: var(--fg);
}
header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
h3 { margin: 0; font-size: 14px; color: var(--fg); }
h4 { margin: 16px 0 6px; font-size: 12px; color: var(--fg-soft); text-transform: uppercase; letter-spacing: 0.5px; }
.close { background: transparent; border: 1px solid var(--border); color: var(--fg); width: 28px; height: 28px; border-radius: 50%; cursor: pointer; font-size: 18px; line-height: 1; }
.loading { padding: 24px; color: var(--fg-soft); }
.meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 6px; }
.badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.badge.running { background: #5eb0ff; color: #0b1220; }
.badge.completed { background: var(--good); color: white; }
.badge.pending { background: var(--bg-sub); color: var(--fg); }
.badge.failed { background: var(--bad); color: white; }
.badge.reverted { background: var(--warn); color: white; }
.meta-item { font-size: 11px; color: var(--fg-soft); }
.desc { font-size: 13px; margin: 0 0 12px; color: var(--fg); }
.progress-bar { background: var(--bg-sub); height: 6px; border-radius: 3px; overflow: hidden; margin: 8px 0; }
.progress-bar span { display: block; height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-soft)); transition: width 0.4s ease; }
.trace-info { display: flex; gap: 8px; align-items: center; font-size: 11px; color: var(--fg-soft); }
.trace-info code { font-family: monospace; color: var(--accent); }
.events { list-style: none; padding: 0; margin: 0; max-height: 280px; overflow-y: auto; }
.events li { display: flex; gap: 8px; align-items: baseline; padding: 4px 0; font-size: 12px; border-bottom: 1px dashed var(--border); }
.events .empty { color: var(--fg-soft); }
.ev-time { font-family: monospace; color: var(--fg-soft); width: 80px; flex-shrink: 0; }
.ev-module { color: var(--accent); width: 80px; flex-shrink: 0; font-weight: 600; }
.ev-msg { color: var(--fg); flex: 1; word-break: break-word; }
.actions { margin-top: 18px; display: flex; gap: 8px; }
.actions button { padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-sub); color: var(--fg); cursor: pointer; font-size: 13px; }
.actions button.danger { background: var(--bad); color: white; border-color: var(--bad); }
.actions button:disabled { opacity: 0.6; cursor: progress; }

.tdrawer-enter-from .drawer { transform: translateX(100%); }
.tdrawer-leave-to .drawer { transform: translateX(100%); }
.tdrawer-enter-active .drawer, .tdrawer-leave-active .drawer { transition: transform 0.22s ease; }
.tdrawer-enter-from, .tdrawer-leave-to { background: rgba(0,0,0,0); }
.tdrawer-enter-active, .tdrawer-leave-active { transition: background 0.22s ease; }
</style>
