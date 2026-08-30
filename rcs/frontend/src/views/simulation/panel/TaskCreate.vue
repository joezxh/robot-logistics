<template>
  <div class="card">
    <h3>{{ t.create_task }}</h3>
    <form @submit.prevent="submit">
      <label>
        <span>{{ t.task_type }}</span>
        <select v-model="type">
          <option value="dock_loading">{{ t.type_dock_loading }}</option>
          <option value="agv_transport">{{ t.type_agv_transport }}</option>
          <option value="warehouse_storage">{{ t.type_warehouse_storage }}</option>
        </select>
      </label>
      <label>
        <span>{{ t.priority }}</span>
        <select v-model.number="priority">
          <option :value="2">HIGH</option>
          <option :value="3">NORMAL</option>
          <option :value="4">LOW</option>
        </select>
      </label>
      <label class="full">
        <span>{{ t.description }}</span>
        <input v-model="description" :placeholder="descriptionPh" />
      </label>
      <label class="full">
        <span>{{ t.device }}</span>
        <select v-model="deviceId">
          <option value="robot-01">robot-01 · 集装箱装卸机器人</option>
          <option value="agv-01">agv-01 · AGV 转运车</option>
          <option value="agv-02">agv-02 · AGV 转运车</option>
          <option value="stacker-01">stacker-01 · 立库堆垛机</option>
        </select>
      </label>
      <button type="submit" class="full">{{ t.submit }}</button>
      <p v-if="feedback" class="feedback">{{ feedback }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import axios from 'axios'
import { useI18n } from '../i18n'
import { success, error as toastError } from '../composables/toast'

const { t } = useI18n()
const type = ref('agv_transport')
const description = ref('')
const priority = ref(3)
const deviceId = ref('agv-01')
const feedback = ref('')

const descriptionPh = computed(() => {
  const map: Record<string, string> = {
    dock_loading: t.value.type_dock_loading,
    agv_transport: t.value.type_agv_transport,
    warehouse_storage: t.value.type_warehouse_storage,
  }
  return map[type.value] ?? ''
})

async function submit() {
  feedback.value = ''
  try {
    const res = await axios.post('/api/tasks', {
      type: type.value,
      description: description.value || type.value,
      priority: priority.value,
      device_id: deviceId.value,
    })
    feedback.value = t.value.create_success + ' ' + res.data.task_id
    success(t.value.toast.task_created, res.data.task_id)
    description.value = ''
  } catch (e) {
    feedback.value = t.value.create_fail
    toastError(t.value.toast.backend_offline, (e as Error).message)
  }
}
</script>

<style scoped>
.card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
.card h3 { margin: 0 0 8px; font-size: 14px; color: var(--fg); }
form { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 10px; color: var(--fg-soft); text-transform: uppercase; letter-spacing: 0.5px; }
label.full { grid-column: span 2; }
select, input { background: var(--bg-sub); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 6px 8px; font-size: 12px; transition: border 0.2s ease; }
select:focus, input:focus { outline: none; border-color: var(--accent); }
button.full { grid-column: span 2; background: linear-gradient(90deg, var(--good), #2aa15c); color: white; border: none; border-radius: 4px; padding: 10px; cursor: pointer; font-weight: 600; font-size: 13px; transition: transform 0.1s ease; }
button.full:hover { transform: translateY(-1px); }
button.full:active { transform: translateY(0); }
.feedback { grid-column: span 2; margin: 6px 0 0; font-size: 12px; padding: 6px 8px; background: var(--bg-sub); border-radius: 4px; color: var(--good); }
</style>
