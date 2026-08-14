# Task 11 Brief — ScenesPage.vue (top route + Tab switcher)

## Files

- **Modify**: `d:\projects\robot-logic\simulation\frontend\src\scenes\ScenesPage.vue`（覆盖 Task 5 占位 stub）

## Requirements

### Step 1: 完整覆盖文件（verbatim from plan）

```vue
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
```

**注意**：引用 `./SceneStage.vue`，该文件由 **Task 12** 创建。本 Task 仅创建 ScenesPage.vue，运行时 SceneStage.vue 缺失会 vue-tsc 报"Cannot find module"，但这是 Task 12 应解决的问题。

### Step 2: 类型检查

```bash
cd "d:/projects/robot-logic/simulation/frontend" && npx vue-tsc --noEmit
```

期望：可能报 1 个"Cannot find module './SceneStage.vue'" 错误（正常，因 Task 12 未做）。这不阻塞 Tasks 11+12 的 commit 分开。

### Step 3: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/ScenesPage.vue
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add ScenesPage with Tab switcher for Top 3 scenes"
```

## Acceptance

- [ ] ScenesPage.vue 内容覆盖 Task 5 stub
- [ ] 含 topbar / tabs / stage 三个区域
- [ ] 切换 tab 调用 `useSceneAPI().load(name)`
- [ ] onMounted 调用 `list()` 获取当前场景
- [ ] 现有 vue-tsc 错误数不变（新增"Cannot find module SceneStage.vue"是预期）

## Return

`Status: DONE | commit: <7位> | test: <一行> | concerns: <无或简要>`