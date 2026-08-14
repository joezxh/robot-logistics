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
