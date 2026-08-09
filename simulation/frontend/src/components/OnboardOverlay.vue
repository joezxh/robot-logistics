<template>
  <Teleport to="body">
    <Transition name="onb">
      <div v-if="visible" class="overlay" @click.self="skip">
        <div class="card" role="dialog" :aria-label="t.onboard.title">
          <div class="step">{{ step + 1 }} / {{ steps.length }}</div>
          <h2>{{ t.onboard.title }}</h2>
          <p class="hint">{{ steps[step].body }}</p>
          <div class="visual">
            <component :is="steps[step].visual" />
          </div>
          <div class="actions">
            <button class="ghost" @click="skip">{{ t.onboard.skip }}</button>
            <span class="grow"></span>
            <button v-if="step > 0" @click="prev">←</button>
            <button class="primary" @click="next">
              {{ step === steps.length - 1 ? t.onboard.done : t.onboard.next }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, h, computed, onMounted } from 'vue'
import { useI18n } from '../i18n'

const { t } = useI18n()
const STORAGE_KEY = 'robot-logic.onboarded'

const visible = ref(false)
const step = ref(0)

interface Step {
  body: string
  visual: ReturnType<typeof h>
}

const steps = computed((): Step[] => [
  {
    body: t.value.onboard.hint,
    visual: h('div', { class: 'kbd' }, [
      h('span', { class: 'kbd-key' }, 'Ctrl'),
      h('span', { class: 'kbd-plus' }, '+'),
      h('span', { class: 'kbd-key' }, 'K'),
      h('span', { class: 'kbd-text' }, '· 命令面板'),
    ]),
  },
  {
    body: 'Shift + 点击设备卡片进入多选模式，可批量回滚多台设备的任务。',
    visual: h('div', { class: 'kbd' }, [
      h('span', { class: 'kbd-key' }, 'Shift'),
      h('span', { class: 'kbd-plus' }, '+'),
      h('span', { class: 'kbd-key' }, '🛞'),
      h('span', { class: 'kbd-text' }, '· 批量回滚'),
    ]),
  },
  {
    body: '点击 KPI 卡片查看历史趋势；Cmd+K 可在任何时候打开。',
    visual: h('div', { class: 'kbd' }, [
      h('span', { class: 'kbd-key' }, 'KPI'),
      h('span', { class: 'kbd-plus' }, '→'),
      h('span', { class: 'kbd-key' }, '📈'),
    ]),
  },
])

function show() { visible.value = true }
function hide() { visible.value = false }
function next() {
  if (step.value < steps.value.length - 1) step.value += 1
  else { persist(); hide() }
}
function prev() {
  if (step.value > 0) step.value -= 1
}
function skip() { persist(); hide() }
function persist() {
  try { localStorage.setItem(STORAGE_KEY, '1') } catch { /* ignore */ }
}

onMounted(() => {
  let stored: string | null = null
  try { stored = localStorage.getItem(STORAGE_KEY) } catch { /* ignore */ }
  if (!stored) show()
})
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.65);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.card {
  width: min(440px, 92vw);
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 30px 80px rgba(0,0,0,0.55);
  color: var(--fg);
}
.step { font-size: 11px; color: var(--fg-soft); margin-bottom: 6px; }
h2 { margin: 0 0 10px; font-size: 18px; }
.hint { font-size: 13px; line-height: 1.6; color: var(--fg-soft); margin: 0 0 18px; }
.visual { min-height: 60px; display: flex; align-items: center; justify-content: center; padding: 12px; background: var(--bg-sub); border-radius: 8px; margin-bottom: 16px; }
.actions { display: flex; gap: 8px; align-items: center; }
.actions .grow { flex: 1; }
.actions button { padding: 6px 14px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-sub); color: var(--fg); cursor: pointer; font-size: 13px; }
.actions button.primary { background: var(--accent); color: white; border-color: var(--accent); }
.actions button.ghost { background: transparent; }

.kbd { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; }
.kbd-key {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  padding: 4px 8px;
  border-radius: 6px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  box-shadow: 0 2px 0 var(--border);
  font-family: monospace;
  font-weight: 600;
}
.kbd-plus { color: var(--fg-soft); font-weight: 700; }
.kbd-text { color: var(--fg-soft); }

.onb-enter-from, .onb-leave-to { opacity: 0; transform: translateY(8px); }
.onb-enter-active, .onb-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
</style>
