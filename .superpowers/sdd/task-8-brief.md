# Task 8 Brief — useSceneKPI composable

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\composables\useSceneKPI.ts`

## Step 1: 创建文件（verbatim）

```typescript
import { ref } from 'vue'
import { useSceneAPI, type SceneKPI } from './useSceneAPI'

export function useSceneKPI(sceneName: string) {
  const kpi = ref<SceneKPI | null>(null)
  const { getKPI } = useSceneAPI()

  let timer: number | undefined

  async function refresh(): Promise<void> {
    try {
      kpi.value = await getKPI(sceneName)
    } catch {
      /* backend may be unavailable */
    }
  }

  function start(): void {
    stop()
    refresh()
    timer = window.setInterval(refresh, 2000)
  }

  function stop(): void {
    if (timer !== undefined) {
      clearInterval(timer)
      timer = undefined
    }
  }

  return { kpi, refresh, start, stop }
}
```

## Step 2: 类型检查

```bash
cd "d:/projects/robot-logic/simulation/frontend" && npx vue-tsc --noEmit
```

## Step 3: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/composables/useSceneKPI.ts
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add useSceneKPI composable"
```

## Acceptance

verbatim 文件；vue-tsc 0 new errors；仅 commit 1 个文件。

## Return

`Status: DONE | commit: <7位> | test: <一行> | concerns: <无或简要>`