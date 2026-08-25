import { http } from './http'
import type { CommandLogRow, EventLogRow } from '@/types'

export const listCommands = (deviceId?: string, limit = 100) => {
  const q = new URLSearchParams()
  if (deviceId) q.set('device_id', deviceId)
  q.set('limit', String(limit))
  return http.get<CommandLogRow[]>(`/logs/commands?${q.toString()}`)
}
export const listEvents = (level?: string, limit = 100) => {
  const q = new URLSearchParams()
  if (level) q.set('level', level)
  q.set('limit', String(limit))
  return http.get<EventLogRow[]>(`/logs/events?${q.toString()}`)
}