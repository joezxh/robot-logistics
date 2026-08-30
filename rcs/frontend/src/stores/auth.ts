// Authentication / authorisation store.
//
// Owns the JWT, the resolved profile (roles + flattened permissions) and the
// permission-filtered menu tree returned by `/api/sys/auth/me/menus`. The
// router reads `menus` to register dynamic routes and the sidebar renders it
// directly, so there is a single source of truth for "what can this user see".
import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { SysHttpClient, extractDetail } from '@/api/sysHttp'
import * as authApi from '@/api/sysAuth'
import type { MenuNode, UserInfo } from '@/types'

/** Wildcard granted to super-admins by the backend. */
const WILDCARD = '*:*'

/** Codes that make a menu entry appear in the top-bar portal dropdown. */
export const PORTAL_PERMISSIONS = [
  'twin:sitemap:view',
  'twin:warehouse:view',
  'sys:device:control',
] as const

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(SysHttpClient.token)
  const profile = ref<UserInfo | null>(null)
  const menus = ref<MenuNode[]>([])
  const loading = ref(false)
  const menusLoaded = ref(false)
  const error = ref<string>('')

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => Boolean(profile.value?.isAdmin))
  const roles = computed(() => profile.value?.roles ?? [])
  const permissions = computed(() => profile.value?.permissions ?? [])

  /** Route paths this user is allowed to open (derived from the menu tree). */
  const allowedPaths = computed(() => {
    const paths = new Set<string>()
    const walk = (nodes: MenuNode[]) => {
      for (const node of nodes) {
        if (node.path) paths.add(normalisePath(node.path))
        if (node.children?.length) walk(node.children)
      }
    }
    walk(menus.value)
    return paths
  })

  function hasPermission(code: string | string[] | undefined | null): boolean {
    if (!code) return true
    const required = Array.isArray(code) ? code : [code]
    if (required.length === 0) return true
    if (permissions.value.includes(WILDCARD)) return true
    return required.every((c) => permissions.value.includes(c))
  }

  /** Menus flagged for the portal dropdown, resolved from the user's grants. */
  const portalMenus = computed<MenuNode[]>(() => {
    const found: MenuNode[] = []
    const walk = (nodes: MenuNode[]) => {
      for (const node of nodes) {
        if (node.permission && (PORTAL_PERMISSIONS as readonly string[]).includes(node.permission)) {
          found.push(node)
        }
        if (node.children?.length) walk(node.children)
      }
    }
    walk(menus.value)
    return found
  })

  function setToken(next: string) {
    token.value = next
    SysHttpClient.setToken(next)
  }

  async function login(username: string, password: string): Promise<void> {
    loading.value = true
    error.value = ''
    try {
      const result = await authApi.login({ username, password })
      setToken(result.token)
      await loadProfile()
      await loadMenus()
    } catch (err) {
      setToken('')
      error.value = err instanceof Error ? extractDetail((err as { detail?: unknown }).detail) || err.message : String(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadProfile(): Promise<UserInfo | null> {
    if (!token.value) return null
    profile.value = await authApi.fetchProfile()
    return profile.value
  }

  async function loadMenus(force = false): Promise<MenuNode[]> {
    if (!token.value) return []
    if (menusLoaded.value && !force) return menus.value
    const res = await authApi.fetchMyMenus()
    menus.value = res?.data ?? []
    menusLoaded.value = true
    return menus.value
  }

  async function logout(): Promise<void> {
    try {
      if (token.value) await authApi.logout()
    } catch {
      // The token may already be expired — clearing local state is what matters.
    } finally {
      reset()
    }
  }

  function reset() {
    token.value = ''
    profile.value = null
    menus.value = []
    menusLoaded.value = false
    error.value = ''
    SysHttpClient.clearToken()
  }

  return {
    token,
    profile,
    menus,
    loading,
    menusLoaded,
    error,
    isAuthenticated,
    isAdmin,
    roles,
    permissions,
    allowedPaths,
    portalMenus,
    hasPermission,
    setToken,
    login,
    loadProfile,
    loadMenus,
    logout,
    reset,
  }
})

/** Normalise `/admin/maps/` -> `/admin/maps` for path comparisons. */
export function normalisePath(path: string): string {
  return path.replace(/\/+$/, '') || '/'
}
