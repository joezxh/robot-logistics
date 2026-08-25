// Floor shell blueprint types — mirror rcs_backend.models.floor_shell.

export interface Bounds {
  w: number
  d: number
  h?: number
}

export interface TempRange {
  min: number
  max: number
}

export type WallKind = 'wall' | 'glass' | 'rack' | 'fence'

export interface WallSegment {
  id: string
  x0: number
  z0: number
  x1: number
  z1: number
  h?: number
  kind?: WallKind
}

export type HazardLevel = 'none' | 'low' | 'medium' | 'high'

export interface Zone {
  id: string
  ref: string
  type: string
  x: number
  z: number
  w: number
  d: number
  name?: string | null
  site_node_ids?: string[]
  temperature_range?: TempRange | null
  batch_tracking?: boolean
  hazard_level?: HazardLevel | null
  customs_regulated?: boolean
  current_load_pct?: number
}

export interface Facility {
  id: string
  ref: string
  type: string
  x: number
  z: number
  w: number
  d: number
  h?: number
}

export interface Dock {
  id: string
  ref: string
  x: number
  z: number
  direction?: 'N' | 'S' | 'E' | 'W'
  door_w?: number
}

export interface Corridor {
  id: string
  from_zone: string
  to_zone: string
  w?: number
  bidirectional?: boolean
}

export type MarkingKind = 'lane' | 'stop' | 'crossing' | 'work_zone' | 'evac'

export interface Marking {
  id: string
  kind?: MarkingKind
  points?: number[][]
  color?: string
}

export interface Floor {
  id: string
  z: number
  bounds: Bounds
  walls?: WallSegment[]
  zones?: Zone[]
  facilities?: Facility[]
}

export interface FloorShell {
  bounds: Bounds
  walls?: WallSegment[]
  zones?: Zone[]
  facilities?: Facility[]
  docks?: Dock[]
  corridors?: Corridor[]
  markings?: Marking[]
  metadata?: Record<string, unknown>
  floors?: Floor[]
}

// 23 zone types covering 6 scenarios (mirrors floor_shell.ZONE_TYPES).
export const ZONE_TYPES = [
  // E-commerce
  'flow_rack', 'high_rack', 'mezzanine', 'automated', 'temp', 'temp_bagged', 'returns',
  // Manufacturing
  'production_line', 'wip_buffer', 'parts_storage', 'staging',
  // Cold-chain
  'cold_zone', 'frozen_zone', 'ambient_zone', 'loading_bay',
  // Port
  'container_yard', 'customs_area',
  // Reverse logistics
  'returns_received', 'qc_staging', 'reshelving', 'disposal',
  // Multi-floor
  'floor_1', 'floor_2', 'floor_3', 'elevator_shaft',
] as const

export type ZoneType = (typeof ZONE_TYPES)[number]

export function isZoneType(value: string): value is ZoneType {
  return (ZONE_TYPES as readonly string[]).includes(value)
}
