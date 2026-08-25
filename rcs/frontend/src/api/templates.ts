// REST client for /api/rcs/topology/templates*
import { http } from './http'
import type { FloorShell, SiteGrid, ScenarioId, ScenarioTemplateInfo } from '@/types'

export interface TemplateBundle {
  scenario_id: ScenarioId
  shell: FloorShell
  grid: SiteGrid
  metadata: Record<string, unknown>
}

export function listTemplates(): Promise<ScenarioTemplateInfo[]> {
  return http.get<ScenarioTemplateInfo[]>('/topology/templates')
}

export function getTemplate(scenarioId: ScenarioId): Promise<TemplateBundle> {
  return http.get<TemplateBundle>(`/topology/templates/${encodeURIComponent(scenarioId)}`)
}
