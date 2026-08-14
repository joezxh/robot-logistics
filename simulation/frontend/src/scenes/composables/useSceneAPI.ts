import { ref } from 'vue'
import axios from 'axios'

export interface ScenePreset {
  name: string
  label: string
  description: string
  sites: Array<Record<string, unknown>>
  devices: Array<Record<string, unknown>>
  tasks: Array<Record<string, unknown>>
  kpi_definitions: Array<Record<string, unknown>>
}

export interface SceneKPI {
  scene: string
  throughput_per_hour: number
  success_rate: number
  active_tasks: number
  completed_tasks: number
  failed_tasks: number
}

export function useSceneAPI() {
  const currentScene = ref<string>('')

  async function list(): Promise<{ available: string[]; current: string | null }> {
    const res = await axios.get('/api/scenes')
    return res.data
  }

  async function load(name: string): Promise<ScenePreset & { devices: unknown[]; sites: unknown[] }> {
    const res = await axios.post(`/api/scenes/load/${name}`)
    currentScene.value = name
    return res.data
  }

  async function getCurrent(): Promise<ScenePreset> {
    const res = await axios.get('/api/scenes/current')
    return res.data
  }

  async function getKPI(name: string): Promise<SceneKPI> {
    const res = await axios.get(`/api/scenes/${name}/kpi`)
    return res.data
  }

  return { currentScene, list, load, getCurrent, getKPI }
}