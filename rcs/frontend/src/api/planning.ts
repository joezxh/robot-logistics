import { http } from './http'
import type { PlanningProfile } from '@/types'

export const listProfiles = () => http.get<PlanningProfile[]>('/planning-profiles')
export const getProfile = (id: string) =>
  http.get<PlanningProfile>(`/planning-profiles/${encodeURIComponent(id)}`)
export const createProfile = (body: {
  name: string
  algo: string
  axes: number
  vel_max: number[]
  acc_max: number[]
  created_by?: string
}) => http.post<PlanningProfile>('/planning-profiles', body)
export const deleteProfile = (id: string) =>
  http.delete<void>(`/planning-profiles/${encodeURIComponent(id)}`)