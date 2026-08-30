import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getShell } from '@/api/topologyShell'
import { importWarehouseTheatre, previewWarehouseTheatre } from '@/api/warehouse'
import type { FloorShell } from '@/types'
import type { WarehouseImportResult, WarehousePreview } from '@/api/warehouse'

export const useWarehouseStore = defineStore('warehouse', () => {
  const shell = ref<FloorShell | null>(null)
  const preview = ref<WarehousePreview | null>(null)
  const importResult = ref<WarehouseImportResult | null>(null)
  const loading = ref(false)
  const importing = ref(false)
  const error = ref<string | null>(null)

  const SITE_ID = 'warehouse-theatre-3d'

  /** Load the previously-imported warehouse shell from backend */
  async function loadWarehouse(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      shell.value = await getShell(SITE_ID)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  /** Preview the conversion without saving */
  async function loadPreview(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      preview.value = await previewWarehouseTheatre()
      shell.value = preview.value.shell as FloorShell
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  /** Trigger the import and then load the saved shell */
  async function doImport(): Promise<void> {
    importing.value = true
    error.value = null
    try {
      importResult.value = await importWarehouseTheatre()
      // Reload the shell after import
      shell.value = await getShell(SITE_ID)
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      importing.value = false
    }
  }

  return {
    shell, preview, importResult,
    loading, importing, error,
    loadWarehouse, loadPreview, doImport,
  }
})
