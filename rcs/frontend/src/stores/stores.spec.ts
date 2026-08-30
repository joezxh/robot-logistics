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

// Mirrors the backend /maps/templates payload for a database warehouse template.
function tpl(key: string, name: string, category: string) {
  return {
    key,
    map_id: `tpl-${key}`,
    site_id: `tpl-${key}`,
    name,
    name_en: key,
    category,
    description: '',
    bounds: { w: 160, d: 100 },
    node_count: 60,
    edge_count: 60,
    node_types: {},
    zone_count: 8,
    facility_count: 10,
    dock_count: 4,
    wall_count: 4,
    grid_row_count: 8,
  }
}

const WAREHOUSE_TEMPLATES = [
  tpl('ecommerce_large', '大型电商仓', 'ecommerce'),
  tpl('port_terminal', '港口集装箱码头', 'port'),
]

describe('useScenarioStore', () => {
  it('loadTemplates populates the list and auto-selects the first key', async () => {
    fakeFetch(WAREHOUSE_TEMPLATES)
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(store.templates).toHaveLength(2)
    expect(store.selected).toBe('ecommerce_large')
    expect(store.loading).toBe(false)
  })

  it('self-heals an empty catalogue by seeding', async () => {
    let seeded = false
    const fn = vi.fn(async (url: string) => {
      let body: unknown
      if (url.endsWith('/maps/templates/seed')) {
        seeded = true
        body = []
      } else {
        body = seeded ? WAREHOUSE_TEMPLATES : []
      }
      return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(seeded).toBe(true)
    expect(store.templates).toHaveLength(2)
    expect(store.selected).toBe('ecommerce_large')
  })

  it('selectedTemplate and templateByKey resolve the chosen template', async () => {
    fakeFetch(WAREHOUSE_TEMPLATES)
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(store.selectedTemplate?.category).toBe('ecommerce')
    expect(store.templateByKey('port_terminal')?.site_id).toBe('tpl-port_terminal')
    expect(store.templateByKey('nope')).toBeNull()

    store.select('port_terminal')
    expect(store.selectedTemplate?.category).toBe('port')
  })

  it('select does not throw for an unknown key', async () => {
    fakeFetch(WAREHOUSE_TEMPLATES)
    const store = useScenarioStore()
    await store.loadTemplates()
    store.select('does_not_exist')
    expect(store.selected).toBe('does_not_exist')
    expect(store.selectedTemplate).toBeNull()
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
