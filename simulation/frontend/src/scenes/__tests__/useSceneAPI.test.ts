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
