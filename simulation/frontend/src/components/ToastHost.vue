<template>
  <div class="toast-host" aria-live="polite" aria-atomic="false">
    <TransitionGroup name="toast" tag="ul" class="list">
      <li
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="t.kind"
        role="status"
        @click="dismiss(t.id)"
      >
        <span class="icon" :class="`icon-${t.kind}`">{{ icon(t.kind) }}</span>
        <div class="body">
          <div class="title">{{ t.title }}</div>
          <div v-if="t.message" class="message">{{ t.message }}</div>
        </div>
        <button class="close" @click.stop="dismiss(t.id)" :aria-label="t.title">×</button>
      </li>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { toasts, dismissToast } from '../composables/toast'

function dismiss(id: number) {
  dismissToast(id)
}

function icon(kind: string): string {
  switch (kind) {
    case 'success':
      return '✓'
    case 'warning':
      return '⚠'
    case 'error':
      return '✕'
    default:
      return 'ℹ'
  }
}
</script>

<style scoped>
.toast-host {
  position: fixed;
  top: 64px;
  right: 16px;
  z-index: 9999;
  pointer-events: none;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 360px;
}
.toast {
  pointer-events: auto;
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 10px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  border-radius: 6px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.18);
  cursor: pointer;
  font-size: 13px;
  color: var(--fg);
}
.toast.success { border-left-color: #4caf50; }
.toast.warning { border-left-color: #f59e0b; }
.toast.error { border-left-color: #ef4444; }
.toast.info { border-left-color: #3b82f6; }
.icon {
  font-weight: 700;
  font-size: 16px;
  line-height: 1;
  width: 18px;
  text-align: center;
  flex-shrink: 0;
}
.icon-success { color: #4caf50; }
.icon-warning { color: #f59e0b; }
.icon-error { color: #ef4444; }
.icon-info { color: #3b82f6; }
.body { flex: 1; min-width: 0; }
.title { font-weight: 600; margin-bottom: 2px; }
.message { font-size: 12px; color: var(--fg-soft); line-height: 1.45; }
.close {
  background: transparent;
  border: 0;
  color: var(--fg-soft);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  padding: 0 4px;
}
.close:hover { color: var(--fg); }
.toast-enter-from { opacity: 0; transform: translateX(20px); }
.toast-leave-to { opacity: 0; transform: translateX(20px); }
.toast-enter-active, .toast-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
</style>
