import { describe, it, expect } from 'vitest'
import type { FloorShell } from '@/types'
import { toShellBlueprint, mergeShellIntoFloorFull, mapZoneType, mapFacilityKind } from './floorShell'
import type { FloorFull } from '../types'

function shell(overrides: Partial<FloorShell> = {}): FloorShell {
  return {
    bounds: { w: 100, d: 60, h: 12 },
    walls: [{ id: 'w1', x0: 0, z0: 0, x1: 100, z1: 0, h: 8, kind: 'wall' }],
    zones: [
      { id: 'z1', ref: 'A-01', type: 'high_rack', x: 0, z: 0, w: 20, d: 10, current_load_pct: 42 },
      { id: 'z2', ref: 'A-02', type: 'cold_zone', x: 30, z: 0, w: 20, d: 10 },
    ],
    facilities: [{ id: 'f1', ref: 'CHG-1', type: 'charger', x: 5, z: 50, w: 3, d: 3 }],
    docks: [{ id: 'd1', ref: 'DOCK-1', x: 0, z: 58, direction: 'S', door_w: 5 }],
    corridors: [{ id: 'c1', from_zone: 'A-01', to_zone: 'A-02', w: 3, bidirectional: true }],
    markings: [{ id: 'm1', kind: 'lane', points: [[0, 0], [10, 0]], color: '#ff0000' }],
    ...overrides,
  }
}

describe('toShellBlueprint', () => {
  it('maps bounds and drops the height the renderer does not model', () => {
    const bp = toShellBlueprint(shell())
    expect(bp.bounds).toEqual({ w: 100, d: 60 })
  })

  it('maps wall geometry and defaults a missing height', () => {
    const bp = toShellBlueprint(shell({ walls: [{ id: 'w', x0: 0, z0: 0, x1: 10, z1: 0 }] }))
    expect(bp.walls).toHaveLength(1)
    expect(bp.walls[0]).toMatchObject({ x0: 0, z0: 0, x1: 10, z1: 0, h: 6 })
  })

  it('collapses RCS-only zone types onto renderable archetypes', () => {
    expect(mapZoneType('cold_zone')).toBe('temp')
    expect(mapZoneType('high_rack')).toBe('high_rack')
    expect(mapZoneType('totally_unknown')).toBe('rack')
  })

  it('seeds occupancy from RCS current_load_pct', () => {
    const bp = toShellBlueprint(shell())
    expect(bp.zones?.[0].occ).toEqual({ total: 100, occupied: 42 })
    expect(bp.zones?.[1].occ).toBeUndefined()
  })

  it('maps facility kind, falling back to sorting for unknown types', () => {
    expect(mapFacilityKind('charger')).toBe('charger')
    expect(mapFacilityKind('container_yard')).toBe('sorting')
  })

  it('defaults dock flow to outbound but preserves the RCS compass facing', () => {
    const dock = toShellBlueprint(shell()).docks[0]
    expect(dock.direction).toBe('outbound')
    expect(dock.facing).toBe('S') // flow vs. orientation are different concepts
    expect(dock.w).toBe(5) // from door_w
  })

  it('derives corridor geometry from zone centres', () => {
    const bp = toShellBlueprint(shell())
    // A-01 centre (10,5) -> A-02 centre (40,5)
    expect(bp.corridors[0]).toMatchObject({ x0: 10, z0: 5, x1: 40, z1: 5, main: true })
  })

  it('skips corridors referencing unknown zones', () => {
    const bp = toShellBlueprint(shell({ corridors: [{ id: 'c', from_zone: 'nope', to_zone: 'A-02' }] }))
    expect(bp.corridors).toHaveLength(0)
  })

  it('converts marking colour from hex string to the renderer numeric form', () => {
    const bp = toShellBlueprint(shell())
    expect(bp.markings?.[0].color).toBe(0xff0000)
    expect(bp.markings?.[0].pts).toEqual([[0, 0], [10, 0]])
  })

  it('falls back to floors[0] when the shell has no top-level geometry', () => {
    const bp = toShellBlueprint(
      shell({
        zones: undefined,
        walls: undefined,
        floors: [
          {
            id: 'L1',
            z: 0,
            bounds: { w: 50, d: 30 },
            zones: [{ id: 'fz', ref: 'B-01', type: 'rack', x: 1, z: 2, w: 4, d: 5 }],
          },
        ],
      }),
    )
    expect(bp.bounds).toEqual({ w: 50, d: 30 })
    expect(bp.zones).toHaveLength(1)
    expect(bp.zones?.[0].ref).toBe('B-01')
  })
})

describe('mergeShellIntoFloorFull', () => {
  it('replaces geometry but keeps simulation inventory', () => {
    const floorFull: FloorFull = {
      shell: {
        bounds: { w: 1, d: 1 },
        walls: [],
        docks: [],
        facilities: [],
        corridors: [],
      },
      zones: [
        {
          ref: 'A-01',
          type: 'rack',
          x: 0,
          z: 0,
          w: 1,
          d: 1,
          levels: 3,
          cells: [{ aisle: 1, row: 1, col: 1, level: 1, qty: 7 }],
          slots: [{ name: 's1', items: [] }],
          bulks: [{ name: 'b1', qty: 2 }],
        },
      ],
    }

    const merged = mergeShellIntoFloorFull(floorFull, shell())
    expect(merged).not.toBeNull()
    // Geometry now comes from RCS.
    expect(merged!.shell!.bounds).toEqual({ w: 100, d: 60 })
    expect(merged!.shell!.zones).toHaveLength(2)
    // Inventory is untouched.
    const zone = merged!.zones![0]
    expect(zone.levels).toBe(3)
    expect(zone.cells).toHaveLength(1)
    expect(zone.bulks).toHaveLength(1)
  })

  it('returns the simulation payload untouched when RCS has no shell', () => {
    const floorFull: FloorFull = { zones: [{ ref: 'A-01', type: 'rack', x: 0, z: 0, w: 1, d: 1 }] }
    expect(mergeShellIntoFloorFull(floorFull, null)).toBe(floorFull)
  })

  it('produces a blueprint-only payload when there is no simulation data', () => {
    const merged = mergeShellIntoFloorFull(null, shell())
    expect(merged!.shell!.bounds).toEqual({ w: 100, d: 60 })
    expect(merged!.zones).toBeUndefined()
  })
})
