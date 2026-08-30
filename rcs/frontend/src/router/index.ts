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
 * Register the console children derived from the user's menus.
 *
 * Safe to call repeatedly: previously added dynamic routes are removed first so
 * a role change (or a re-login as another user) cannot leak stale routes.
 */
export function registerDynamicRoutes(): void {
  const auth = useAuthStore()
  const existing = router.getRoutes()
  for (const route of existing) {
    if (route.name && String(route.name).startsWith('menu-')) {
      router.removeRoute(route.name)
    }
    if (route.meta?.builtIn && route.name) {
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
    if (route.name && (String(route.name).startsWith('menu-') || route.meta?.builtIn)) {
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

  // 1. Public routes (login / 404) never require a session.
  if (to.meta?.public) {
    if (to.name === 'login' && auth.isAuthenticated) {
      return { path: firstAllowedPath() }
    }
    return true
  }

  // 2. Authentication.
  if (!auth.isAuthenticated) {
    return { name: 'login', query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined }
  }

  // 3. Make sure the profile + menu tree are loaded for this session.
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
