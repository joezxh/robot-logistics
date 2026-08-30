<script setup lang="ts">
// Top bar: brand title, portal menu, theme + language switchers and the
// user dropdown (profile / logout).
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  BulbFilled,
  BulbOutlined,
  DownOutlined,
  FullscreenExitOutlined,
  FullscreenOutlined,
  GlobalOutlined,
  IdcardOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { LOCALE_LABELS, SUPPORTED_LOCALES, localise } from '@/i18n'
import { resolveIcon } from '@/utils/icons'
import { useI18n } from 'vue-i18n'
import type { AppLocale } from '@/types'

const { t } = useI18n()
const auth = useAuthStore()
const app = useAppStore()
const router = useRouter()

const currentTime = ref('')
let timer: number | undefined

function tick() {
  const now = new Date()
  const pad = (n: number) => String(n).padStart(2, '0')
  currentTime.value = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`
}

onMounted(() => {
  tick()
  timer = window.setInterval(tick, 1000)
})
onUnmounted(() => {
  if (timer) window.clearInterval(timer)
})

const isFullscreen = ref(false)

function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().then(() => (isFullscreen.value = true)).catch(() => {})
  } else {
    document.exitFullscreen().then(() => (isFullscreen.value = false)).catch(() => {})
  }
}

const initial = computed(() => auth.profile?.realName?.charAt(0)?.toUpperCase() ?? 'U')

function onUserMenu({ key }: { key: string | number }) {
  if (key === 'profile') router.push('/profile')
  if (key === 'logout') void onLogout()
}

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}

function onLocale({ key }: { key: string }) {
  app.setAppLocale(key as AppLocale)
}

function onPortalClick({ key }: { key: string | number }) {
  const path = String(key)
  if (path && path !== 'undefined') router.push(path)
}
</script>

<template>
  <header class="topbar">
    <button class="icon-btn" type="button" @click="app.toggleSidebar()">
      <MenuUnfoldOutlined v-if="app.sidebarCollapsed" />
      <MenuFoldOutlined v-else />
    </button>

    <div class="topbar-title">
      <span class="kicker">Console</span>
      <h1 class="title">{{ t('sys.brand') }}</h1>
    </div>

    <!-- Portal: direct access to the big-screen views granted to this user. -->
    <a-dropdown v-if="auth.portalMenus.length">
      <button class="portal-btn" type="button">
        <GlobalOutlined />
        <span>{{ t('sys.header.portal') }}</span>
        <DownOutlined class="caret" />
      </button>
      <template #overlay>
        <a-menu @click="onPortalClick">
          <a-menu-item v-for="m in auth.portalMenus" :key="m.path">
            <component :is="resolveIcon(m.icon)" />
            {{ localise(m.i18n, m.name) }}
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>

    <div class="spacer" />

    <span class="live-dot" aria-hidden="true" />
    <span class="clock mono">{{ currentTime }}</span>

    <a-dropdown>
      <button class="icon-btn" type="button" :title="t('sys.header.language')">
        <GlobalOutlined />
      </button>
      <template #overlay>
        <a-menu :selected-keys="[app.locale]" @click="onLocale">
          <a-menu-item v-for="loc in SUPPORTED_LOCALES" :key="loc">
            {{ LOCALE_LABELS[loc] }}
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>

    <button class="icon-btn" type="button" :title="t('sys.header.theme')" @click="app.toggleTheme()">
      <BulbFilled v-if="app.isDark" />
      <BulbOutlined v-else />
    </button>

    <button class="icon-btn" type="button" @click="toggleFullscreen">
      <FullscreenExitOutlined v-if="isFullscreen" />
      <FullscreenOutlined v-else />
    </button>

    <a-dropdown placement="bottomRight">
      <div class="user-chip">
        <a-avatar :size="30" class="avatar">{{ initial }}</a-avatar>
        <span class="user-name">{{ auth.profile?.realName ?? '-' }}</span>
        <DownOutlined class="caret" />
      </div>
      <template #overlay>
        <a-menu @click="onUserMenu">
          <a-menu-item key="profile">
            <IdcardOutlined />
            {{ t('sys.header.profile') }}
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="logout">
            <LogoutOutlined />
            {{ t('sys.header.logout') }}
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </header>
</template>

<style scoped>
.topbar {
  position: relative;
  height: var(--header-h);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 18px;
  background: var(--bg-surface);
  -webkit-backdrop-filter: var(--glass);
  backdrop-filter: var(--glass);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

/* Thin accent "system bus" line along the bottom edge of the header — reads as
 * a live instrument rail rather than a plain 1px divider. */
.topbar::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  opacity: 0.55;
  pointer-events: none;
}

.topbar-title {
  display: flex;
  flex-direction: column;
  line-height: 1;
}

.kicker {
  font-family: var(--font-tech);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--accent);
}

.title {
  margin: 3px 0 0;
  font-family: var(--font-display);
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 0.2px;
  color: var(--fg);
  white-space: nowrap;
}

.spacer {
  flex: 1;
}

.clock {
  font-size: 12px;
  color: var(--fg-secondary);
  white-space: nowrap;
}

/* Pulsing "system live" indicator sitting next to the clock. */
.live-dot {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  border-radius: 50%;
  background: var(--ok);
  box-shadow: var(--glow-ok);
  animation: live-pulse 2s ease-in-out infinite;
}

@keyframes live-pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.45;
    transform: scale(0.82);
  }
}

@media (prefers-reduced-motion: reduce) {
  .live-dot {
    animation: none;
  }
}

.icon-btn {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--fg-secondary);
  cursor: pointer;
  font-size: 15px;
  transition: all var(--transition);
}

.icon-btn:hover {
  color: var(--accent);
  border-color: var(--border-strong);
  background: var(--bg-hover);
}

.portal-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 34px;
  padding: 0 14px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--fg-secondary);
  cursor: pointer;
  font-size: 13px;
  transition: all var(--transition);
}

.portal-btn:hover {
  color: var(--accent);
  border-color: var(--border-strong);
  background: var(--bg-hover);
}

.caret {
  font-size: 10px;
  opacity: 0.7;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px 4px 4px;
  border: 1px solid var(--border);
  border-radius: 999px;
  cursor: pointer;
  transition: background var(--transition), border-color var(--transition);
}

.user-chip:hover {
  background: var(--bg-hover);
  border-color: var(--border-strong);
}

.avatar {
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  color: var(--fg-inverse) !important;
  font-weight: 700;
  flex-shrink: 0;
}

.user-name {
  font-size: 13px;
  color: var(--fg);
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .live-dot,
  .clock,
  .topbar-title {
    display: none;
  }
}
</style>
