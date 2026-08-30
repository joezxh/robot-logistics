import type { ItemStock } from './warehouse'
import type { DockSlot } from './logistics'

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
  /** Business flow — what the simulation backend models. */
  direction: 'inbound' | 'outbound'
  /**
   * Compass facing — what RCS's FloorShell models. The two are different
   * concepts (flow vs. orientation), so both are carried rather than guessing
   * one from the other. Populated by the FloorShell adapter.
   */
  facing?: 'N' | 'S' | 'E' | 'W'
}

export type FacilityKind = 'charger' | 'sorting' | 'packing' | 'qc' | 'entrance' | 'returns'

export interface FacilityPlacement {
  ref: string
  kind: FacilityKind
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
  // Optional: the backend may inline zone geometry in the blueprint, in which
  // case `ThreeEngine.buildShell` uses it to reposition `FloorFull.zones`.
  // Optional so the blueprint stays valid when zones live at the top level.
  zones?: Zone[]
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

// `DockSlot` lives in ./logistics — that version is a superset (it also carries
// the optional `task`/`vehicle` links). Having both made `types/index.ts` fail
// with TS2308 on the `export *` re-export; the extra fields are optional, so
// consumers of the narrower shape are unaffected.
