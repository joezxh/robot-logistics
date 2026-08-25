import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getShell } from '@/api/topologyShell'
import { getTemplate } from '@/api/templates'
import type { FloorShell, ScenarioId } from '@/types'

export const useFloorShellStore = defineStore('floorShell', () => {
  const shell = ref<FloorShell | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadByScenario(id: ScenarioId): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const b = await getTemplate(id)
      shell.value = b.shell
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function loadBySite(siteId: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      shell.value = await getShell(siteId)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  return { shell, loading, error, loadByScenario, loadBySite }
})
