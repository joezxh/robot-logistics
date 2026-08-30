// Turn the backend menu tree into vue-router records.
//
// `sys_menu.component` stores a path relative to `src/` (e.g.
// "views/system/UserManage.vue"). Vite's `import.meta.glob` gives us a lazy
// loader for every view at build time, so a menu added in the database becomes
// a route without touching front-end code.
import type { RouteRecordRaw } from 'vue-router'
import type { MenuNode } from '@/types'

/** Eager-ish glob: keys are "/src/views/...", values are dynamic imports. */
const viewModules = import.meta.glob('/src/views/**/*.vue')

/** A console page that has no row in the backend menu tree. */
interface BuiltInView {
  component: string
  name: string
  title: string
}

/** Static pages rendered inside the console shell that have no menu row. */
const BUILT_IN_VIEWS: Record<string, BuiltInView> = {
  '/dashboard': { component: 'views/DashboardView.vue', name: 'DashboardView', title: 'Dashboard' },
  '/profile': { component: 'views/ProfileView.vue', name: 'ProfileView', title: 'Profile' },
  // Simulation console. Its data comes from the simulation backend (`/api`),
  // which owns no rows in `sys_menu`, so these routes can never be granted via
  // the menu tree. Registering them as built-ins makes the guard admit them;
  // the sidebar renders them from a synthetic node (see `AppSidebar.vue`).
  '/simulation': {
    component: 'views/simulation/DashboardEntry.vue',
    name: 'SimulationDashboard',
    title: '仿真总览',
  },
  '/simulation/scenes': {
    component: 'views/simulation/ScenesEntry.vue',
    name: 'SimulationScenes',
    title: '场景仿真',
  },
  '/simulation/warehouse': {
    component: 'views/simulation/WarehouseEntry.vue',
    name: 'SimulationWarehouse',
    title: '仓储仿真',
  },
}

function resolveComponent(componentPath: string | null | undefined): RouteRecordRaw['component'] | undefined {
  if (!componentPath) return undefined
  const normalised = componentPath.startsWith('/src/')
    ? componentPath
    : `/src/${componentPath.replace(/^\/+/, '')}`
  return viewModules[normalised] as RouteRecordRaw['component'] | undefined
}

/**
 * Build route records for every navigable menu node.
 *
 * Directories (type 1) are skipped as routes — their children carry the real
 * paths. Button permissions (type 3) are skipped entirely.
 */
export function buildRoutes(nodes: MenuNode[], parentPath = ''): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []

  for (const node of nodes) {
    const rawPath = node.path ?? ''
    // Join parent + child so "/system" + "/users" -> "/system/users".
    const fullPath = rawPath.startsWith('/')
      ? rawPath
      : `${parentPath}/${rawPath}`.replace(/\/+/g, '/')

    if (node.type === 2 && node.component) {
      const component = resolveComponent(node.component)
      if (component) {
        routes.push({
          path: fullPath.replace(/^\//, ''),
          name: node.componentName || `menu-${node.id}`,
          component,
          meta: {
            menuId: node.id,
            permission: node.permission ?? undefined,
            title: node.name,
            i18n: node.i18n,
            icon: node.icon ?? undefined,
            keepAlive: node.keepAlive === 1,
          },
        })
      } else {
        console.warn(
          `[router] menu "${node.name}" (${node.permission}) points at an unknown component: ${node.component}`,
        )
      }
    }

    if (node.children?.length) {
      routes.push(...buildRoutes(node.children, node.type === 2 ? '' : fullPath))
    }
  }

  return routes
}

/**
 * Ensure the always-available console pages exist even when the database menu
 * rows were removed or the role does not grant them.
 */
export function builtInRoutes(existingPaths: Set<string>): RouteRecordRaw[] {
  const routes: RouteRecordRaw[] = []
  for (const [path, view] of Object.entries(BUILT_IN_VIEWS)) {
    if (existingPaths.has(path)) continue
    const component = resolveComponent(view.component)
    if (!component) continue
    routes.push({
      path: path.replace(/^\//, ''),
      name: view.name,
      component,
      meta: { builtIn: true, title: view.title },
    })
  }
  return routes
}
