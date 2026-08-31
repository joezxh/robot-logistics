import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getMap } from '@/api/map'
import type { SiteGrid, ScenarioId } from '@/types'

export const useSiteGridStore = defineStore('siteGrid', () => {
  const grid = ref<SiteGrid | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadByScenario(id: ScenarioId): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const m = await getMap('tpl-' + id)
      const w = m.bounds?.w ?? 0
      const d = m.bounds?.d ?? 0
      grid.value = {
        site_id: 'tpl-' + id,
        bounds: { w, d },
        resolution: 2,
        cells: [],
      }
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  return { grid, loading, error, loadByScenario }
})
