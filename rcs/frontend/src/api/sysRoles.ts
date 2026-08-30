// Role management endpoints (/api/sys/roles).
import { qs, sysHttp } from './sysHttp'
import type { Envelope, RolePayload, RoleRow } from '@/types/sys'

export const listRoles = (keyword?: string) =>
  sysHttp.get<Envelope<RoleRow[]>>(`/roles${qs({ keyword })}`)

export const createRole = (body: RolePayload) => sysHttp.post<Envelope<RoleRow>>('/roles', body)

export const updateRole = (id: number, body: Partial<RolePayload>) =>
  sysHttp.put<Envelope<RoleRow>>(`/roles/${id}`, body)

export const deleteRole = (id: number) => sysHttp.delete<Envelope<null>>(`/roles/${id}`)

export const getRoleMenus = (id: number) => sysHttp.get<Envelope<number[]>>(`/roles/${id}/menus`)

export const assignRoleMenus = (id: number, menuIds: number[]) =>
  sysHttp.put<Envelope<null>>(`/roles/${id}/menus`, { menuIds })

export const getRoleUsers = (id: number) => sysHttp.get<Envelope<number[]>>(`/roles/${id}/users`)
