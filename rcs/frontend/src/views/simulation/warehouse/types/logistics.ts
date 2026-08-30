import type { Zone, Facility, Dock, ShellBlueprint } from './zone'

export interface FloorFull {
  shell?: ShellBlueprint
  zones?: Zone[]
  facilities?: Facility[]
  docks?: Dock[]
}

export type TaskType = 'inbound' | 'outbound' | 'transfer' | 'replenishment'
export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'

export interface TaskItem {
  item_code: string
  item_name: string
  qty: number
  uom: string
}

export interface LogisticsTask {
  ref: string
  type: TaskType
  status: TaskStatus
  priority: number
  source_dock?: string
  target_dock?: string
  items: TaskItem[]
  assigned_vehicle?: string
  eta?: number
  completed_at?: number
  created_at: number
}

export interface LogisticsStats {
  total_inbound: number
  total_outbound: number
  avg_processing_time: number
  dock_utilization: number
}

export interface DockDetail {
  ref: string
  direction: 'inbound' | 'outbound'
  name: string
  x: number
  z: number
  slots: DockSlot[]
  utilization: number
}

export interface DockSlot {
  ref: string
  status: 'available' | 'occupied' | 'scheduled'
  task?: string
  vehicle?: string
}
