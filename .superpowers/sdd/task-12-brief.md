# Task 12 Brief — SceneStage 5-panel framework

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\SceneStage.vue`

## Plan Defect Corrected

Plan 使用 `@/dashboard/...` / `@/panel/...` 路径别名，但 tsconfig.json 未配置 `paths` 别名。**修正**：改用相对路径 `../dashboard/TaskTimeline.vue` 等。

## Step 1: 创建文件（verbatim，import 改相对路径）

```vue
<template>
  <div class="stage">
    <div class="left">
      <div class="scene-area">
        <component :is="sceneComponent" v-if="sceneComponent" />
        <div v-else class="placeholder">3D 场景加载中...</div>
      </div>
      <div class="timeline">
        <TaskTimeline />
      </div>
      <div class="logs">
        <LogViewer />
      </div>
    </div>

    <aside class="right">
      <DeviceStatus />
      <div class="kpi-panel">
        <h3>场景 KPI</h3>
        <div v-if="kpi" class="kpi-cards">
          <div v-for="d in kpiCards" :key="d.key" class="kpi-card">
            <div class="kpi-label">{{ d.label }}</div>
            <div class="kpi-value">{{ d.value }}</div>
            <div class="kpi-target">{{ d.target }}</div>
          </div>
        </div>
        <div v-else class="placeholder">KPI 计算中...</div>
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import TaskTimeline from '../dashboard/TaskTimeline.vue'
import LogViewer from '../panel/LogViewer.vue'
import DeviceStatus from '../dashboard/DeviceStatus.vue'
import { useSceneKPI } from './composables/useSceneKPI'

interface Props {
  sceneName: 'pallet' | 'box' | 'bag'
}
const props = defineProps<Props>()

const sceneComponent = computed(() => {
  switch (props.sceneName) {
    case 'pallet':
      return () => import('./ScenePallet.vue')
    case 'box':
      return () => import('./SceneBox.vue')
    case 'bag':
      return () => import('./SceneBag.vue')
    default:
      return null
  }
})

const { kpi, start: startKpi, stop: stopKpi } = useSceneKPI(props.sceneName)

const kpiCards = computed(() => {
  if (!kpi.value) return []
  return [
    { key: 'throughput', label: '吞吐量', value: String(kpi.value.throughput_per_hour), target: '/h' },
    { key: 'success', label: '成功率', value: `${kpi.value.success_rate}%`, target: '' },
    { key: 'active', label: '活跃任务', value: String(kpi.value.active_tasks), target: '' },
    { key: 'completed', label: '已完成', value: String(kpi.value.completed_tasks), target: '' },
  ]
})

onMounted(() => startKpi())
onUnmounted(() => stopKpi())
</script>

<style scoped>
.stage {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(280px, 1fr);
  height: 100%;
  padding: 12px;
  gap: 12px;
}
.left {
  display: grid;
  grid-template-rows: minmax(0, 1.4fr) auto auto;
  gap: 12px;
  min-height: 0;
}
.scene-area {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  min-height: 0;
}
.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--fg-soft);
  font-size: 13px;
}
.right {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
  overflow-y: auto;
}
.kpi-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
}
.kpi-panel h3 {
  font-size: 13px;
  margin: 0 0 8px 0;
  color: var(--fg);
}
.kpi-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.kpi-card {
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px;
  text-align: center;
}
.kpi-label { font-size: 10px; color: var(--fg-soft); }
.kpi-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent);
  margin: 4px 0;
}
.kpi-target { font-size: 10px; color: var(--fg-muted); }
</style>
```

### Step 2: 类型检查

如 vue-tsc 因 `ScenePallet.vue` / `SceneBox.vue` / `SceneBag.vue` 缺失报错，先创建 3 个最小 stub：

```vue
<!-- ScenePallet.vue stub -->
<template><div class="placeholder">托盘场景</div></template>
<script setup lang="ts"></script>

<!-- SceneBox.vue stub -->
<template><div class="placeholder">箱装场景</div></template>
<script setup lang="ts"></script>

<!-- SceneBag.vue stub -->
<template><div class="placeholder">袋装场景</div></template>
<script setup lang="ts"></script>
```

Task 13-15 会分别覆盖这些 stub。如 vue-tsc 不报错，可直接下一步。

```bash
cd "d:/projects/robot-logic/simulation/frontend" && npx vue-tsc --noEmit
```

### Step 3: 提交

**仅** SceneStage.vue 单独 commit（stub 文件由 Task 13-15 处理）：

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/SceneStage.vue
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add SceneStage 5-panel framework"
```

如需先 commit stub：

```bash
git add simulation/frontend/src/scenes/ScenePallet.vue
git add simulation/frontend/src/scenes/SceneBox.vue
git add simulation/frontend/src/scenes/SceneBag.vue
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add ScenePallet/Box/Bag placeholder stubs"
```

请根据实际 vue-tsc 行为决定。如 Step 2 失败需 stub，先 commit stub；否则仅 commit SceneStage.vue。

## Acceptance

- [ ] SceneStage.vue 创建（5 面板布局）
- [ ] `TaskTimeline` / `LogViewer` / `DeviceStatus` 用相对路径 import
- [ ] useSceneKPI 启动/停止在 mount/unmount
- [ ] vue-tsc 0 new errors
- [ ] commit 文件按需（SceneStage.vue +/- stub）

## Return

`Status: DONE | commit: <7位> | test: <一行> | concerns: <无或简要>`