// Console-wide UI preferences: skin (dark/light) and sidebar state.
//
// The active *language* lives in the i18n module (`@/i18n`) because vue-i18n
// owns it; this store mirrors the choice so components can react to it and so
// the value survives a page reload.
import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import { currentLocale, detectLocale, isSupportedLocale, setLocale } from '@/i18n'
import type { AppLocale } from '@/types'

const THEME_KEY = 'rcs.console.theme'
const SIDEBAR_KEY = 'rcs.console.sidebar-collapsed'

function readStored<T extends string>(key: string, allowed: readonly T[], fallback: T): T {
  try {
    const raw = globalThis.localStorage?.getItem(key)
    if (raw && (allowed as readonly string[]).includes(raw)) return raw as T
  } catch {
    /* storage unavailable (SSR / privacy mode) */
  }
  return fallback
}

export const useAppStore = defineStore('app', () => {
  const THEMES = ['dark', 'light'] as const
  type Theme = (typeof THEMES)[number]

  const theme = ref<Theme>(readStored(THEME_KEY, THEMES, 'dark'))
  const locale = ref<AppLocale>(detectLocale())
  const sidebarCollapsed = ref(
    readStored(SIDEBAR_KEY, ['true', 'false'], 'false') === 'true',
  )
  /** Incremented whenever role/menu grants change so views can force a refresh. */
  const permissionVersion = ref(0)

  const isDark = computed(() => theme.value === 'dark')

  function applyTheme(next: Theme = theme.value) {
    if (typeof document === 'undefined') return
    document.documentElement.setAttribute('data-theme', next)
    document.documentElement.style.colorScheme = next
  }

  function setTheme(next: Theme) {
    theme.value = next
    applyTheme(next)
    try {
      globalThis.localStorage?.setItem(THEME_KEY, next)
    } catch {
      /* ignore */
    }
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  function setAppLocale(next: AppLocale) {
    if (!isSupportedLocale(next)) return
    locale.value = next
    setLocale(next)
  }

  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    try {
      globalThis.localStorage?.setItem(SIDEBAR_KEY, String(sidebarCollapsed.value))
    } catch {
      /* ignore */
    }
  }

  function bumpPermissions() {
    permissionVersion.value += 1
  }

  /** Read the persisted theme before the first paint to avoid a flash. */
  function hydrate() {
    applyTheme()
    locale.value = currentLocale()
  }

  // Keep the mirrored locale in sync when something else switches languages.
  watch(
    () => currentLocale(),
    (value) => {
      if (value !== locale.value) locale.value = value
    },
  )

  hydrate()

  return {
    theme,
    locale,
    sidebarCollapsed,
    permissionVersion,
    isDark,
    setTheme,
    toggleTheme,
    setAppLocale,
    toggleSidebar,
    bumpPermissions,
    hydrate,
  }
})
