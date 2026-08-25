// REST client for the embedded control runtime: /api/rcs/registry,
// /api/rcs/{device_id}/command|state|estop|clear_estop, /api/rcs/_health
import { http } from './http'
import type {
  RegistryResponse,
  DeviceState,
  CommandRequest,
  CommandResult,
  ControlHealth,
} from '@/types'

export function listDevices(): Promise<RegistryResponse> {
  return http.get<RegistryResponse>('/registry')
}

export function getDeviceState(deviceId: string): Promise<DeviceState> {
  return http.get<DeviceState>(`/${encodeURIComponent(deviceId)}/state`)
}

export function sendCommand(deviceId: string, cmd: CommandRequest): Promise<CommandResult> {
  return http.post<CommandResult>(`/${encodeURIComponent(deviceId)}/command`, cmd)
}

export function estop(deviceId: string): Promise<CommandResult> {
  return http.post<CommandResult>(`/${encodeURIComponent(deviceId)}/estop`, {})
}

export function clearEstop(deviceId: string): Promise<CommandResult> {
  return http.post<CommandResult>(`/${encodeURIComponent(deviceId)}/clear_estop`, {})
}

export function controlHealth(): Promise<ControlHealth> {
  return http.get<ControlHealth>('/_health')
}
