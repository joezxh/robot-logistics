// Site grid (AGV navigation cells) types — mirror rcs_backend.models.site_grid.

export type CellType =
  | 'EMPTY'
  | 'FREE'
  | 'BLOCKED'
  | 'CHARGING'
  | 'STAGING'
  | 'PICK'
  | 'DROP'
  | 'ELEVATOR'
  | 'RACK'

export interface Cell {
  x: number
  z: number
  type: CellType
  cost?: number
}

export interface BoundsLite {
  w: number
  d: number
}

export interface SiteGrid {
  site_id: string
  bounds: BoundsLite
  resolution: number
  cells: Cell[][]
  metadata?: Record<string, unknown>
}

export function cellCount(grid: SiteGrid): number {
  return grid.cells.reduce((sum, row) => sum + row.length, 0)
}

export function gridCapacity(grid: SiteGrid): number {
  const cols = Math.max(1, Math.floor(grid.bounds.w / grid.resolution))
  const rows = Math.max(1, Math.floor(grid.bounds.d / grid.resolution))
  return cols * rows
}

export function isCellType(value: string): value is CellType {
  return [
    'EMPTY', 'FREE', 'BLOCKED', 'CHARGING', 'STAGING',
    'PICK', 'DROP', 'ELEVATOR', 'RACK',
  ].includes(value)
}
