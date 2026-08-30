// Simulation theme.
//
// Scoped to the simulation subtree on purpose: the original implementation set
// `document.documentElement.dataset.theme`, which would repaint the whole RCS
// console when a user toggled the theme inside an embedded simulation page.
// The value is now consumed by `SimulationRoot.vue` via `:data-theme`, so the
// variables below only ever apply inside `.sim-root`.
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

watch(theme, (t) => {
  try {
    localStorage.setItem(STORAGE_KEY, t)
  } catch {
    /* ignore */
  }
})

export function useTheme(): { theme: typeof theme; toggle: () => void } {
  function toggle(): void {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }
  return { theme, toggle }
}
