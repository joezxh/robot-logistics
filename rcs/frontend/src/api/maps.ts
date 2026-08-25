import { http } from './http'
import type { MapRow, MapVersionRow } from '@/types'

export const listMaps = () => http.get<MapRow[]>('/maps')
export const getMap = (id: string) => http.get<MapRow>(`/maps/${encodeURIComponent(id)}`)
export const createMap = (body: { name: string; nodes?: any[]; edges?: any[] }) =>
  http.post<MapRow>('/maps', body)
export const updateMap = (id: string, body: { name?: string; nodes: any[]; edges: any[] }) =>
  http.put<MapRow>(`/maps/${encodeURIComponent(id)}`, body)
export const deleteMap = (id: string) => http.delete<void>(`/maps/${encodeURIComponent(id)}`)
export const importMap = (id: string, payload: { nodes: any[]; edges: any[] }) =>
  http.post<MapRow>(`/maps/${encodeURIComponent(id)}/import`, payload)
export const exportMap = (id: string) => http.get<MapRow>(`/maps/${encodeURIComponent(id)}/export`)
export const listVersions = (id: string) =>
  http.get<MapVersionRow[]>(`/maps/${encodeURIComponent(id)}/versions`)
export const restoreVersion = (mapId: string, versionId: string) =>
  http.post<MapRow>(`/maps/${encodeURIComponent(mapId)}/versions/${encodeURIComponent(versionId)}/restore`, {})