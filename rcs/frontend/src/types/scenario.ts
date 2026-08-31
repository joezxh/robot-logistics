// Scenario id namespace. These ids were historically hard-coded demo scenarios;
// they now serve as i18n keys for localized scenario labels (scenarioName).
// Floor-shell / grid payloads are no longer bundled here — they are served from
// the unified `robot_unified_maps` table via the `/api/rcs/maps` endpoints.

export const SCENARIO_IDS = [
  'ecommerce',
  'manufacturing',
  'cold_chain',
  'port',
  'reverse_logistics',
  'multi_floor',
] as const

export type ScenarioId = (typeof SCENARIO_IDS)[number]
