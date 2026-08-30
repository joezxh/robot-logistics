// User management endpoints (/api/sys/users).
import { qs, sysHttp } from './sysHttp'
import type { Envelope, UserPayload, UserRow, UserUpdatePayload } from '@/types/sys'

export interface UserListQuery {
  keyword?: string
  status?: string
  skip?: number
  limit?: number
}

export const listUsers = (q: UserListQuery = {}) =>
  sysHttp.get<Envelope<UserRow[]>>(`/users${qs(q)}`)

export const getUser = (id: number) => sysHttp.get<Envelope<UserRow>>(`/users/${id}`)

export const createUser = (body: UserPayload) => sysHttp.post<Envelope<UserRow>>('/users', body)

export const updateUser = (id: number, body: UserUpdatePayload) =>
  sysHttp.put<Envelope<UserRow>>(`/users/${id}`, body)

export const deleteUser = (id: number) => sysHttp.delete<Envelope<null>>(`/users/${id}`)

export const setUserStatus = (id: number, status: string) =>
  sysHttp.put<Envelope<null>>(`/users/${id}/status`, { status })

export const resetUserPassword = (id: number, newPassword: string) =>
  sysHttp.post<Envelope<null>>(`/users/${id}/reset-password`, { newPassword })

export const getUserRoles = (id: number) => sysHttp.get<Envelope<number[]>>(`/users/${id}/roles`)

export const assignUserRoles = (id: number, roleIds: number[]) =>
  sysHttp.put<Envelope<null>>(`/users/${id}/roles`, { roleIds })
