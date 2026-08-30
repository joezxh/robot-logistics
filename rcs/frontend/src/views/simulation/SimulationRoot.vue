<script setup lang="ts">
// Root of every embedded simulation page.
//
// Responsibilities that used to live in the standalone app's `App.vue`:
//   * render `.sim-root`, the style scope for `simulation.css`
//   * bind the simulation's own theme (scoped, never `documentElement`)
//   * broadcast global hotkeys as window CustomEvents
//   * own the task-watcher timer so leaving the page stops the polling
//
// The stylesheet is imported here (not in `main.ts`) so it is only fetched when
// a simulation route is actually opened.
import { onMounted, onUnmounted } from 'vue'
import { useTheme } from './theme'
import { startTaskWatcher } from './composables/taskWatcher'
import './simulation.css'

const { theme } = useTheme()

let stopWatcher: (() => void) | undefined

function onKey(e: KeyboardEvent): void {
  const mod = e.ctrlKey || e.metaKey
  if (mod && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    window.dispatchEvent(new CustomEvent('robot-logic:toggle-palette'))
  } else if (mod && e.key.toLowerCase() === 'r') {
    e.preventDefault()
    window.dispatchEvent(new CustomEvent('robot-logic:refresh'))
  } else if (e.key === 'Escape') {
    window.dispatchEvent(new CustomEvent('robot-logic:close-drawers'))
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  stopWatcher = startTaskWatcher()
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  stopWatcher?.()
})
</script>

<template>
  <div class="sim-root" :data-theme="theme">
    <slot />
  </div>
</template>
