import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { http } from '@/api/http'

beforeAll(() => {
  // Mock echarts so jsdom (no canvas) doesn't error during DeviceMap2D init.
  vi.mock('echarts', () => ({
    init: vi.fn(() => ({ setOption: vi.fn(), resize: vi.fn(), dispose: vi.fn() })),
  }))
  // Mock three's WebGL renderer + OrbitControls for DeviceMap3D.
  vi.mock('three', async () => {
    const actual = await vi.importActual<any>('three')
    return {
      ...actual,
      WebGLRenderer: class {
        domElement = document.createElement('canvas')
        setSize = vi.fn()
        render = vi.fn()
        dispose = vi.fn()
      },
    }
  })
  vi.mock('three/examples/jsm/controls/OrbitControls.js', () => ({
    OrbitControls: class {
      target = { set: vi.fn() }
      update = vi.fn()
      dispose = vi.fn()
    },
  }))
})

const TEMPLATES = [
  { scenario_id: 'ecommerce', name: 'Ecommerce', bounds: { w: 160, d: 100 }, zone_count: 1 },
  { scenario_id: 'multi_floor', name: 'Multi-floor', bounds: { w: 80, d: 60 }, zone_count: 1 },
]

const BUNDLES: Record<string, unknown> = {
  ecommerce: {
    scenario_id: 'ecommerce',
    shell: { bounds: { w: 160, d: 100 }, zones: [
      { id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 },
    ] },
    grid: { site_id: 'ecommerce', bounds: { w: 160, d: 100 }, resolution: 2, cells: [[]] },
    metadata: {},
  },
  multi_floor: {
    scenario_id: 'multi_floor',
    shell: {
      bounds: { w: 80, d: 60, h: 12 },
      zones: [{ id: 'el1', ref: 'EL-1', type: 'elevator_shaft', x: 70, z: 50, w: 5, d: 5 }],
      floors: [
        { id: 'L1', z: 0, bounds: { w: 80, d: 60 }, zones: [] },
        { id: 'L2', z: 4, bounds: { w: 80, d: 60 }, zones: [] },
      ],
    },
    grid: { site_id: 'multi_floor', bounds: { w: 80, d: 60 }, resolution: 2, cells: [[]] },
    metadata: {},
  },
}

function routeFetch() {
  const fn = vi.fn(async (url: string) => {
    let body: unknown
    if (url.endsWith('/topology/templates')) body = TEMPLATES
    else {
      const id = url.split('/topology/templates/')[1]
      body = BUNDLES[id] ?? {}
    }
    return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
  })
  ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
  return fn
}

describe('SiteMapView', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  async function mountView() {
    routeFetch()
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: SiteMapView } = await import('./SiteMapView.vue')
    const wrapper = mount(SiteMapView, { global: { plugins: [i18n] } })
    await new Promise((r) => setTimeout(r, 20))
    return wrapper
  }

  it('renders a scenario selector with the loaded templates', async () => {
    const wrapper = await mountView()
    const options = wrapper.findAll('select').flatMap((s) => s.findAll('option'))
    expect(options.length).toBeGreaterThan(0)
    expect(options[0].text()).toBe('电商仓')
  })

  it('shows the 2D map by default and switches to 3D on toggle', async () => {
    const wrapper = await mountView()
    expect(wrapper.find('[data-testid="map2d"]').exists()).toBe(true)
    // click the 3D toggle button
    const buttons = wrapper.findAll('button')
    const threeD = buttons.find((b) => b.text() === '三维视图')!
    await threeD.trigger('click')
    expect(wrapper.find('[data-testid="map3d"]').exists()).toBe(true)
  })

  it('renders the scenario panel for the selected scenario', async () => {
    const wrapper = await mountView()
    expect(wrapper.find('.scenario-panel').exists()).toBe(true)
  })

  it('hides the floor selector when the shell has no floors', async () => {
    const wrapper = await mountView()
    // scenario <select> present, floor <select> (bound to floorIndex) absent
    const selects = wrapper.findAll('select')
    expect(selects.length).toBeGreaterThanOrEqual(1)
    const floorOptions = selects.flatMap((s) => s.findAll('option')).map((o) => o.text())
    // ecommerce shell has no floors, so no "L1"/"L2" floor options
    expect(floorOptions.some((t) => t === 'L1' || t === 'L2')).toBe(false)
  })

  it('shows a floor selector for multi_floor shells', async () => {
    routeFetch()
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: SiteMapView } = await import('./SiteMapView.vue')
    const { useScenarioStore } = await import('@/stores/scenario')
    const store = useScenarioStore()
    await store.loadTemplates()
    const wrapper = mount(SiteMapView, { global: { plugins: [i18n] } })
    await new Promise((r) => setTimeout(r, 10))
    await store.select('multi_floor')
    await new Promise((r) => setTimeout(r, 20))
    // scenario select + floor select
    expect(wrapper.findAll('select').length).toBeGreaterThanOrEqual(2)
  })
})
