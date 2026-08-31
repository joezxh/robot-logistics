import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMap } from '@/api/map'
import type { FloorShell, ScenarioId } from '@/types'

export const useFloorShellStore = defineStore('floorShell', () => {
  const shell = ref<FloorShell | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadByScenario(id: ScenarioId): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const m = await getMap('tpl-' + id)
      shell.value = m.geometry
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
      const m = await getMap(siteId)
      shell.value = m.geometry
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  return { shell, loading, error, loadByScenario, loadBySite }
})
