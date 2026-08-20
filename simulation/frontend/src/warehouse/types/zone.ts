export type ZoneType = 'rack' | 'flow_rack' | 'automated' | 'high_rack' | 'mezzanine' | 'temp' | 'temp_bagged' | 'returns'

export interface Bounds {
  w: number
  d: number
}

export interface Wall {
  x0: number
  z0: number
  x1: number
  z1: number
  h: number
  dock_bumper?: boolean
}

export interface DockPlacement {
  ref: string
  x: number
  z: number
  w: number
  d: number
  direction: 'inbound' | 'outbound'
}

export interface FacilityPlacement {
  ref: string
  kind: 'charger' | 'sorting' | 'packing' | 'qc' | 'entrance' | 'returns'
  x: number
  z: number
  w: number
  d: number
}

export interface Corridor {
  x0: number
  z0: number
  x1: number
  z1: number
  main?: boolean
}

export interface Marking {
  type: string
  pts: [number, number][]
  width: number
  color: number
  dashed?: boolean
}

export interface VehiclePlacement {
  ref: string
  x: number
  z: number
  w: number
  d: number
  flow: 'inbound' | 'outbound' | 'internal'
  cargo: string[]
}

export interface ShellBlueprint {
  bounds: Bounds
  walls: Wall[]
  docks: DockPlacement[]
  facilities: FacilityPlacement[]
  corridors: Corridor[]
  markings?: Marking[]
  vehicles?: VehiclePlacement[]
}

export interface Zone {
  ref: string
  type: ZoneType
  name?: string
  x: number
  z: number
  w: number
  d: number
  levels?: number
  cells?: ZoneCell[]
  slots?: ZoneSlot[]
  bulks?: ZoneBulk[]
  occ?: { total: number; occupied: number }
}

export interface ZoneCell {
  aisle: number
  row: number
  col: number
  level: number
  qty: number
}

export interface ZoneSlot {
  name: string
  occ?: number
  items?: ItemStock[]
}

export interface ZoneBulk {
  name: string
  qty: number
}

export interface Facility {
  ref: string
  kind: 'charger' | 'sorting' | 'packing' | 'qc' | 'entrance' | 'returns'
  name?: string
  x: number
  z: number
  w?: number
  d?: number
}

export interface Dock {
  ref: string
  direction: 'inbound' | 'outbound'
  name?: string
  x: number
  z: number
  w?: number
  d?: number
  slots?: DockSlot[]
}

export interface DockSlot {
  ref: string
  status: 'available' | 'occupied' | 'scheduled'
}
