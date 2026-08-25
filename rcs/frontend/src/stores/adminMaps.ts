import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/maps'
import type { MapRow, MapVersionRow } from '@/types'

export const useAdminMapStore = defineStore('admin-maps', () => {
  const maps = ref<MapRow[]>([])
  const versions = ref<MapVersionRow[]>([])
  const current = ref<MapRow | null>(null)
  const loading = ref(false)

  async function load() {
    loading.value = true
    try { maps.value = await api.listMaps() } finally { loading.value = false }
  }
  async function select(id: string) {
    current.value = await api.getMap(id)
    versions.value = await api.listVersions(id)
  }
  async function importJson(id: string, payload: { nodes: any[]; edges: any[] }) {
    await api.importMap(id, payload)
    await select(id)
  }
  async function exportJson(id: string): Promise<MapRow | null> {
    return await api.exportMap(id)
  }
  async function restore(mapId: string, versionId: string) {
    await api.restoreVersion(mapId, versionId)
    await select(mapId)
  }
  async function create(body: { name: string }) {
    await api.createMap({ name: body.name, nodes: [], edges: [] })
    await load()
  }
  async function remove(id: string) {
    await api.deleteMap(id)
    await load()
  }

  return { maps, versions, current, loading, load, select, importJson, exportJson, restore, create, remove }
})