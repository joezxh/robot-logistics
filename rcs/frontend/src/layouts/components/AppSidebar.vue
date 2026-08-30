<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import type { MenuNode } from '@/types'
import SidebarItem from './SidebarItem.vue'

const router = useRouter()
const app = useAppStore()
const auth = useAuthStore()

/**
 * The simulation console is rendered from data served by the simulation
 * backend, which holds no rows in `sys_menu` — so it can never appear in the
 * permission-filtered tree returned by `/api/sys/auth/me/menus`.
 *
 * These synthetic nodes give it a stable home in the rail. They are display-only:
 * the routes themselves are registered as built-ins in `router/dynamic.ts`, so
 * authorisation behaviour is unchanged (built-in routes carry no permission).
 * IDs are negative to avoid colliding with real `sys_menu.id` values.
 */
function leaf(id: number, name: string, path: string, icon: string): MenuNode {
  return {
    id,
    name,
    i18n: {},
    path,
    icon,
    type: 2,
    sort: 0,
    status: 1,
    visible: 1,
    keepAlive: 0,
    alwaysShow: 0,
    children: [],
  }
}

const SIMULATION_MENU: MenuNode = {
  id: -1000,
  name: '仿真中心',
  i18n: {},
  path: '/simulation',
  icon: 'RobotOutlined',
  type: 1,
  sort: 999,
  status: 1,
  visible: 1,
  keepAlive: 0,
  alwaysShow: 1,
  children: [
    leaf(-1001, '仿真总览', '/simulation', 'DashboardOutlined'),
    leaf(-1002, '场景仿真', '/simulation/scenes', 'ThunderboltOutlined'),
    leaf(-1003, '仓储仿真', '/simulation/warehouse', 'ApartmentOutlined'),
  ],
}

const menus = computed(() => [...auth.menus, SIMULATION_MENU])
const collapsed = computed(() => app.sidebarCollapsed)

const roleText = computed(() => {
  const r = auth.profile?.roles?.[0]
  return r ? r : 'operator'
})

function toggle() {
  app.toggleSidebar()
}

function onSelect(key: string) {
  if (key) router.push(key)
}
</script>

<template>
  <aside class="rail" :class="{ 'rail--collapsed': collapsed }">
    <!-- Brand -->
    <div class="rail-brand" @click="router.push('/dashboard')">
      <div class="rail-logo">
        <span class="rail-logo-mark">R</span>
      </div>
      <div class="rail-brand-text" v-show="!collapsed">
        <div class="rail-brand-name">RCS Console</div>
        <div class="rail-brand-sub">Robot Control Suite</div>
      </div>
    </div>

    <!-- Nav -->
    <nav class="rail-nav">
      <SidebarItem
        v-for="m in menus"
        :key="m.id"
        :node="m"
        :collapsed="collapsed"
        @select="onSelect"
      />
    </nav>

    <!-- Footer / status -->
    <div class="rail-foot" v-show="!collapsed">
      <div class="rail-status">
        <span class="dot" />
        <span>{{ roleText }}</span>
      </div>
      <button class="rail-collapse" :title="collapsed ? 'Expand' : 'Collapse'" @click="toggle">
        {{ collapsed ? '»' : '«' }}
      </button>
    </div>
    <button
      v-show="collapsed"
      class="rail-collapse rail-collapse--mini"
      title="Expand"
      @click="toggle"
    >
      »
    </button>
  </aside>
</template>

<style scoped>
.rail {
  position: relative;
  width: var(--sidebar-w);
  flex: 0 0 var(--sidebar-w);
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-surface);
  -webkit-backdrop-filter: var(--glass);
  backdrop-filter: var(--glass);
  border-right: 1px solid var(--border);
  transition: width var(--transition), flex-basis var(--transition);
}

.rail--collapsed {
  width: var(--sidebar-w-collapsed);
  flex-basis: var(--sidebar-w-collapsed);
}

.rail-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 18px;
  cursor: pointer;
  user-select: none;
}

.rail-logo {
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  border-radius: var(--radius);
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, var(--accent), var(--accent-hover));
  box-shadow: var(--shadow-sm);
}

.rail-logo-mark {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 20px;
  color: var(--fg-inverse);
}

:root[data-theme='light'] .rail-logo-mark {
  color: #fff;
}

.rail-brand-name {
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 16px;
  color: var(--fg);
  line-height: 1.2;
}

.rail-brand-sub {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--fg-muted);
}

.rail-nav {
  flex: 1;
  overflow-y: auto;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rail-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  border-top: 1px solid var(--divider);
}

.rail-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--fg-secondary);
  text-transform: capitalize;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: var(--ok);
  box-shadow: 0 0 0 3px var(--ok-soft);
}

.rail-collapse {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--bg-input);
  color: var(--fg-secondary);
  width: 28px;
  height: 28px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  transition: color var(--transition), border-color var(--transition);
}

.rail-collapse:hover {
  color: var(--accent);
  border-color: var(--border-strong);
}

.rail-collapse--mini {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
}
</style>
