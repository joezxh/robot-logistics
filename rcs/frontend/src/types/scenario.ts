// Scenario template types — mirror rcs_backend.topology.templates.

export const SCENARIO_IDS = [
  'ecommerce',
  'manufacturing',
  'cold_chain',
  'port',
  'reverse_logistics',
  'multi_floor',
] as const

export type ScenarioId = (typeof SCENARIO_IDS)[number]

export interface ScenarioTemplateInfo {
  scenario_id: ScenarioId
  name: string
  bounds: { w: number; d: number }
  zone_count: number
}

export interface ScenarioBundle {
  scenario_id: ScenarioId
  shell: import('./floorShell').FloorShell
  grid: import('./siteGrid').SiteGrid
  metadata: Record<string, unknown>
}

export function isScenarioId(value: string): value is ScenarioId {
  return (SCENARIO_IDS as readonly string[]).includes(value)
}
