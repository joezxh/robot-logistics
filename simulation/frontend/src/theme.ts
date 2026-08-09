import { ref, watch } from 'vue'

const STORAGE_KEY = 'robot-logic.theme'

export type Theme = 'dark' | 'light'

function detectInitial(): Theme {
  if (typeof localStorage === 'undefined') return 'dark'
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'light' || stored === 'dark') return stored
  return 'dark'
}

const theme = ref<Theme>(detectInitial())

function applyTheme(t: Theme): void {
  if (typeof document !== 'undefined') {
    document.documentElement.dataset.theme = t
  }
}

applyTheme(theme.value)
watch(theme, t => {
  applyTheme(t)
  try { localStorage.setItem(STORAGE_KEY, t) } catch { /* ignore */ }
})

export function useTheme(): { theme: typeof theme; toggle: () => void } {
  function toggle(): void {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  return { theme, toggle }
}
