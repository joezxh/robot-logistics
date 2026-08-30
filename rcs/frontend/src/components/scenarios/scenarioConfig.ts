// Per-warehouse-category configuration: relevant zone types, theme color,
// alert types.
//
// Keyed by *category*, not by the six demo `ScenarioId`s. The map page now
// lists the eight database-backed warehouse templates, whose `category` values
// extend beyond SCENARIO_IDS, so lookups go through `configForCategory()` and
// degrade to a neutral default for anything unrecognised.
import type { ScenarioId, ZoneType } from '@/types'
import { ZONE_TYPES } from '@/types'

export interface CategoryConfig {
  id: string
  relevantZones: ZoneType[]
  themeColor: string
  alertTypes: string[]
  // highlight rule hint shown in the panel
  highlights: string[]
}

/** Kept for the demo scenario pages; the map page uses CATEGORY_CONFIG. */
export type { ScenarioId }

export const CATEGORY_CONFIG: Record<string, CategoryConfig> = {
  ecommerce: {
    id: 'ecommerce',
    relevantZones: ['flow_rack', 'high_rack', 'mezzanine', 'automated', 'temp', 'temp_bagged', 'returns'],
    themeColor: '#38bdf8',
    alertTypes: ['overstock', 'pick_timeout'],
    highlights: ['high_rack', 'automated', 'returns'],
  },
  manufacturing: {
    id: 'manufacturing',
    relevantZones: ['production_line', 'wip_buffer', 'parts_storage', 'staging'],
    themeColor: '#a78bfa',
    alertTypes: ['line_stop', 'wip_overflow'],
    highlights: ['production_line', 'wip_buffer'],
  },
  cold_chain: {
    id: 'cold_chain',
    relevantZones: ['cold_zone', 'frozen_zone', 'ambient_zone', 'loading_bay'],
    themeColor: '#3b82f6',
    alertTypes: ['temp_breach'],
    highlights: ['frozen_zone', 'cold_zone'],
  },
  port: {
    id: 'port',
    relevantZones: ['container_yard', 'customs_area'],
    themeColor: '#10b981',
    alertTypes: ['customs_hold', 'yard_full'],
    highlights: ['customs_area'],
  },
  reverse_logistics: {
    id: 'reverse_logistics',
    relevantZones: ['returns_received', 'qc_staging', 'reshelving', 'disposal'],
    themeColor: '#ef4444',
    alertTypes: ['qc_backlog', 'disposal_full'],
    highlights: ['qc_staging', 'reshelving'],
  },
  multi_floor: {
    id: 'multi_floor',
    relevantZones: ['floor_1', 'floor_2', 'floor_3', 'elevator_shaft'],
    themeColor: '#a855f7',
    alertTypes: ['elevator_jam'],
    highlights: ['elevator_shaft'],
  },
  // Categories that only exist as database warehouse templates.
  freight: {
    id: 'freight',
    relevantZones: ['staging', 'loading_bay'],
    themeColor: '#f59e0b',
    alertTypes: ['bay_queue', 'departure_delay'],
    highlights: ['staging'],
  },
  third_party: {
    id: 'third_party',
    relevantZones: ['high_rack', 'customs_area', 'staging', 'returns'],
    themeColor: '#14b8a6',
    alertTypes: ['client_quota', 'bonded_expiry'],
    highlights: ['customs_area'],
  },
}

/**
 * Neutral fallback for a category with no entry above (e.g. a template added
 * server-side before the frontend is updated). It shows every zone rather than
 * hiding the breakdown, so the panel degrades instead of going blank.
 */
export const DEFAULT_CATEGORY_CONFIG: CategoryConfig = {
  id: 'default',
  relevantZones: [...ZONE_TYPES],
  themeColor: '#94a3b8',
  alertTypes: [],
  highlights: [],
}

export function configForCategory(category: string | null | undefined): CategoryConfig {
  if (!category) return DEFAULT_CATEGORY_CONFIG
  return CATEGORY_CONFIG[category] ?? DEFAULT_CATEGORY_CONFIG
}

// Backwards-compatible alias for the demo scenario pages.
export const SCENARIO_CONFIG = CATEGORY_CONFIG as Record<ScenarioId, CategoryConfig>

// Filter a shell's zones down to those relevant for a category.
export function relevantZonesFor(category: string, zoneTypes: string[]): string[] {
  const cfg = configForCategory(category)
  return zoneTypes.filter((t) => cfg.relevantZones.includes(t as ZoneType))
}
