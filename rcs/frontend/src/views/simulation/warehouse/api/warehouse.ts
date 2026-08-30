/**
 * Warehouse API Client
 * Fetches data from FastAPI backend
 */
import type {
  WarehouseGroup,
  Slot,
  FloorFull,
  LogisticsStats,
  LogisticsTask,
  AGVGrid,
} from '../types'

const API_BASE = '/api/warehouse'

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export async function fetchGroups(): Promise<WarehouseGroup[]> {
  const data = await fetchJSON<{ groups: WarehouseGroup[] }>(`${API_BASE}/groups`)
  return data.groups
}

export async function fetchSlots(groupId?: string): Promise<Slot[]> {
  const url = groupId ? `${API_BASE}/slots?group_id=${encodeURIComponent(groupId)}` : `${API_BASE}/slots`
  const data = await fetchJSON<{ slots: Slot[] }>(url)
  return data.slots
}

export async function fetchFloorFull(groupId: string): Promise<FloorFull | null> {
  const data = await fetchJSON<{ floor_full: FloorFull | null }>(
    `${API_BASE}/floor?group_id=${encodeURIComponent(groupId)}`
  )
  return data.floor_full
}

export async function fetchLogisticsStats(): Promise<LogisticsStats> {
  const data = await fetchJSON<{ stats: LogisticsStats }>(`${API_BASE}/logistics/stats`)
  return data.stats
}

export async function fetchLogisticsTasks(): Promise<LogisticsTask[]> {
  const data = await fetchJSON<{ tasks: LogisticsTask[] }>(`${API_BASE}/logistics/tasks`)
  return data.tasks
}

export async function fetchAGVGrid(groupId?: string): Promise<AGVGrid> {
  const url = groupId ? `${API_BASE}/agv/grid?group_id=${encodeURIComponent(groupId)}` : `${API_BASE}/agv/grid`
  const data = await fetchJSON<{ grid: AGVGrid }>(url)
  return data.grid
}

export async function saveAGVGrid(grid: AGVGrid, groupId: string): Promise<void> {
  await fetch(`${API_BASE}/agv/grid?group_id=${encodeURIComponent(groupId)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(grid),
  })
}

export async function fetchWarehouseData(): Promise<{
  groups: WarehouseGroup[]
  slots: Slot[]
  floorFull: FloorFull | null
  stats: LogisticsStats
  tasks: LogisticsTask[]
  agvGrid: AGVGrid | null
}> {
  const [groups, slots, stats, tasks] = await Promise.all([
    fetchGroups(),
    fetchSlots(),
    fetchLogisticsStats(),
    fetchLogisticsTasks(),
  ])

  let floorFull: FloorFull | null = null
  let agvGrid: AGVGrid | null = null

  if (groups.length > 0) {
    ;[floorFull, agvGrid] = await Promise.all([
      fetchFloorFull(groups[0].id),
      fetchAGVGrid(groups[0].id),
    ])
  }

  return { groups, slots, floorFull, stats, tasks, agvGrid }
}

export async function generateDemoData(): Promise<void> {
  await fetch(`${API_BASE}/demo/generate`, { method: 'POST' })
}
