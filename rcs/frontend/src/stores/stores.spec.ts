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

// Mirrors the backend /maps/templates payload (MapTemplateInfo).
function tpl(mapId: string, name: string, nameEn: string, kind = 'warehouse') {
  return { map_id: mapId, name, name_en: nameEn, kind }
}

const WAREHOUSE_TEMPLATES = [
  tpl('tpl-ecommerce_large', '大型电商仓', 'ecommerce_large'),
  tpl('tpl-port_terminal', '港口集装箱码头', 'port_terminal'),
]

describe('useScenarioStore', () => {
  it('loadTemplates populates the list and auto-selects the first map_id', async () => {
    fakeFetch(WAREHOUSE_TEMPLATES)
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(store.templates).toHaveLength(2)
    expect(store.selected).toBe('tpl-ecommerce_large')
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
    expect(store.selected).toBe('tpl-ecommerce_large')
  })

  it('selectedTemplate and templateByKey resolve the chosen template', async () => {
    fakeFetch(WAREHOUSE_TEMPLATES)
    const store = useScenarioStore()
    await store.loadTemplates()
    expect(store.selectedTemplate?.map_id).toBe('tpl-ecommerce_large')
    expect(store.templateByKey('tpl-port_terminal')?.map_id).toBe('tpl-port_terminal')
    expect(store.templateByKey('nope')).toBeNull()

    store.select('tpl-port_terminal')
    expect(store.selectedTemplate?.map_id).toBe('tpl-port_terminal')
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
  it('loadByScenario pulls geometry from the unified map', async () => {
    const body = {
      map_id: 'tpl-ecommerce',
      name: 'Ecommerce',
      is_template: true,
      kind: 'warehouse',
      current_version: 1,
      bounds: { w: 160, d: 100 },
      geometry: { bounds: { w: 160, d: 100 }, zones: [{ id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 }] },
      topology: { nodes: [], edges: [] },
      semantic: {},
    }
    fakeFetch(body)
    const store = useFloorShellStore()
    await store.loadByScenario('ecommerce')
    expect(store.shell?.bounds.w).toBe(160)
    expect(store.shell?.zones?.[0].type).toBe('flow_rack')
  })

  it('loadBySite fetches via the maps endpoint', async () => {
    let captured = ''
    const fn = vi.fn(async (url: string) => {
      captured = url
      const body = { map_id: 'site-1', name: '', is_template: false, current_version: 1, bounds: { w: 5, d: 5 }, geometry: { bounds: { w: 5, d: 5 } }, topology: { nodes: [], edges: [] }, semantic: {} }
      return {
        ok: true, status: 200,
        json: async () => body,
        text: async () => JSON.stringify(body),
      } as unknown as Response
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const store = useFloorShellStore()
    await store.loadBySite('site-1')
    expect(captured).toContain('/maps/site-1')
    expect(store.shell?.bounds.w).toBe(5)
  })
})

describe('useSiteGridStore', () => {
  it('loadByScenario derives an empty grid from the unified map bounds', async () => {
    fakeFetch({
      map_id: 'tpl-multi_floor',
      name: 'Multi Floor',
      is_template: true,
      kind: 'warehouse',
      current_version: 1,
      bounds: { w: 80, d: 60 },
      geometry: { bounds: { w: 80, d: 60 } },
      topology: { nodes: [], edges: [] },
      semantic: {},
    })
    const store = useSiteGridStore()
    await store.loadByScenario('multi_floor')
    expect(store.grid?.site_id).toBe('tpl-multi_floor')
    expect(store.grid?.resolution).toBe(2)
    expect(store.grid?.cells).toEqual([])
  })
})
