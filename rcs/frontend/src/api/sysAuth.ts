// Authentication, session and profile endpoints (/api/sys/auth).
import { sysHttp } from './sysHttp'
import type {
  ChangePasswordPayload,
  LoginPayload,
  LoginResult,
  MenuNode,
  UpdateProfilePayload,
  UserInfo,
} from '@/types/sys'

export const login = (body: LoginPayload) => sysHttp.post<LoginResult>('/auth/login', body)

export const logout = () => sysHttp.post<{ code: number; message: string }>('/auth/logout')

/** Profile + roles + flattened permissions. */
export const fetchProfile = () => sysHttp.get<UserInfo>('/auth/me')

export const updateProfile = (body: UpdateProfilePayload) => sysHttp.put<UserInfo>('/auth/me/profile', body)

export const changePassword = (body: ChangePasswordPayload) =>
  sysHttp.put<{ code: number; message: string }>('/auth/me/password', body)

/** Permission-filtered menu tree for the console sidebar. */
export const fetchMyMenus = () =>
  sysHttp.get<{ code: number; message: string; data: MenuNode[] }>('/auth/me/menus')

export const fetchDashboardSummary = () =>
  sysHttp.get<{
    code: number
    message: string
    data: {
      userCount: number
      roleCount: number
      menuCount: number
      dictCount: number
      activeUserCount: number
      recentOperations: Array<Record<string, unknown>>
    }
  }>('/dashboard/summary')
