# Task 16 Brief — vitest for useSceneAPI + useSceneStage

## Files

- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\__tests__\useSceneAPI.test.ts`
- **Create**: `d:\projects\robot-logic\simulation\frontend\src\scenes\__tests__\useSceneStage.test.ts`

## Step 1: useSceneAPI.test.ts（verbatim from plan）

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { useSceneAPI } from '../composables/useSceneAPI'

vi.mock('axios')
const mockedAxios = axios as unknown as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> }

describe('useSceneAPI', () => {
  beforeEach(() => {
    mockedAxios.get = vi.fn()
    mockedAxios.post = vi.fn()
  })

  it('list() returns available scenes', async () => {
    mockedAxios.get.mockResolvedValue({ data: { available: ['pallet', 'box', 'bag'], current: null } })
    const { list } = useSceneAPI()
    const result = await list()
    expect(result.available).toEqual(['pallet', 'box', 'bag'])
    expect(result.current).toBeNull()
  })

  it('load(name) updates currentScene', async () => {
    mockedAxios.post.mockResolvedValue({ data: { scene: 'pallet', devices: [], sites: [] } })
    const { load, currentScene } = useSceneAPI()
    await load('pallet')
    expect(currentScene.value).toBe('pallet')
  })

  it('getKPI() returns snapshot', async () => {
    mockedAxios.get.mockResolvedValue({ data: { scene: 'box', throughput_per_hour: 50, success_rate: 98, active_tasks: 1, completed_tasks: 2, failed_tasks: 0 } })
    const { getKPI } = useSceneAPI()
    const kpi = await getKPI('box')
    expect(kpi.throughput_per_hour).toBe(50)
  })
})
```

## Step 2: useSceneStage.test.ts（verbatim from plan）

```typescript
import { describe, it, expect } from 'vitest'
import { useSceneStage, type SceneStageName } from '../composables/useSceneStage'

describe('useSceneStage', () => {
  it('starts at idle', () => {
    const { stage } = useSceneStage()
    expect(stage.value).toBe('idle')
  })

  it('advance cycles through stages', () => {
    const { stage, advance } = useSceneStage()
    const expected: SceneStageName[] = ['approach', 'engage', 'lift', 'transfer', 'place', 'return', 'idle']
    for (const want of expected) {
      advance()
      expect(stage.value).toBe(want)
    }
  })

  it('reset() returns to idle and stops timer', () => {
    const { stage, start, stop, reset } = useSceneStage()
    start()
    reset()
    expect(stage.value).toBe('idle')
    stop()
  })
})
```

## Step 3: 运行 vitest

```bash
cd "d:/projects/robot-logic/simulation/frontend"
npx vitest run src/scenes/__tests__
```

期望：2 test files pass, all assertions pass.

注：`vitest` 在 package.json 中**没有**显式依赖。需要先 `npm install --save-dev vitest @vitest/ui jsdom`（如果未安装）。

如 vitest 未安装，先跑：
```bash
cd "d:/projects/robot-logic/simulation/frontend"
npm install --save-dev vitest@^1.6.0
```

## Step 4: 提交

```bash
cd d:/projects/robot-logic
git add simulation/frontend/src/scenes/__tests__/useSceneAPI.test.ts
git add simulation/frontend/src/scenes/__tests__/useSceneStage.test.ts
git -c user.name="cursor" -c user.email="cursor@local" commit -m "test(scenes): add vitest for useSceneAPI + useSceneStage"
```

如需 commit package.json + package-lock.json（vitest 安装），在 commit 前一并 add。

## Acceptance

- [ ] vitest 安装成功（如需）
- [ ] 2 个测试文件创建
- [ ] `npx vitest run src/scenes/__tests__` 全部通过
- [ ] 仅 commit 这 2 个 test 文件 + 必要的 npm 锁文件

## Return

`Status: DONE | commit: <7位> | test: <N passed> | concerns: <无或简要>`