// Admin module types (devices / maps / orders / planning / scheduler / logs).

export interface DeviceRow {
  device_id: string
  morphology: string
  robot_type?: string | null
  num_joints: number
  control_hz: number
  mode?: string | null
  limits: Record<string, number[]>
  home_joints: number[]
  spec: Record<string, unknown>
  status: string
  locked?: boolean
  created_at?: string | null
  updated_at?: string | null
}

export interface SiteNode {
  id: string
  pos: number[]
  type?: string
  capacity?: number
}

export interface SiteEdge {
  from: string
  to: string
  distance: number
  speed_limit?: number
  bidirectional?: boolean
}

export interface MapVersionRow {
  version_id: string
  version: number
  note: string | null
  created_at?: string | null
}

/** Unified map DTO returned by GET /api/rcs/maps/{id} and list endpoints. */
export interface UnifiedMapDTO {
  map_id: string
  name: string
  name_en?: string | null
  is_template: boolean
  kind?: string | null
  current_version: number
  bounds: { w: number; d: number } | null
  geometry: import('./floorShell').FloorShell
  topology: { nodes: SiteNode[]; edges: SiteEdge[] }
  semantic: Record<string, unknown>
  dynamic?: Record<string, unknown> | null
  created_at?: string | null
  updated_at?: string | null
}

/** Portable export bundle returned by GET /api/rcs/maps/{id}/export. */
export interface MapExportBundle {
  map_id: string
  name: string
  geometry: import('./floorShell').FloorShell
  topology: { nodes: SiteNode[]; edges: SiteEdge[] }
  semantic: Record<string, unknown>
}

export interface OrderItem {
  ref: string
  quantity: number
}

export interface OrderTask {
  node_id: string
  task_type: string
  slo_class: string
  depends_on: string[]
  status?: string
}

export interface OrderRow {
  order_id: string
  scenario_id?: string | null
  priority: number
  deadline?: number | null
  status: string
  items: OrderItem[]
  tasks: OrderTask[]
  created_at: number
}

export interface PlanningProfile {
  profile_id: string
  name: string
  algo: 'trapezoidal' | 'quintic' | string
  axes: number
  vel_max: number[]
  acc_max: number[]
  created_by?: string | null
  created_at?: string | null
}

export interface SchedulerWeights {
  w1: number
  w2: number
  w3: number
  w4: number
}

export interface SchedulerConfig {
  config_id: string
  name: string
  strategy: string
  weights: SchedulerWeights
  active: boolean
  created_at?: string | null
}

export interface CommandLogRow {
  cmd_id: string
  device_id: string
  cmd_type: string
  payload: Record<string, unknown>
  issued_by?: string | null
  result: string
  created_at?: string | null
}

export interface EventLogRow {
  event_id: string
  level: string
  source?: string | null
  message: string
  meta: Record<string, unknown>
  created_at?: string | null
}