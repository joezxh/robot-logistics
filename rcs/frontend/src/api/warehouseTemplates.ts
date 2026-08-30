// REST client for the database-backed warehouse templates.
//
// These are NOT the same as /topology/templates (six hard-coded demo
// scenarios). A warehouse template is a real record spread across
// robot_topology_shell / robot_topology_grid / robot_site_maps, flagged with
// `is_template` and seeded by POST /maps/templates/seed.
//
// Consequence: adding or editing a template server-side needs no frontend
// change — the picker is driven entirely by this list.
import { http } from './http'

export interface WarehouseTemplateInfo {
  key: string
  /** id of the row in robot_site_maps (the navigation graph). */
  map_id: string
  /** id of the row in robot_topology_shell (the FloorShell geometry). */
  site_id: string
  name: string
  name_en: string
  /** Drives which panel theme / alert chips the map page shows. */
  category: string
  description: string
  bounds: { w: number; d: number }
  node_count: number
  edge_count: number
  node_types: Record<string, number>
  zone_count: number
  facility_count: number
  dock_count: number
  wall_count: number
  grid_row_count: number
}

export function listWarehouseTemplates(): Promise<WarehouseTemplateInfo[]> {
  return http.get<WarehouseTemplateInfo[]>('/maps/templates')
}

/** Idempotent — safe to call on page load to guarantee templates exist. */
export function seedWarehouseTemplates(): Promise<unknown[]> {
  return http.post<unknown[]>('/maps/templates/seed', {})
}

/**
 * Localised display name.
 *
 * The backend ships a Chinese (`name`) and an English (`name_en`) label per
 * template and that is the only translation it can offer, so zh locales use
 * `name` and everything else `name_en`. Keeping names as data (rather than
 * i18n keys) is deliberate: a new template then needs no frontend change.
 */
export function templateDisplayName(
  tpl: Pick<WarehouseTemplateInfo, 'name' | 'name_en'>,
  locale: string,
): string {
  return locale.startsWith('zh') ? tpl.name || tpl.name_en : tpl.name_en || tpl.name
}
