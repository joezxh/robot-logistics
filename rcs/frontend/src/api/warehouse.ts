// REST client for warehouse_theatre_3d integration
import { http } from './http'
import type { FloorShell } from '@/types'

export interface WarehouseImportResult {
  ok: boolean
  site_id: string
  map_id: string
  map_version: number
  zone_count: number
  node_count: number
  edge_count: number
  shell: {
    bounds: { w: number; d: number }
    wall_count: number
    zone_count: number
    facility_count: number
    dock_count: number
  }
}

export interface WarehousePreview {
  shell: FloorShell
  nodes: Array<{
    id: string
    pos: number[]
    type: string
    zone_type?: string
    capacity?: number
    flow?: string
    facility_kind?: string
  }>
  edges: Array<{
    from: string
    to: string
    distance: number
    bidirectional: boolean
    speed_limit: number
  }>
  summary: {
    zone_count: number
    facility_count: number
    dock_count: number
    wall_count: number
    node_count: number
    edge_count: number
  }
}

/** Import warehouse_theatre_3d blueprint into RCS backend */
export function importWarehouseTheatre(): Promise<WarehouseImportResult> {
  return http.post<WarehouseImportResult>('/import/warehouse-theatre', {})
}

/** Preview converted data without saving */
export function previewWarehouseTheatre(): Promise<WarehousePreview> {
  return http.get<WarehousePreview>('/import/warehouse-theatre/preview')
}
