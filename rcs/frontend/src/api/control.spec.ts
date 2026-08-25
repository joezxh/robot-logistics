import { describe, it, expect, vi } from 'vitest'
import { http } from '@/api/http'
import {
  listDevices, getDeviceState, sendCommand, estop, clearEstop, controlHealth,
} from '@/api/control'

const okRes = (body: unknown, status = 200): Response =>
  ({ ok: true, status, json: async () => body, text: async () => JSON.stringify(body) }) as unknown as Response

function mockFetch(fn: (url: string, init?: RequestInit) => Response) {
  ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = vi.fn(fn) as unknown as typeof fetch
}

describe('control API', () => {
  it('listDevices GET /registry', async () => {
    mockFetch((url) => {
      expect(url).toBe('/api/rcs/registry')
      return okRes({ devices: [{ device_id: 'R-01', morphology: 'arm', num_joints: 6, control_hz: 50 }] })
    })
    const out = await listDevices()
    expect(out.devices[0].device_id).toBe('R-01')
  })

  it('getDeviceState GET /:id/state', async () => {
    mockFetch((url) => {
      expect(url).toBe('/api/rcs/R-01/state')
      return okRes({ device_id: 'R-01', mode: 'idle', active_command_id: null, last_error: null })
    })
    const st = await getDeviceState('R-01')
    expect(st.mode).toBe('idle')
  })

  it('sendCommand POSTs /:id/command', async () => {
    mockFetch((url, init) => {
      expect(url).toBe('/api/rcs/R-01/command')
      expect(init?.method).toBe('POST')
      const body = JSON.parse(init!.body as string)
      expect(body.type).toBe('estop')
      return okRes({ status: 'accepted', device_id: 'R-01' })
    })
    const out = await sendCommand('R-01', { type: 'estop' })
    expect(out.status).toBe('accepted')
  })

  it('estop posts /:id/estop', async () => {
    mockFetch((url) => {
      expect(url).toBe('/api/rcs/R-01/estop')
      return okRes({ status: 'estop', device_id: 'R-01' })
    })
    const out = await estop('R-01')
    expect(out.status).toBe('estop')
  })

  it('clearEstop posts /:id/clear_estop', async () => {
    mockFetch((url) => {
      expect(url).toBe('/api/rcs/R-01/clear_estop')
      return okRes({ status: 'cleared', device_id: 'R-01' })
    })
    const out = await clearEstop('R-01')
    expect(out.status).toBe('cleared')
  })

  it('controlHealth GET /_health', async () => {
    mockFetch((url) => {
      expect(url).toBe('/api/rcs/_health')
      return okRes({ running: true, loop: 'ok' })
    })
    const h = await controlHealth()
    expect(h.running).toBe(true)
  })
})
