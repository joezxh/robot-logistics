/**
 * RCS warehouse inventory client.
 *
 * Reads the WMS inventory layer (slots / items / AGV / tasks) from the RCS
 * backend at `/api/rcs/warehouse/inventory/*`. When the geometry was imported
 * into RCS, this is the authoritative source and the warehouse view flips its
 * data-source badge to green `RCS`.
 */
import type { Slot, WarehouseGroup, LogisticsTask, LogisticsStats } from '../types'

const API_BASE = '/api/rcs/warehouse/inventory'

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`RCS inventory API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function fetchRcsGroups(): Promise<WarehouseGroup[]> {
  const data = await fetchJSON<{ groups: WarehouseGroup[] }>(`${API_BASE}/groups`)
  return data.groups
}

export async function fetchRcsSlots(groupId?: string): Promise<Slot[]> {
  const url = groupId ? `${API_BASE}/slots?group_id=${encodeURIComponent(groupId)}` : `${API_BASE}/slots`
  const data = await fetchJSON<{ slots: Slot[] }>(url)
  return data.slots
}

export async function fetchRcsTasks(): Promise<LogisticsTask[]> {
  const data = await fetchJSON<{ tasks: LogisticsTask[] }>(`${API_BASE}/tasks`)
  return data.tasks
}

export async function fetchRcsStats(): Promise<LogisticsStats> {
  const data = await fetchJSON<{ stats: LogisticsStats }>(`${API_BASE}/stats`)
  return data.stats
}

export async function seedRcsInventory(): Promise<void> {
  await fetch(`${API_BASE}/seed`, { method: 'POST' })
}
