import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  listTemplates,
  seedTemplates,
  type MapTemplateInfo,
} from '@/api/map'

/**
 * Catalogue of database-backed unified-map templates.
 *
 * Templates live in the backend `robot_unified_maps` table (flagged
 * `is_template`) and are served by GET /api/rcs/maps/templates, so adding one
 * server-side needs no UI change. Selection is keyed by `map_id`.
 *
 * The store only tracks the catalogue and the selection; the FloorShell itself
 * belongs to `floorShell.loadBySite(template.map_id)`.
 */
export const useScenarioStore = defineStore('scenario', () => {
  const templates = ref<MapTemplateInfo[]>([])
  /** Template map_id, e.g. "tpl-ecommerce". */
  const selected = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadTemplates(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      templates.value = await listTemplates()
      // Seeding is idempotent, so calling it on an empty catalogue is a safe
      // way to self-heal a fresh database without an extra ops step.
      if (templates.value.length === 0) {
        await seedTemplates()
        templates.value = await listTemplates()
      }
      if (!selected.value && templates.value.length > 0) {
        selected.value = templates.value[0].map_id
      }
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  function select(mapId: string): void {
    selected.value = mapId
  }

  const selectedTemplate = computed<MapTemplateInfo | null>(
    () => templates.value.find((t) => t.map_id === selected.value) ?? null,
  )

  function templateByKey(mapId: string | null): MapTemplateInfo | null {
    if (!mapId) return null
    return templates.value.find((t) => t.map_id === mapId) ?? null
  }

  return {
    templates,
    selected,
    selectedTemplate,
    loading,
    error,
    loadTemplates,
    select,
    templateByKey,
  }
})
