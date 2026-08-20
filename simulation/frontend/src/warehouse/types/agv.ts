export type CellType = 0 | 1 | 2 | 3

export interface AGVCell {
  t: CellType
  w: number
}

export interface AGVNode {
  x: number
  z: number
  g: number
  h: number
  f: number
  parent?: AGVNode
}

export interface AGVGrid {
  cols: number
  rows: number
  cell_size: number
  cells: AGVCell[]
}

export interface AisleGap {
  index: number
  label: string
  z_center: number
  width: number
}

export interface AGVPath {
  task_id: string
  points: [number, number, number][]
  vehicle_ref: string
  status: 'planned' | 'active' | 'completed'
}

export interface AGVTool {
  type: 'block' | 'walk' | 'main' | 'restricted'
  label: string
  color: string
}

export const AGV_TOOLS: AGVTool[] = [
  { type: 'block', label: 'Block', color: '#374151' },
  { type: 'walk', label: 'Walk', color: '#6b7280' },
  { type: 'main', label: 'Main Path', color: '#3b82f6' },
  { type: 'restricted', label: 'Restricted', color: '#f97316' },
]

export const AGV_WEIGHTS: Record<CellType, number> = {
  0: 999,
  1: 1,
  2: 1,
  3: 5,
}
