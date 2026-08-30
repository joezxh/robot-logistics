// Menu / permission endpoints (/api/sys/menus).
//
// Menus carry a JSONB `i18n` map so the console can switch language without
// re-fetching the tree.
import { qs, sysHttp } from './sysHttp'
import type { Envelope, MenuNode, MenuPayload, MenuSimple } from '@/types/sys'

export interface MenuListQuery {
  name?: string
  status?: number
  type?: number
}

/** Nested tree used by both the sidebar and the management table. */
export const listMenuTree = (q: MenuListQuery = {}) =>
  sysHttp.get<Envelope<MenuNode[]>>(`/menus${qs(q)}`)

export const listMenuFlat = (q: MenuListQuery = {}) =>
  sysHttp.get<Envelope<MenuNode[]>>(`/menus/flat${qs(q)}`)

/** `id / parentId / name` projection for the parent-menu picker. */
export const listMenuSimple = () => sysHttp.get<Envelope<MenuSimple[]>>('/menus/simple')

export const getMenu = (id: number) => sysHttp.get<Envelope<MenuNode>>(`/menus/${id}`)

export const createMenu = (body: MenuPayload) => sysHttp.post<Envelope<MenuNode>>('/menus', body)

export const updateMenu = (id: number, body: Partial<MenuPayload>) =>
  sysHttp.put<Envelope<MenuNode>>(`/menus/${id}`, body)

export const deleteMenu = (id: number) => sysHttp.delete<Envelope<null>>(`/menus/${id}`)
