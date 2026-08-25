import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/devices'
import type { DeviceRow } from '@/types'

export const useAdminDeviceStore = defineStore('admin-devices', () => {
  const devices = ref<DeviceRow[]>([])
  const loading = ref(false)
  const selectedId = ref<string | null>(null)

  async function load() {
    loading.value = true
    try { devices.value = await api.listDevices() } finally { loading.value = false }
  }
  async function save(id: string, body: Partial<DeviceRow>) {
    await api.updateDevice(id, body)
    await load()
  }
  async function create(body: DeviceRow) {
    await api.createDevice(body)
    await load()
  }
  async function remove(id: string) {
    await api.deleteDevice(id)
    await load()
  }

  return { devices, loading, selectedId, load, save, create, remove }
})