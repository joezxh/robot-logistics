import { http } from './http'
import type { SchedulerConfig } from '@/types'

export const listConfigs = () => http.get<SchedulerConfig[]>('/scheduler-configs')
export const getActive = () => http.get<SchedulerConfig>('/scheduler-configs/active')
export const createConfig = (body: { name: string; strategy?: string; weights: any }) =>
  http.post<SchedulerConfig>('/scheduler-configs', body)
export const updateConfig = (id: string, body: Partial<SchedulerConfig>) =>
  http.put<SchedulerConfig>(`/scheduler-configs/${encodeURIComponent(id)}`, body)
export const activateConfig = (id: string) =>
  http.post<{ activated: string }>(`/scheduler-configs/${encodeURIComponent(id)}/activate`, {})