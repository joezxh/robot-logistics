import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listTemplates, getTemplate, type TemplateBundle } from '@/api/templates'
import type { ScenarioId, ScenarioTemplateInfo } from '@/types'

export const useScenarioStore = defineStore('scenario', () => {
  const templates = ref<ScenarioTemplateInfo[]>([])
  const selected = ref<ScenarioId | null>(null)
  const bundle = ref<TemplateBundle | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadTemplates(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      templates.value = await listTemplates()
      if (!selected.value && templates.value.length > 0) {
        selected.value = templates.value[0].scenario_id
      }
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  function select(id: ScenarioId): void {
    selected.value = id
    bundle.value = null
  }

  async function loadBundle(id: ScenarioId): Promise<void> {
    loading.value = true
    error.value = null
    try {
      bundle.value = await getTemplate(id)
      selected.value = id
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  return { templates, selected, bundle, loading, error, loadTemplates, select, loadBundle }
})
