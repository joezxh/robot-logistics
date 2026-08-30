<script setup lang="ts">
// Left navigation: the permission-filtered menu tree for the signed-in user.
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { localise } from '@/i18n'
import SidebarItem from './SidebarItem.vue'

const auth = useAuthStore()
const app = useAppStore()
const route = useRoute()
const router = useRouter()

/** Key of the currently open leaf, so the highlighted state follows the route. */
const selectedKeys = computed(() => [route.path])

/** Expand every directory that contains the active route by default. */
const openKeys = computed(() => {
  const keys: string[] = []
  const walk = (nodes: typeof auth.menus, trail: string[]) => {
    for (const node of nodes) {
      const next = [...trail, `dir-${node.id}`]
      if (node.children?.length) walk(node.children, next)
      if (node.path === route.path) keys.push(...next)
    }
  }
  walk(auth.menus, [])
  return keys
})

function onMenuClick({ key }: { key: string }) {
  if (key && key !== route.path) router.push(key)
}

/** Only directories and visible pages are shown; buttons never are. */
const visibleMenus = computed(() => auth.menus.filter((m) => m.type !== 3 && m.visible === 1))
</script>

<template>
  <aside class="sidebar" :class="{ collapsed: app.sidebarCollapsed }">
    <div class="brand">
      <span class="brand-mark">R</span>
      <span v-show="!app.sidebarCollapsed" class="brand-text">{{ localise({}, 'RCS') }}</span>
    </div>

    <a-menu
      class="sidebar-menu"
      mode="inline"
      theme="dark"
      :inline-collapsed="app.sidebarCollapsed"
      :selected-keys="selectedKeys"
      :open-keys="openKeys"
      @click="onMenuClick"
    >
      <SidebarItem v-for="node in visibleMenus" :key="node.id" :node="node" />
    </a-menu>

    <div class="sidebar-footer" v-show="!app.sidebarCollapsed">
      <button class="collapse-btn" type="button" @click="app.toggleSidebar()">
        {{ app.sidebarCollapsed ? '»' : '«' }}
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-w);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg-base);
  border-right: 1px solid var(--border);
  transition: width var(--transition);
  overflow: hidden;
}

.sidebar.collapsed {
  width: var(--sidebar-w-collapsed);
}

.brand {
  height: var(--header-h);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 15px;
  color: var(--fg-inverse);
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  flex-shrink: 0;
}

.brand-text {
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 1.5px;
  color: var(--fg);
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  border-inline-end: none !important;
  background: transparent !important;
  padding-top: 6px;
}

.sidebar-menu :deep(.ant-menu-item),
.sidebar-menu :deep(.ant-menu-submenu-title) {
  margin: 2px 8px;
  border-radius: var(--radius-sm);
  width: calc(100% - 16px);
  color: var(--fg-secondary);
}

.sidebar-menu :deep(.ant-menu-item:hover),
.sidebar-menu :deep(.ant-menu-submenu-title:hover) {
  color: var(--accent);
  background: var(--bg-hover);
}

.sidebar-menu :deep(.ant-menu-item-selected) {
  color: var(--accent);
  background: var(--accent-soft) !important;
  box-shadow: inset 2px 0 0 var(--accent);
}

.sidebar-menu :deep(.ant-menu-submenu-selected > .ant-menu-submenu-title) {
  color: var(--accent);
}

.sidebar-menu :deep(.ant-menu-inline),
.sidebar-menu :deep(.ant-menu-sub) {
  background: transparent !important;
}

.sidebar-footer {
  border-top: 1px solid var(--border);
  padding: 8px;
  flex-shrink: 0;
}

.collapse-btn {
  width: 100%;
  height: 30px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--fg-secondary);
  cursor: pointer;
  transition: all var(--transition);
}

.collapse-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--bg-hover);
}
</style>
