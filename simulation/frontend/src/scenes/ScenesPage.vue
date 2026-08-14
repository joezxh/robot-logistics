<template>
  <div class="scenes-page">
    <header class="topbar">
      <router-link to="/" class="iconbtn" title="返回 Dashboard">← Dashboard</router-link>
      <span class="logo">🚛</span>
      <h1>场景仿真</h1>
      <span class="grow"></span>
      <span class="badge" v-if="currentScene">{{ currentScene }}</span>
    </header>

    <nav class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.name"
        :class="['tab', { active: currentTab === tab.name }]"
        @click="onSwitch(tab.name)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <main class="stage">
      <SceneStage
        v-if="currentTab"
        :key="currentTab"
        :scene-name="currentTab"
      />
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import SceneStage from './SceneStage.vue'
import { useSceneAPI } from './composables/useSceneAPI'

interface TabSpec {
  name: 'pallet' | 'box' | 'bag'
  label: string
}

const tabs: TabSpec[] = [
  { name: 'pallet', label: '📦 托盘 (🥇)' },
  { name: 'box', label: '📦 箱装 (🥈)' },
  { name: 'bag', label: '📦 袋装 (🥉)' },
]

const currentTab = ref<'' | 'pallet' | 'box' | 'bag'>('pallet')
const currentScene = ref<string>('')
const { load, list } = useSceneAPI()

async function onSwitch(name: 'pallet' | 'box' | 'bag') {
  currentTab.value = name
  await load(name)
  currentScene.value = name
}

onMounted(async () => {
  try {
    const info = await list()
    currentScene.value = info.current ?? ''
  } catch {
    /* backend may be down */
  }
})
</script>

<style scoped>
.scenes-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--bg-app);
}
.topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.topbar h1 {
  font-size: 16px;
  margin: 0;
  font-weight: 600;
}
.topbar .logo { font-size: 20px; }
.topbar .grow { flex: 1; }
.topbar .badge {
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--accent);
  color: white;
  font-size: 11px;
  font-weight: 600;
}
.tabs {
  display: flex;
  gap: 4px;
  padding: 8px 24px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
}
.tab {
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  color: var(--fg);
  padding: 6px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.tab.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}
.stage {
  flex: 1;
  min-height: 0;
}
.iconbtn {
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  color: var(--fg);
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  text-decoration: none;
}
</style>
