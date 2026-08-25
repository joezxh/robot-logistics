import { http } from './http'
import type { DeviceRow } from '@/types'

export const listDevices = () => http.get<DeviceRow[]>('/devices')
export const getDevice = (id: string) => http.get<DeviceRow>(`/devices/${encodeURIComponent(id)}`)
export const updateDevice = (id: string, body: Partial<DeviceRow>) =>
  http.put<DeviceRow>(`/devices/${encodeURIComponent(id)}`, body)
export const createDevice = (body: DeviceRow) => http.post<DeviceRow>('/devices', body)
export const deleteDevice = (id: string) => http.delete<void>(`/devices/${encodeURIComponent(id)}`)