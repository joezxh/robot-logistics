import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  listWarehouseTemplates,
  seedWarehouseTemplates,
  type WarehouseTemplateInfo,
} from '@/api/warehouseTemplates'

/**
 * Catalogue of database-backed warehouse templates.
 *
 * These replace the six hard-coded demo scenarios on the map page. Templates
 * live in the backend (robot_topology_shell + robot_topology_grid +
 * robot_site_maps, flagged `is_template`) and are served by
 * GET /api/rcs/maps/templates, so adding one server-side needs no UI change.
 *
 * The store only tracks the catalogue and the selection; the FloorShell itself
 * belongs to `floorShell.loadBySite(template.site_id)`.
 */
export const useScenarioStore = defineStore('scenario', () => {
  const templates = ref<WarehouseTemplateInfo[]>([])
  /** Template key, e.g. "port_terminal". */
  const selected = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function loadTemplates(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      templates.value = await listWarehouseTemplates()
      // Seeding is idempotent, so calling it on an empty catalogue is a safe
      // way to self-heal a fresh database without an extra ops step.
      if (templates.value.length === 0) {
        await seedWarehouseTemplates()
        templates.value = await listWarehouseTemplates()
      }
      if (!selected.value && templates.value.length > 0) {
        selected.value = templates.value[0].key
      }
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  function select(key: string): void {
    selected.value = key
  }

  const selectedTemplate = computed<WarehouseTemplateInfo | null>(
    () => templates.value.find((t) => t.key === selected.value) ?? null,
  )

  function templateByKey(key: string | null): WarehouseTemplateInfo | null {
    if (!key) return null
    return templates.value.find((t) => t.key === key) ?? null
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
