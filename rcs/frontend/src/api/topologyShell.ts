// REST client for /api/rcs/topology/shell*
import { http } from './http'
import type { FloorShell } from '@/types'

export interface ShellSummary {
  site_id: string
  bounds: { w: number; d: number }
  zone_count: number
}

export function listShells(): Promise<ShellSummary[]> {
  return http.get<ShellSummary[]>('/topology/shell')
}

export function getShell(siteId: string): Promise<FloorShell> {
  return http.get<FloorShell>(`/topology/shell/${encodeURIComponent(siteId)}`)
}
