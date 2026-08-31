// REST client for the UNIFIED map model (`/maps/...`).
//
// Backend: rcs/api/control/control_unified_maps.py (mounted at /api/rcs by the
// app, so every path below is RELATIVE — `http.baseUrl` already defaults to
// '/api/rcs'. Writing '/api/rcs/maps/...' would produce
// '/api/rcs/api/rcs/maps/...'.
//
// This supersedes `./maps.ts` (old nodes/edges MapRow client) and
// `./warehouseTemplates.ts` (old richer template payload). Those files are still
// imported by stores that migrate in later tasks, so they stay until then.
//
// A unified map carries three orthogonal payloads instead of a single
// nodes/edges blob:
//   geometry  — FloorShell (walls / zones / docks / facilities)  → 3D + 2D view
//   topology  — { nodes, edges } navigation graph                → path planning
//   semantic  — free-form labels, zone semantics, i18n strings   → UI metadata
// plus a `dynamic` sub-resource for per-element runtime state
// (`/maps/{id}/dynamic/{element_id}`).
import { http } from './http'
import type { FloorShell } from '@/types'

/** Navigation graph carried by `topology`. Shapes are backend-defined. */
export interface UnifiedTopology {
  nodes: any[]
  edges: any[]
}

/** Planar bounds of a map/floor shell. */
export interface MapBounds {
  w: number
  d: number
}

/** GET/POST/PUT /maps — one row of the `robot_unified_maps` table. */
export interface UnifiedMapDTO {
  map_id: string
  name: string
  name_en?: string | null
  is_template: boolean
  kind?: string | null
  current_version: number
  bounds: MapBounds | null
  geometry: FloorShell
  topology: UnifiedTopology
  semantic: Record<string, any>
  dynamic?: Record<string, any>
  created_at?: string | null
  updated_at?: string | null
}

/**
 * GET /maps/templates — the SLIM template list served by the unified router.
 *
 * Deliberately NOT the richer `WarehouseTemplateInfo` from
 * `./warehouseTemplates.ts`: the unified endpoint returns only
 * `{map_id, name, name_en, kind}` (no category / bounds / node_count ...).
 */
export interface MapTemplateInfo {
  map_id: string
  name: string
  name_en?: string | null
  kind?: string | null
}

/**
 * Localised display name for a template: prefer the Chinese label, otherwise
 * the English name, finally the raw map_id.
 */
export function templateDisplayName(tpl: MapTemplateInfo, locale: string): string {
  if (locale.startsWith('zh') && tpl.name) return tpl.name
  if (tpl.name_en) return tpl.name_en
  return tpl.name || tpl.map_id
}

/** Row of the `robot_map_dynamic_state` table. */
export interface DynamicStateDTO {
  element_id: string
  state: string | null
  payload: Record<string, any> | null
  updated_at?: string | null
}

/** POST /maps — matches the backend `UnifiedMapCreate` model. */
export interface CreateMapBody {
  name: string
  geometry?: FloorShell | null
  topology?: Partial<UnifiedTopology> | null
  semantic?: Record<string, any> | null
  is_template?: boolean
  kind?: string | null
  name_en?: string | null
  bounds?: MapBounds | null
  data?: Record<string, any> | null
}

/** PUT /maps/{map_id} — matches the backend `UnifiedMapUpdate` model. */
export interface UpdateMapBody {
  name?: string | null
  geometry?: FloorShell | null
  topology?: UnifiedTopology | null
  semantic?: Record<string, any> | null
}

/** PUT /maps/{map_id}/dynamic/{element_id} — matches `DynamicStatePut`. */
export interface PutDynamicBody {
  state?: string
  payload?: Record<string, any>
}

/** GET /maps/{map_id}/export — the portable bundle. */
export interface MapExportBundle {
  map_id: string
  name: string
  geometry: FloorShell
  topology: UnifiedTopology
  semantic: Record<string, any>
}

// ── Map CRUD ─────────────────────────────────────────────────────────────────

