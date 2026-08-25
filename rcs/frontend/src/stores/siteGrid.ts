import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getTemplate } from '@/api/templates'
import type { SiteGrid, ScenarioId } from '@/types'

export const useSiteGridStore = defineStore('siteGrid', () => {
  const grid = ref<SiteGrid | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadByScenario(id: ScenarioId): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const b = await getTemplate(id)
      grid.value = b.grid
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  return { grid, loading, error, loadByScenario }
})
