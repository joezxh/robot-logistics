import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  listDevices,
  getDeviceState,
  sendCommand,
  estop as estopApi,
  clearEstop as clearEstopApi,
  controlHealth,
} from '@/api/control'
import type { DeviceProfile, DeviceState, CommandRequest } from '@/types'

export const useDeviceStore = defineStore('devices', () => {
  const devices = ref<DeviceProfile[]>([])
  const states = ref<Record<string, DeviceState>>({})
  const health = ref<{ running: boolean }>({ running: false })
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastCommand = ref<string | null>(null)

  async function loadRegistry(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const res = await listDevices()
      devices.value = res.devices
      health.value = await controlHealth().catch(() => ({ running: false }))
    } catch (e) {
      error.value = (e as Error).message
    } finally {
      loading.value = false
    }
  }

  async function refreshState(deviceId: string): Promise<void> {
    try {
      states.value[deviceId] = await getDeviceState(deviceId)
    } catch {
      /* device offline in sim */
    }
  }

  async function runCommand(deviceId: string, cmd: CommandRequest): Promise<void> {
    error.value = null
    try {
      const res = await sendCommand(deviceId, cmd)
      lastCommand.value = `${cmd.type} → ${res.status}`
      await refreshState(deviceId)
    } catch (e) {
      error.value = (e as Error).message
    }
  }

  async function estop(deviceId: string): Promise<void> {
    await estopApi(deviceId)
    await refreshState(deviceId)
  }

  async function clearEstop(deviceId: string): Promise<void> {
    await clearEstopApi(deviceId)
    await refreshState(deviceId)
  }

  return { devices, states, health, loading, error, lastCommand, loadRegistry, refreshState, runCommand, estop, clearEstop }
})
