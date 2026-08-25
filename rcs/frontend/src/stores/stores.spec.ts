import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { http } from '@/api/http'
import { useScenarioStore } from '@/stores/scenario'
import { useFloorShellStore } from '@/stores/floorShell'
import { useSiteGridStore } from '@/stores/siteGrid'

function fakeFetch(body: unknown, status = 200) {
  const fn = vi.fn(async () => ({
    ok: true,
    status,
    json: async () => body,
    text: async () => JSON.stringify(body),
  }) as unknown as Response)
  ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
  return fn
}

beforeEach(() => {
  setActivePinia(createPinia())
})

describe('useScenarioStore', () => {
  it('loadTemplates populates the list and auto-selects the first', async () => {
    fakeFetch([
      { scenario_id: 'ecommerce', name: 'Ecommerce', bounds: { w: 160, d: 100 }, zone_count: 8 },
      { scenario_id: 'port', name: 'Port', bounds: { w: 200, d: 150 }, zone_count: 8 },
    ])
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(store.templates).toHaveLength(2)
    expect(store.selected).toBe('ecommerce')
    expect(store.loading).toBe(false)
  })

  it('loadBundle fetches shell+grid+metadata for the scenario', async () => {
    fakeFetch({
      scenario_id: 'port',
      shell: { bounds: { w: 200, d: 150 } },
      grid: { site_id: 'port', bounds: { w: 200, d: 150 }, resolution: 2, cells: [[]] },
      metadata: { alert_types: ['customs_hold'] },
    })
    const store = useScenarioStore()
    await store.loadBundle('port')
    expect(store.bundle?.scenario_id).toBe('port')
    expect(store.selected).toBe('port')
  })

  it('select clears the cached bundle', async () => {
    fakeFetch({
      scenario_id: 'port',
      shell: { bounds: { w: 200, d: 150 } },
      grid: { site_id: 'port', bounds: { w: 200, d: 150 }, resolution: 2, cells: [[]] },
      metadata: {},
    })
    const store = useScenarioStore()
    await store.loadBundle('port')
    expect(store.bundle).not.toBeNull()
    store.select('ecommerce')
    expect(store.bundle).toBeNull()
    expect(store.selected).toBe('ecommerce')
  })

  it('captures errors on failure', async () => {
    const fn = vi.fn(async () => ({ ok: false, status: 500, statusText: 'X', json: async () => ({}) }) as unknown as Response)
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(store.error).toMatch(/HTTP 500/)
    expect(store.templates).toHaveLength(0)
  })
})

describe('useFloorShellStore', () => {
  it('loadByScenario pulls shell from the template bundle', async () => {
    fakeFetch({
      scenario_id: 'ecommerce',
      shell: { bounds: { w: 160, d: 100 }, zones: [{ id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 }] },
      grid: { site_id: 'ecommerce', bounds: { w: 160, d: 100 }, resolution: 2, cells: [[]] },
      metadata: {},
    })
    const store = useFloorShellStore()
    await store.loadByScenario('ecommerce')
    expect(store.shell?.bounds.w).toBe(160)
    expect(store.shell?.zones?.[0].type).toBe('flow_rack')
  })

  it('loadBySite fetches via the shell endpoint', async () => {
    let captured = ''
    const fn = vi.fn(async (url: string) => {
      captured = url
      return { ok: true, status: 200, json: async () => ({}), text: async () => JSON.stringify({ bounds: { w: 5, d: 5 } }) } as unknown as Response
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const store = useFloorShellStore()
    await store.loadBySite('site-1')
    expect(captured).toContain('/topology/shell/site-1')
    expect(store.shell?.bounds.w).toBe(5)
  })
})

describe('useSiteGridStore', () => {
  it('loadByScenario pulls grid from the template bundle', async () => {
    fakeFetch({
      scenario_id: 'multi_floor',
      shell: { bounds: { w: 80, d: 60, h: 12 } },
      grid: { site_id: 'multi_floor', bounds: { w: 80, d: 60 }, resolution: 2, cells: [[], []] },
      metadata: {},
    })
    const store = useSiteGridStore()
    await store.loadByScenario('multi_floor')
    expect(store.grid?.resolution).toBe(2)
    expect(store.grid?.cells).toHaveLength(2)
  })
})
