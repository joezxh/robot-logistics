import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { http } from '@/api/http'
import { useDeviceStore } from '@/stores/devices'

function fakeFetch(body: unknown, status = 200) {
  const fn = vi.fn(async () => ({
    ok: true, status,
    json: async () => body,
    text: async () => JSON.stringify(body),
  }) as unknown as Response)
  ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
  return fn
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('useDeviceStore', () => {
  it('loadRegistry populates devices and health', async () => {
    fakeFetch({ devices: [{ device_id: 'R-01', morphology: 'arm', num_joints: 6, control_hz: 50, robot_type: null }] })
    // health call also hits fetch
    const store = useDeviceStore()
    await store.loadRegistry()
    expect(store.devices).toHaveLength(1)
    expect(store.devices[0].device_id).toBe('R-01')
    expect(store.loading).toBe(false)
  })

  it('refreshState records per-device state', async () => {
    fakeFetch({ device_id: 'R-01', mode: 'moving', active_command_id: 'c1', last_error: null })
    const store = useDeviceStore()
    await store.refreshState('R-01')
    expect(store.states['R-01'].mode).toBe('moving')
  })

  it('estop updates device state', async () => {
    const fn = vi.fn(async (url: string) => {
      if (url.includes('/estop')) {
        const body = { status: 'estop', device_id: 'R-01' }
        return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
      }
      // refreshState -> GET /state
      const body = { device_id: 'R-01', mode: 'estopped', active_command_id: null, last_error: null }
      return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const store = useDeviceStore()
    await store.estop('R-01')
    expect(store.states['R-01'].mode).toBe('estopped')
  })

  it('captures errors on registry failure', async () => {
    const fn = vi.fn(async () => ({ ok: false, status: 500, statusText: 'X', json: async () => ({}) }) as unknown as Response)
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const store = useDeviceStore()
    await store.loadRegistry()
    expect(store.error).toMatch(/HTTP 500/)
    expect(store.devices).toHaveLength(0)
  })
})
