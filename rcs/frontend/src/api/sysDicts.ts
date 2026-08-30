// Dictionary endpoints (/api/sys/dictionaries).
import { qs, sysHttp } from './sysHttp'
import type {
  DictItemPayload,
  DictItemRow,
  DictPayload,
  DictRow,
  DictWithItems,
  Envelope,
} from '@/types/sys'

export const listDictionaries = (params: { keyword?: string; type?: string } = {}) =>
  sysHttp.get<Envelope<DictRow[]>>(`/dictionaries${qs(params)}`)

/** Fetch several dictionaries in one round trip (console bootstrap). */
export const batchDictionaries = (codes: string[]) =>
  sysHttp.get<Envelope<Record<string, DictItemRow[]>>>(`/dictionaries/batch${qs({ codes: codes.join(',') })}`)

export const getDictionary = (code: string) =>
  sysHttp.get<Envelope<DictWithItems>>(`/dictionaries/${encodeURIComponent(code)}`)

export const createDictionary = (body: DictPayload) =>
  sysHttp.post<Envelope<DictRow>>('/dictionaries', body)

export const updateDictionary = (code: string, body: Partial<DictPayload>) =>
  sysHttp.put<Envelope<DictRow>>(`/dictionaries/${encodeURIComponent(code)}`, body)

export const deleteDictionary = (code: string) =>
  sysHttp.delete<Envelope<null>>(`/dictionaries/${encodeURIComponent(code)}`)

export const listDictItems = (code: string) =>
  sysHttp.get<Envelope<DictItemRow[]>>(`/dictionaries/${encodeURIComponent(code)}/items`)

export const createDictItem = (code: string, body: DictItemPayload) =>
  sysHttp.post<Envelope<DictItemRow>>(`/dictionaries/${encodeURIComponent(code)}/items`, body)

export const updateDictItem = (itemId: number, body: Partial<DictItemPayload>) =>
  sysHttp.put<Envelope<DictItemRow>>(`/dictionaries/items/${itemId}`, body)

export const deleteDictItem = (itemId: number) =>
  sysHttp.delete<Envelope<null>>(`/dictionaries/items/${itemId}`)
