// System-administration types — mirrors the Pydantic models in
// rcs/backend/rcs/sysadmin/schemas.py.

// NOTE: `SUPPORTED_LOCALES` lives in `@/i18n` (single source of truth) so that
// re-exporting `./sys` from `@/types` cannot clash with it.

/** Console skins. */
export type AppTheme = 'dark' | 'light'

/** Supported console languages (the DB menu `i18n` map uses the same keys). */
export type AppLocale = 'zh-CN' | 'zh-TW' | 'en-US' | 'ja-JP'

/** JSONB map stored in `sys_menu.i18n`. */
export type I18nMap = Partial<Record<AppLocale, string>>

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginResult {
  token: string
  tokenType: string
  expiresIn: number
  userId: number
  username: string
  realName: string
}

export interface UserInfo {
  userId: number
  username: string
  realName: string
  phone?: string | null
  email?: string | null
  avatar?: string | null
  status: string
  isAdmin: boolean
  roles: string[]
  permissions: string[]
  lastLoginAt?: string | null
  createdAt?: string | null
}

export interface UpdateProfilePayload {
  realName?: string
  phone?: string
  email?: string
  avatar?: string
}

export interface ChangePasswordPayload {
  oldPassword: string
  newPassword: string
}

// ---------------------------------------------------------------------------
// Menus
// ---------------------------------------------------------------------------

/** 1 = directory, 2 = page, 3 = button permission. */
export type MenuType = 1 | 2 | 3

export interface MenuNode {
  id: number
  name: string
  i18n: I18nMap
  permission?: string | null
  path?: string | null
  type: MenuType
  parentId?: number | null
  icon?: string | null
  component?: string | null
  componentName?: string | null
  sort: number
  status: number
  visible: number
  keepAlive: number
  alwaysShow: number
  children: MenuNode[]
}

export interface MenuPayload {
  name: string
  i18n?: I18nMap
  permission?: string | null
  path?: string | null
  type?: MenuType
  parentId?: number | null
  icon?: string | null
  component?: string | null
  componentName?: string | null
  sort?: number
  status?: number
  visible?: number
  keepAlive?: number
  alwaysShow?: number
}

export interface MenuSimple {
  id: number
  parentId?: number | null
  name: string
  i18n: I18nMap
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------

export interface UserRow {
  userId: number
  username: string
  realName: string
  phone?: string | null
  email?: string | null
  avatar?: string | null
  status: string
  isAdmin: boolean
  roleIds: number[]
  roleNames: string[]
  lastLoginAt?: string | null
  lastLoginIp?: string | null
  createdAt?: string | null
  updatedAt?: string | null
}

export interface UserPayload {
  username: string
  password: string
  realName: string
  phone?: string
  email?: string
  status?: string
  isAdmin?: boolean
  roleIds?: number[]
}

export interface UserUpdatePayload {
  realName?: string
  phone?: string
  email?: string
  avatar?: string
  status?: string
  isAdmin?: boolean
}

// ---------------------------------------------------------------------------
// Roles
// ---------------------------------------------------------------------------

export interface RoleRow {
  roleId: number
  roleName: string
  roleCode: string
  description?: string | null
  regionCode?: string | null
  regionLevel?: string | null
  sortOrder: number
  status: string
  menuIds: number[]
  createdAt?: string | null
}

export interface RolePayload {
  roleName: string
  roleCode: string
  description?: string
  regionCode?: string
  regionLevel?: string
  sortOrder?: number
  status?: string
}

// ---------------------------------------------------------------------------
// Dictionaries
// ---------------------------------------------------------------------------

export interface DictRow {
  dictId: number
  dictCode: string
  dictName: string
  dictType: string
  description?: string | null
  sortOrder: number
  isActive: boolean
  extraData?: Record<string, unknown> | null
  createdAt?: string | null
  updatedAt?: string | null
}

export interface DictItemRow {
  itemId: number
  dictCode: string
  itemCode: string
  itemName: string
  itemValue?: string | null
  parentCode?: string | null
  level: number
  color?: string | null
  icon?: string | null
  sortOrder: number
  isActive: boolean
  extraData?: Record<string, unknown> | null
  remark?: string | null
  createdAt?: string | null
  updatedAt?: string | null
}

export interface DictWithItems extends DictRow {
  items: DictItemRow[]
}

export interface DictPayload {
  dictCode: string
  dictName: string
  dictType: string
  description?: string
  sortOrder?: number
  isActive?: boolean
  extraData?: Record<string, unknown> | null
}

export interface DictItemPayload {
  dictCode: string
  itemCode: string
  itemName: string
  itemValue?: string
  parentCode?: string
  level?: number
  color?: string
  icon?: string
  sortOrder?: number
  isActive?: boolean
  extraData?: Record<string, unknown> | null
  remark?: string
}

// ---------------------------------------------------------------------------
// Audit logs
// ---------------------------------------------------------------------------

export interface AuditLogRow {
  logId: number
  userId?: number | null
  username?: string | null
  operationType: string
  operationModule?: string | null
  operationDesc?: string | null
  requestMethod?: string | null
  requestUrl?: string | null
  requestParams?: Record<string, unknown> | null
  requestIp?: string | null
  userAgent?: string | null
  responseStatus?: number | null
  responseTimeMs?: number | null
  oldData?: Record<string, unknown> | null
  newData?: Record<string, unknown> | null
  createdAt?: string | null
}

export interface AuditStats {
  total: number
  byType: Record<string, number>
}

// ---------------------------------------------------------------------------
// Shared response envelope
// ---------------------------------------------------------------------------

export interface Envelope<T> {
  code: number
  message: string
  data: T | null
  total?: number | null
}

/** Page query accepted by every list endpoint. */
export interface PageQuery {
  skip?: number
  limit?: number
}

export interface DashboardSummary {
  userCount: number
  roleCount: number
  menuCount: number
  dictCount: number
  activeUserCount: number
  recentOperations: Array<{
    logId: number
    operationType: string
    operationModule?: string | null
    operationDesc?: string | null
    responseStatus?: number | null
    createdAt?: string | null
  }>
}
