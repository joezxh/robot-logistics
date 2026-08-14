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
