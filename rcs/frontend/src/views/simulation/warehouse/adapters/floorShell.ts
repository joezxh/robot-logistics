/**
 * Adapter: RCS `FloorShell`  ->  renderer `ShellBlueprint`.
 *
 * WHY THIS EXISTS
 * ---------------
 * The warehouse theatre now has a single source of truth for *geometry*:
 * the RCS topology API, which stores a `FloorShell` per site. The simulation
 * backend still serves *inventory* (slot levels/items), logistics stats, the AGV
 * grid and warehouse CRUD — none of which exist in the RCS domain yet (its 12
 * tables are all robot-control: devices/orders/topology/planning/scheduling).
 *
 * So this adapter is deliberately the seam between the two layers:
 *
 *   FloorShell  (transport + persistence, owned by RCS)   -- this file -->
 *   ShellBlueprint (render structure, consumed by ThreeEngine)
 *
 * `ShellBlueprint` therefore stops being a wire format and becomes an internal
 * render shape. Inventory still arrives separately via `FloorFull.zones` and is
 * merged by `mergeShellIntoFloorFull()` below.
 *
 * MIGRATION NOTE
 * --------------
 * When RCS gains an inventory domain (slot/logistics tables), the only thing
 * that needs to change is where `FloorFull.zones`/`slots` come from. Nothing in
 * ThreeEngine or this file has to move.
 */
import type {
  FloorShell,
  Zone as RcsZone,
  WallSegment as RcsWall,
  Facility as RcsFacility,
  Dock as RcsDock,
  Corridor as RcsCorridor,
  Marking as RcsMarking,
} from '@/types'
import type {
  ShellBlueprint,
  Wall,
  Zone,
  ZoneType,
  FacilityPlacement,
  FacilityKind,
  DockPlacement,
  Corridor,
  Marking,
} from '../types'
import type { FloorFull } from '../types'

/** Fallbacks for fields RCS does not model but the renderer requires. */
const DEFAULT_WALL_H = 6
const DEFAULT_DOCK_W = 4
const DEFAULT_DOCK_D = 3
const DEFAULT_MARKING_WIDTH = 0.15
const DEFAULT_MARKING_COLOR = 0xfacc15

const SIM_ZONE_TYPES = [
  'rack', 'flow_rack', 'automated', 'high_rack', 'mezzanine', 'temp', 'temp_bagged', 'returns',
] as const

const SIM_FACILITY_KINDS = [
  'charger', 'sorting', 'packing', 'qc', 'entrance', 'returns',
] as const

/**
 * RCS models 23 zone types across 6 scenarios; the renderer supports 8 shelf
 * archetypes. RCS-only types collapse onto the closest renderable shape rather
 * than being dropped — geometry still renders, only the shelf styling differs.
 */
const ZONE_TYPE_MAP: Record<string, ZoneType> = {
  // E-commerce (1:1 with renderer)
  rack: 'rack',
  flow_rack: 'flow_rack',
  automated: 'automated',
  high_rack: 'high_rack',
  mezzanine: 'mezzanine',
  temp: 'temp',
  temp_bagged: 'temp_bagged',
  returns: 'returns',
  // Cold-chain
  cold_zone: 'temp',
  frozen_zone: 'temp',
  ambient_zone: 'rack',
  loading_bay: 'returns',
  // Manufacturing
  production_line: 'rack',
  wip_buffer: 'rack',
  parts_storage: 'rack',
  staging: 'rack',
  // Port
  container_yard: 'rack',
  customs_area: 'rack',
  // Reverse logistics
  returns_received: 'returns',
  qc_staging: 'rack',
  reshelving: 'rack',
  disposal: 'returns',
  // Multi-floor
  floor_1: 'rack',
  floor_2: 'rack',
  floor_3: 'rack',
  elevator_shaft: 'rack',
}

export function mapZoneType(type: string | undefined): ZoneType {
  if (!type) return 'rack'
  return ZONE_TYPE_MAP[type] ?? (SIM_ZONE_TYPES.includes(type as ZoneType) ? (type as ZoneType) : 'rack')
}

export function mapFacilityKind(type: string | undefined): FacilityKind {
  if (!type) return 'sorting'
  return (SIM_FACILITY_KINDS as readonly string[]).includes(type) ? (type as FacilityKind) : 'sorting'
}

function hexColorToInt(color: string | undefined, fallback: number): number {
  if (!color) return fallback
  const cleaned = color.replace('#', '').trim()
  // #RGB and #RRGGBB both parse fine as hex; guard against junk.
  if (!/^[0-9a-fA-F]{3,8}$/.test(cleaned)) return fallback
  const value = Number.parseInt(cleaned, 16)
  return Number.isFinite(value) ? value : fallback
}

/**
 * RCS supports multi-floor shells; the renderer currently renders one level.
 * Top-level geometry wins; if the shell puts everything on floors[0], use that.
 */
function resolveLevel(shell: FloorShell) {
  const hasTopLevel = (shell.zones?.length ?? 0) > 0 || (shell.walls?.length ?? 0) > 0
  const floor = !hasTopLevel && shell.floors?.length ? shell.floors[0] : undefined
  return {
    bounds: floor?.bounds ?? shell.bounds,
    walls: shell.walls?.length ? shell.walls : (floor?.walls ?? []),
    zones: shell.zones?.length ? shell.zones : (floor?.zones ?? []),
    facilities: shell.facilities?.length ? shell.facilities : (floor?.facilities ?? []),
  }
}

