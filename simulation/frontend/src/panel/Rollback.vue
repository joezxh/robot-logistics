<template>
  <div class="card">
    <h3>{{ t.rollback }}</h3>
    <p class="hint">{{ t.rollback_hint }}</p>
    <label class="row">
      <span>{{ t.rollback }}</span>
      <input type="number" v-model.number="limit" min="1" max="20" />
    </label>
    <button class="primary" :disabled="busy" @click="ask = true">{{ busy ? t.rollback_busy : `${t.rollback} ${limit}` }}</button>
    <p v-if="feedback" class="feedback">{{ feedback }}</p>
    <ul v-if="results.length" class="results">
      <li v-for="r in results" :key="r.task.task_id">
        <code>{{ r.task.task_id }}</code> · <span class="module">{{ r.task.type }}</span>
      </li>
    </ul>

    <div v-if="ask" class="modal" @click.self="ask = false">
      <div class="dialog">
        <h4>{{ t.rollback }} {{ limit }}</h4>
        <p>设备位置 / 电池 / 路径将恢复到任务执行前的状态。该操作不可撤销。</p>
        <div class="actions">
          <button @click="ask = false">{{ t.cancel }}</button>
          <button class="danger" :disabled="busy" @click="confirm">{{ t.confirm }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'
import { useI18n, tf } from '../i18n'
import { success, error as toastError } from '../composables/toast'

const { t } = useI18n()
const limit = ref(3)
const busy = ref(false)
const feedback = ref('')
const ask = ref(false)
const results = ref<Array<{ task: { task_id: string; type: string } }>>([])

async function confirm() {
  busy.value = true
  ask.value = false
  feedback.value = ''
  try {
    const res = await axios.post('/api/tasks/rollback', { limit: limit.value })
    results.value = res.data
    feedback.value = tf(t.value.toast.rollback_done, { n: res.data.length })
    success(tf(t.value.toast.rollback_done, { n: res.data.length }))
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    feedback.value = detail ? `回滚失败：${detail}` : t.value.create_fail
    toastError(t.value.rollback, detail ?? '')
  } finally {
    busy.value = false
  }
}
</script>

<style scoped>
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; color: var(--fg); }
.card h3 { margin: 0 0 4px; font-size: 14px; color: var(--fg-muted); }
.hint { margin: 0 0 8px; font-size: 12px; color: var(--fg-soft); }
.row { display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 12px; color: var(--fg-soft); }
.row input { width: 64px; background: var(--bg-sub); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; font-size: 12px; }
button.primary { width: 100%; background: var(--bad); color: white; border: none; border-radius: 4px; padding: 8px; cursor: pointer; font-weight: 600; }
button.primary:hover:not(:disabled) { background: #d04a4a; }
button.primary:disabled { opacity: 0.6; cursor: progress; }
.feedback { margin: 6px 0 0; font-size: 12px; color: var(--good); }
.results { list-style: none; margin: 6px 0 0; padding: 0; font-size: 12px; color: var(--fg); }
.results li { padding: 2px 0; }
.results .module { color: var(--accent-soft); }
.results code { color: var(--accent); }

.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 200; }
.dialog { width: 360px; max-width: 92vw; background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; box-shadow: 0 16px 36px rgba(0,0,0,0.35); color: var(--fg); }
.dialog h4 { margin: 0 0 6px; font-size: 14px; }
.dialog p { margin: 0 0 12px; font-size: 13px; color: var(--fg-soft); }
.actions { display: flex; gap: 8px; justify-content: flex-end; }
.actions button { padding: 6px 14px; border-radius: 4px; border: 1px solid var(--border); background: var(--bg-sub); color: var(--fg); cursor: pointer; font-size: 12px; }
.actions button.danger { background: var(--bad); border-color: var(--bad); color: white; }
.actions button.danger:disabled { opacity: 0.6; cursor: progress; }
</style>
