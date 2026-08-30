// Router bootstrap.
//
// Static routes: /login, the console shell, and a catch-all.
// Dynamic routes: registered at runtime from the permission-filtered menu tree
// returned by /api/sys/auth/me/menus (see `./dynamic`).
//
// The guard enforces three things, in order:
//   1. an authenticated session (token present)
//   2. a loaded profile + menu tree (fetched once per session)
//   3. that the target path was granted to the user
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { buildRoutes, builtInRoutes } from './dynamic'

const CONSOLE_ROUTE_NAME = 'console'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, hideChrome: true },
  },
  {
    path: '/',
    name: CONSOLE_ROUTE_NAME,
    component: () => import('@/layouts/ConsoleLayout.vue'),
    // No static redirect here: `DashboardView` and friends are registered at
    // runtime by `registerDynamicRoutes()`, so a name-based redirect would fail
    // at startup ("No match for name: DashboardView"). The `beforeEach` guard
    // sends `/` to `firstAllowedPath()` once the menu tree is loaded.
    children: [
      // Populated by `registerDynamicRoutes()` after login.
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { public: true, hideChrome: true },
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

/** True once the menu-derived routes have been added for this session. */
let dynamicRegistered = false

/**
 * Does this record belong to the menu-derived set?
 *
 * Menu rows are named after `component_name` (e.g. "UserManage"), so matching
 * on a `menu-` prefix alone misses most of them. Every record produced by
 * `buildRoutes()` carries `meta.menuId`, and the fallback pages carry
 * `meta.builtIn` — those two flags are the reliable marker.
 */
function isDynamicRoute(route: { name: unknown; meta?: unknown }): boolean {
  const meta = (route.meta ?? {}) as Record<string, unknown>
  return (
    String(route.name).startsWith('menu-') ||
    meta.menuId !== undefined ||
    Boolean(meta.builtIn)
  )
}

/**
 * Register the console children derived from the user's menus.
 *
 * Safe to call repeatedly: previously added dynamic routes are removed first so
 * a role change (or a re-login as another user) cannot leak stale routes.
 */
export function registerDynamicRoutes(): void {
  const auth = useAuthStore()
  const existing = router.getRoutes()
  for (const route of existing) {
    if (route.name && isDynamicRoute(route)) {
      router.removeRoute(route.name)
    }
  }

  const dynamic = buildRoutes(auth.menus)
  const paths = new Set(dynamic.map((r) => `/${r.path}`))
  const records = [...dynamic, ...builtInRoutes(paths)]

  for (const record of records) {
    if (!record.name || router.hasRoute(record.name)) continue
    router.addRoute(CONSOLE_ROUTE_NAME, record)
  }
  dynamicRegistered = true
}

/** Drop the dynamic routes (used on logout). */
export function resetDynamicRoutes(): void {
  for (const route of router.getRoutes()) {
    if (route.name && isDynamicRoute(route)) {
      router.removeRoute(route.name)
    }
  }
  dynamicRegistered = false
}

function firstAllowedPath(): string {
  const auth = useAuthStore()
  const first = auth.menus.find((m) => m.path)?.path
  if (first) return first
  const firstChild = auth.menus.find((m) => m.children?.length)?.children?.find((c) => c.path)
  return firstChild?.path ?? '/dashboard'
}

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // 1. No session yet — send everything to the login page, remembering where
  //    the user wanted to go so a deep link survives the detour.
  if (!auth.isAuthenticated) {
    if (to.name === 'login') return true
    return { name: 'login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined }
  }

  // 2. Authenticated: load the profile + menu tree and register the routes
  //    BEFORE deciding anything about `to`.
  //
  //    This ordering is what makes a full page load on a dynamic path work.
  //    Until the menu routes are registered the console has no children, so
  //    `/system/users` resolves to the 404 catch-all — and because that
  //    catch-all is public, an earlier version of this guard allowed it
  //    immediately and never registered the real route.
  if (!auth.profile) {
    try {
      await auth.loadProfile()
    } catch {
      auth.reset()
      return { name: 'login' }
    }
  }
  if (!dynamicRegistered || !auth.menusLoaded) {
    try {
      await auth.loadMenus(true)
      registerDynamicRoutes()
    } catch {
      auth.reset()
      return { name: 'login' }
    }
    // Re-resolve the target: `to` was matched before the menu routes existed,
    // so it may now match a freshly added one. Returning the path replays the
    // navigation; the next pass skips this branch (both flags are now set), so
    // the redirect happens at most once.
    return to.fullPath
  }

  // 3. Already signed in — the login page has nothing left to offer.
  if (to.name === 'login') {
    return { path: firstAllowedPath() }
  }

  // 4. Authorisation: the path must have come from the user's menu tree.
  if (!to.meta?.public && !to.meta?.builtIn && to.meta?.permission) {
    if (!auth.hasPermission(to.meta.permission as string)) {
      return { name: 'not-found' }
    }
  }

  // 5. Root of the console -> the first page the user may actually open.
  if (to.path === '/') {
    return { path: firstAllowedPath() }
  }

  return true
})

export default router
