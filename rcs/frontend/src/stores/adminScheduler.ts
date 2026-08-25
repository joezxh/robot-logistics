import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/scheduler'
import type { SchedulerConfig, SchedulerWeights } from '@/types'

export const useAdminSchedulerStore = defineStore('admin-scheduler', () => {
  const configs = ref<SchedulerConfig[]>([])
  const active = ref<SchedulerConfig | null>(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    try {
      configs.value = await api.listConfigs()
      try { active.value = await api.getActive() } catch { active.value = null }
    } finally { loading.value = false }
  }
  async function create(body: { name: string; strategy?: string; weights: SchedulerWeights }) {
    await api.createConfig(body)
    await load()
  }
  async function update(id: string, body: Partial<SchedulerConfig>) {
    await api.updateConfig(id, body)
    await load()
  }
  async function activate(id: string) {
    await api.activateConfig(id)
    await load()
  }

  return { configs, active, loading, load, create, update, activate }
})