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
