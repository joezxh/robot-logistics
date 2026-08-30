export interface UOMCapacity {
  uom: string
  qty: number
  reserved: number
  cap: number
}

export interface ItemStock {
  c: string
  n: string
  u: string
  g: string
  qty: number
  reserved: number
  rate: number
  stock_value: number
}

export interface SlotLevel {
  wh: string
  label: string
  uoms: UOMCapacity[]
  items: ItemStock[]
}

export interface Slot {
  wh: string
  label: string
  row: number
  col: number
  row_gap: number
  levels: SlotLevel[]
}

export interface WarehouseGroup {
  id: string
  name: string
  parent_id: string
  parent_name: string
  slot_count: number
}

export interface WarehouseDetail {
  name: string
  warehouse_name: string
  company: string
  wt_warehouse_type: 'Building' | 'Floor' | 'Slot' | 'Bin' | 'Dock' | 'Zone' | 'Aisle' | 'Cell' | 'Bulk' | 'Facility'
  parent_warehouse: string
  is_group: boolean
  disabled: boolean
  wt_row: number
  wt_col: number
  wt_row_gap: number
  uom_capacities: UOMCapacity[]
}

export type ViewMode = '3d' | '2d' | 'editor'
export type Language = 'zh' | 'en'
export type Theme = 'dark' | 'light'