/** List live maps. Templates are hidden unless `includeTemplates` is true. */
export function listMaps(includeTemplates = false): Promise<UnifiedMapDTO[]> {
  return http.get<UnifiedMapDTO[]>(`/maps?include_templates=${includeTemplates}`)
}

export function getMap(id: string): Promise<UnifiedMapDTO> {
  return http.get<UnifiedMapDTO>(`/maps/${encodeURIComponent(id)}`)
}

export function createMap(body: CreateMapBody): Promise<UnifiedMapDTO> {
  return http.post<UnifiedMapDTO>('/maps', body)
}

export function updateMap(id: string, body: UpdateMapBody): Promise<UnifiedMapDTO> {
  return http.put<UnifiedMapDTO>(`/maps/${encodeURIComponent(id)}`, body)
}

/** 204 No Content on success. */
export function deleteMap(id: string): Promise<void> {
  return http.delete<void>(`/maps/${encodeURIComponent(id)}`)
}

// ── Templates ────────────────────────────────────────────────────────────────

export function listTemplates(): Promise<MapTemplateInfo[]> {
  return http.get<MapTemplateInfo[]>('/maps/templates')
}

/** Idempotent — re-running refreshes template rows instead of duplicating. */
export function seedTemplates(): Promise<UnifiedMapDTO[]> {
  return http.post<UnifiedMapDTO[]>('/maps/templates/seed', {})
}

/** 201 + the new live map, or 404 when `templateKey` is unknown. */
export function createFromTemplate(templateKey: string, name?: string): Promise<UnifiedMapDTO> {
  return http.post<UnifiedMapDTO>('/maps/from-template', { template_key: templateKey, name })
}

// ── Import / export ──────────────────────────────────────────────────────────

/**
 * Merge an export bundle (or a flattened `{geometry, topology, semantic}`
 * subset) into an existing map. Missing keys are left untouched, so the payload
 * is typed as a plain dict — the backend decides what it recognises.
 */
export function importMap(id: string, payload: Record<string, any>): Promise<UnifiedMapDTO> {
  return http.post<UnifiedMapDTO>(`/maps/${encodeURIComponent(id)}/import`, payload)
}

export function exportMap(id: string): Promise<MapExportBundle> {
  return http.get<MapExportBundle>(`/maps/${encodeURIComponent(id)}/export`)
}

// ── Versioning ───────────────────────────────────────────────────────────────
// The versioning sub-tables are deferred backend-side: list_versions returns []
// and restore_version 404s. The surface stays stable so callers need no change
// once the tables land.

export function listVersions(id: string): Promise<any[]> {
  return http.get<any[]>(`/maps/${encodeURIComponent(id)}/versions`)
}

export function restoreVersion(id: string, versionId: string): Promise<UnifiedMapDTO> {
  return http.post<UnifiedMapDTO>(
    `/maps/${encodeURIComponent(id)}/versions/${encodeURIComponent(versionId)}/restore`,
    {},
  )
}

// ── Dynamic state ────────────────────────────────────────────────────────────

/** All dynamic-state rows for a map. 404 if the parent map does not exist. */
export function listDynamic(id: string): Promise<DynamicStateDTO[]> {
  return http.get<DynamicStateDTO[]>(`/maps/${encodeURIComponent(id)}/dynamic`)
}

/** Upsert the state of one element. 404 if the parent map does not exist. */
export function putDynamic(
  id: string,
  elementId: string,
  body: PutDynamicBody,
): Promise<DynamicStateDTO> {
  return http.put<DynamicStateDTO>(
    `/maps/${encodeURIComponent(id)}/dynamic/${encodeURIComponent(elementId)}`,
    body,
  )
}

/** 204 No Content on success, 404 when the row is missing. */
export function deleteDynamic(id: string, elementId: string): Promise<void> {
  return http.delete<void>(
    `/maps/${encodeURIComponent(id)}/dynamic/${encodeURIComponent(elementId)}`,
  )
}