function toWalls(walls: RcsWall[]): Wall[] {
  // RCS carries `kind` (wall/glass/rack/fence); the renderer only needs geometry.
  return walls.map((w) => ({
    x0: w.x0,
    z0: w.z0,
    x1: w.x1,
    z1: w.z1,
    h: w.h ?? DEFAULT_WALL_H,
  }))
}

/**
 * Geometry only. Inventory (levels/cells/slots/bulks) stays with the simulation
 * backend for now; `occ` is seeded from RCS's `current_load_pct` so load-based
 * colouring still works even when no inventory data is present.
 */
function toZones(zones: RcsZone[]): Zone[] {
  return zones.map((z) => {
    const mapped: Zone = {
      ref: z.ref || z.id,
      type: mapZoneType(z.type),
      name: z.name ?? undefined,
      x: z.x,
      z: z.z,
      w: z.w,
      d: z.d,
    }
    if (typeof z.current_load_pct === 'number') {
      mapped.occ = { total: 100, occupied: z.current_load_pct }
    }
    return mapped
  })
}

function toFacilities(facilities: RcsFacility[]): FacilityPlacement[] {
  return facilities.map((f) => ({
    ref: f.ref || f.id,
    kind: mapFacilityKind(f.type),
    x: f.x,
    z: f.z,
    w: f.w,
    d: f.d,
  }))
}

/**
 * Direct MISMATCH, documented rather than silently mangled:
 *   sim  `direction` = business flow   ('inbound' | 'outbound')
 *   RCS  `direction` = compass facing  ('N' | 'S' | 'E' | 'W')
 * These are different concepts. We keep the RCS facing in `facing` and default
 * the business flow to 'outbound' (docks face outward in every built-in shell).
 */
function toDocks(docks: RcsDock[]): DockPlacement[] {
  return docks.map((d) => ({
    ref: d.ref || d.id,
    x: d.x,
    z: d.z,
    w: d.door_w ?? DEFAULT_DOCK_W,
    d: DEFAULT_DOCK_D, // RCS models a door width, not a dock depth.
    direction: 'outbound',
    facing: d.direction,
  }))
}

/**
 * RCS corridors are TOPOLOGICAL (zone -> zone); the renderer wants GEOMETRY
 * (a line segment). We derive the segment joining the two zone centres — a good
 * approximation for straight aisles, which is what every built-in shell uses.
 */
function toCorridors(corridors: RcsCorridor[], zones: RcsZone[]): Corridor[] {
  if (!corridors.length) return []
  const byKey = new Map<string, RcsZone>()
  for (const z of zones) {
    byKey.set(z.ref, z)
    byKey.set(z.id, z)
  }
  const out: Corridor[] = []
  for (const c of corridors) {
    const a = byKey.get(c.from_zone)
    const b = byKey.get(c.to_zone)
    if (!a || !b) continue // dangling reference — skip rather than draw a bogus line
    out.push({
      x0: a.x + a.w / 2,
      z0: a.z + a.d / 2,
      x1: b.x + b.w / 2,
      z1: b.z + b.d / 2,
      main: c.bidirectional ?? true,
    })
  }
  return out
}

function toMarkings(markings: RcsMarking[]): Marking[] {
  return markings.map((m) => ({
    type: m.kind ?? 'lane',
    pts: (m.points ?? []).map((p) => [p[0], p[1]] as [number, number]),
    width: DEFAULT_MARKING_WIDTH, // not modelled by RCS
    color: hexColorToInt(m.color, DEFAULT_MARKING_COLOR),
  }))
}

/** Convert an RCS `FloorShell` into the renderer's `ShellBlueprint`. */
export function toShellBlueprint(shell: FloorShell): ShellBlueprint {
  const level = resolveLevel(shell)
  return {
    bounds: { w: level.bounds.w, d: level.bounds.d },
    walls: toWalls(level.walls ?? []),
    zones: toZones(level.zones ?? []),
    facilities: toFacilities(level.facilities ?? []),
    docks: toDocks(shell.docks ?? []),
    corridors: toCorridors(shell.corridors ?? [], level.zones ?? []),
    markings: shell.markings?.length ? toMarkings(shell.markings) : [],
    // RCS has no vehicle placements; the simulation backend still supplies them.
    vehicles: [],
  }
}

/**
 * Merge RCS-owned geometry with simulation-owned inventory.
 *
 * `FloorFull.zones` carries the stock detail (levels/cells/slots/bulks) that RCS
 * cannot express yet. ThreeEngine overlays zone coordinates from
 * `shell.zones` by matching `ref`, so zones whose ref is absent from the shell
 * simply keep their simulation coordinates — a safe, per-zone degradation.
 */
export function mergeShellIntoFloorFull(
  floorFull: FloorFull | null | undefined,
  shell: FloorShell | null | undefined,
): FloorFull | null {
  if (!shell) return floorFull ?? null
  const blueprint = toShellBlueprint(shell)
  if (!floorFull) return { shell: blueprint }
  return { ...floorFull, shell: blueprint }
}
