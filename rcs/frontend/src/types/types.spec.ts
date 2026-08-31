import { describe, it, expect } from 'vitest'
import {
  ZONE_TYPES,
  isZoneType,
  type FloorShell,
  type Zone,
} from '@/types/floorShell'
import {
  type SiteGrid,
  type Cell,
  cellCount,
  gridCapacity,
  isCellType,
} from '@/types/siteGrid'
import {
  SCENARIO_IDS,
  type ScenarioId,
} from '@/types/scenario'

describe('floorShell types', () => {
  it('ZONE_TYPES covers 25 zone types across 6 scenarios', () => {
    expect(ZONE_TYPES).toHaveLength(25)
    expect(ZONE_TYPES).toContain('flow_rack')
    expect(ZONE_TYPES).toContain('elevator_shaft')
  })

  it('isZoneType validates against the allow-list', () => {
    expect(isZoneType('flow_rack')).toBe(true)
    expect(isZoneType('not_a_zone')).toBe(false)
  })

  it('FloorShell accepts the backend ecommerce payload shape', () => {
    const shell: FloorShell = {
      bounds: { w: 160, d: 100 },
      zones: [
        { id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 } as Zone,
      ],
      metadata: { scenario: 'ecommerce', theme: 'warm' },
    }
    expect(shell.bounds.w).toBe(160)
    expect(shell.zones?.[0].type).toBe('flow_rack')
  })

  it('FloorShell supports multi_floor via floors[]', () => {
    const shell: FloorShell = {
      bounds: { w: 80, d: 60, h: 12 },
      zones: [{ id: 'el1', ref: 'EL-1', type: 'elevator_shaft', x: 70, z: 50, w: 5, d: 5 }],
      floors: [
        {
          id: 'L1',
          z: 0,
          bounds: { w: 80, d: 60 },
          zones: [{ id: 'f1-s', ref: 'STG-1', type: 'staging', x: 0, z: 0, w: 30, d: 20 }],
        },
      ],
    }
    expect(shell.floors).toHaveLength(1)
    expect(shell.floors?.[0].zones?.[0].type).toBe('staging')
  })
})

describe('siteGrid types', () => {
  const buildGrid = (w: number, d: number, resolution: number, cols: number, rows: number): SiteGrid => {
    const cells: Cell[][] = []
    for (let z = 0; z < rows; z++) {
      const row: Cell[] = []
      for (let x = 0; x < cols; x++) row.push({ x, z, type: 'EMPTY' })
      cells.push(row)
    }
    return { site_id: 's1', bounds: { w, d }, resolution, cells }
  }

  it('cells is a 2D array (rows × cols)', () => {
    const g = buildGrid(80, 60, 2, 40, 30)
    expect(g.cells).toHaveLength(30)
    expect(g.cells[0]).toHaveLength(40)
  })

  it('cellCount sums all rows', () => {
    const g = buildGrid(80, 60, 2, 40, 30)
    expect(cellCount(g)).toBe(1200)
  })

  it('gridCapacity = floor(w/res) * floor(d/res)', () => {
    const g = buildGrid(80, 60, 2, 40, 30)
    expect(gridCapacity(g)).toBe(40 * 30)
  })

  it('isCellType validates the AGV cell enum', () => {
    expect(isCellType('FREE')).toBe(true)
    expect(isCellType('RACK')).toBe(true)
    expect(isCellType('UNKNOWN')).toBe(false)
  })
})

describe('scenario types', () => {
  it('SCENARIO_IDS enumerates exactly 6 scenarios', () => {
    expect(SCENARIO_IDS).toHaveLength(6)
    expect(SCENARIO_IDS).toEqual([
      'ecommerce', 'manufacturing', 'cold_chain',
      'port', 'reverse_logistics', 'multi_floor',
    ])
  })

  it('ScenarioId is the union of SCENARIO_IDS', () => {
    const id: ScenarioId = 'port'
    expect(SCENARIO_IDS).toContain(id)
  })
})
