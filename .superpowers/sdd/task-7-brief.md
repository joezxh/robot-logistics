# Task 7 Brief — useSceneStage 7-stage state machine

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\composables\useSceneStage.ts`

## Requirements

### Step 1: 创建文件（verbatim）

```typescript
import { ref } from 'vue'

export type SceneStageName =
  | 'idle'
  | 'approach'
  | 'engage'
  | 'lift'
  | 'transfer'
  | 'place'
  | 'return'

const STAGE_ORDER: SceneStageName[] = [
  'idle',
  'approach',
  'engage',
  'lift',
  'transfer',
  'place',
  'return',
]

const STAGE_DURATION_MS: Record<SceneStageName, number> = {
  idle: 500,
  approach: 2000,
  engage: 1500,
  lift: 800,
  transfer: 2500,
  place: 1500,
  return: 2000,
}

export function useSceneStage() {
  const stage = ref<SceneStageName>('idle')

  function advance(): void {
    const idx = STAGE_ORDER.indexOf(stage.value)
    stage.value = STAGE_ORDER[(idx + 1) % STAGE_ORDER.length]
  }

  let timer: number | undefined
  function start(): void {
    stop()
    const tick = (): void => {
      advance()
      timer = window.setTimeout(tick, STAGE_DURATION_MS[stage.value])
    }
    timer = window.setTimeout(tick, STAGE_DURATION_MS[stage.value])
  }

  function stop(): void {
    if (timer !== undefined) {
      clearTimeout(timer)
      timer = undefined
    }
  }

  function reset(): void {
    stop()
    stage.value = 'idle'
  }

  return { stage, advance, start, stop, reset }
}
```

### Step 2: 类型检查

```bash
cd "d:/projects/robot-logic/simulation/frontend"
npx vue-tsc --noEmit
```

### Step 3: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/composables/useSceneStage.ts
git -c user.name="cursor" -c user.email="cursor@local" commit -m "feat(scenes): add useSceneStage 7-stage state machine"
```

## Acceptance Checklist

- [ ] 文件 verbatim
- [ ] 7 个 stage 名称正确
- [ ] `advance()` 按顺序循环（idle → approach → engage → lift → transfer → place → return → idle）
- [ ] `start()` 启动定时器切换 stage
- [ ] `stop()` 清除定时器
- [ ] `reset()` 停止 + 重置为 idle
- [ ] vue-tsc 0 new errors

## Return

`Status: DONE | commit: <7位> | test: <一行> | concerns: <无或简要>`