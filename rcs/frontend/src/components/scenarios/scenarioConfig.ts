// Per-scenario configuration: relevant zone types, theme color, alert types.
import type { ScenarioId, ZoneType } from '@/types'

export interface ScenarioConfig {
  id: ScenarioId
  relevantZones: ZoneType[]
  themeColor: string
  alertTypes: string[]
  // highlight rule hint shown in the panel
  highlights: string[]
}

export const SCENARIO_CONFIG: Record<ScenarioId, ScenarioConfig> = {
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
}

// Filter a shell's zones down to those relevant for a scenario.
export function relevantZonesFor(scenarioId: ScenarioId, zoneTypes: string[]): string[] {
  const cfg = SCENARIO_CONFIG[scenarioId]
  return zoneTypes.filter((t) => cfg.relevantZones.includes(t as ZoneType))
}
