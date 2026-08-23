<template>
  <div>
    <header class="topbar">
      <div class="brand">
        <span class="logo">🤖</span>
        <h1>{{ t.title }}</h1>
      </div>
      <p class="subtitle">{{ t.subtitle }}</p>
      <span class="badge">{{ t.badge }}</span>
      <span class="grow"></span>
      <router-link to="/scenes" class="iconbtn" title="场景仿真">🚛 场景仿真</router-link>
      <UserMenu />
      <button class="iconbtn" @click="paletteOpen = true" :title="t.hotkey_help">⌘K</button>
      <button class="iconbtn" @click="toggleLang" title="language">🌐</button>
      <button class="iconbtn" @click="themeToggle" title="theme">🌓</button>
      <StatusBar />
      <a class="docs" href="/api" target="_blank">{{ t.api }}</a>
      <a class="docs" href="/metrics" target="_blank">{{ t.metrics }}</a>
    </header>

    <main :class="{ 'has-drawer': drawerDevice }">
      <section class="timeline">
        <TaskTimeline />
      </section>

      <section class="scene" :data-caption="t.scene_caption">
        <WarehouseScene ref="sceneRef" />
      </section>

      <aside v-if="drawerDevice" class="drawer">
        <DeviceDrawer :device-id="drawerDevice" @close="drawerDevice = ''" />
      </aside>

      <section class="panel">
        <RightTabs />
      </section>
    </main>

    <CommandPalette v-if="paletteOpen" @close="paletteOpen = false" @pick-device="onPickDevice" />

    <KpiZoom />
    <ToastHost />
    <OnboardOverlay />
    <TaskDrawer />
    <LoginOverlay />
    <HelpOverlay />
  </div>
</template>

<script setup lang="ts">
import TaskQueueChart from '../dashboard/TaskQueue.vue'
import KpiPanel from '../dashboard/Kpi.vue'
import AlertPanel from '../dashboard/Alerts.vue'
import TaskTimeline from '../dashboard/TaskTimeline.vue'
import TaskCreateForm from '../panel/TaskCreate.vue'
import RollbackPanel from '../panel/Rollback.vue'
import LogViewer from '../panel/LogViewer.vue'
import WarehouseScene from '../three/WarehouseScene.vue'
import DeviceDrawer from '../dashboard/DeviceDrawer.vue'
import CommandPalette from '../components/CommandPalette.vue'
import KpiZoom from '../dashboard/KpiZoom.vue'
import ToastHost from '../components/ToastHost.vue'
import OnboardOverlay from '../components/OnboardOverlay.vue'
import TaskDrawer from '../dashboard/TaskDrawer.vue'
import LoginOverlay from '../components/LoginOverlay.vue'
import UserMenu from '../components/UserMenu.vue'
import StatusBar from '../components/StatusBar.vue'
import HelpOverlay from '../components/HelpOverlay.vue'
import RightTabs from '../panel/RightTabs.vue'
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from '../i18n'
import { useTheme } from '../theme'

const { t, toggle: toggleLang } = useI18n()
const { toggle: themeToggle } = useTheme()

const drawerDevice = ref<string>('')
const paletteOpen = ref(false)
const sceneRef = ref<InstanceType<typeof WarehouseScene> | null>(null)

function openDrawer(id: string) {
  drawerDevice.value = id
  sceneRef.value?.follow?.(id)
}
function onPickDevice(id: string) {
  drawerDevice.value = id
  paletteOpen.value = false
  sceneRef.value?.follow?.(id)
}

function togglePalette() {
  paletteOpen.value = !paletteOpen.value
}

function refreshNow() {
  window.dispatchEvent(new CustomEvent('robot-logic:refresh'))
}

function closeDrawers() {
  drawerDevice.value = ''
}

function onKey(e: KeyboardEvent) {
  const mod = e.ctrlKey || e.metaKey
  if (mod && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    togglePalette()
  } else if (mod && e.key.toLowerCase() === 'r') {
    e.preventDefault()
    refreshNow()
  } else if (e.key === 'Escape') {
    if (paletteOpen.value) { paletteOpen.value = false; return }
    if (drawerDevice.value) { drawerDevice.value = ''; return }
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('robot-logic:toggle-palette', togglePalette)
  window.addEventListener('robot-logic:refresh', refreshNow)
  window.addEventListener('robot-logic:close-drawers', closeDrawers)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('robot-logic:toggle-palette', togglePalette)
  window.removeEventListener('robot-logic:refresh', refreshNow)
  window.removeEventListener('robot-logic:close-drawers', closeDrawers)
})
</script>
