import { describe, it, expect, vi, beforeEach, beforeAll } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { http } from '@/api/http'
import Antd from 'ant-design-vue'

beforeAll(() => {
  // Polyfills required by ant-design-vue in jsdom.
  if (!window.matchMedia) {
    window.matchMedia = ((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })) as unknown as typeof window.matchMedia
  }
  if (!('ResizeObserver' in globalThis)) {
    ;(globalThis as any).ResizeObserver = class {
      observe = vi.fn()
      unobserve = vi.fn()
      disconnect = vi.fn()
    }
  }
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
        setPixelRatio = vi.fn()
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
  // jsdom has no WebGL context, so stub the post-processing chain that
  // DeviceMap3D uses for its bloom pass.
  vi.mock('three/examples/jsm/postprocessing/EffectComposer.js', () => ({
    EffectComposer: class {
      addPass = vi.fn()
      render = vi.fn()
      setSize = vi.fn()
      dispose = vi.fn()
    },
  }))
  vi.mock('three/examples/jsm/postprocessing/RenderPass.js', () => ({
    RenderPass: class {
      scene = null
      camera = null
    },
  }))
  vi.mock('three/examples/jsm/postprocessing/UnrealBloomPass.js', () => ({
    UnrealBloomPass: class {},
  }))
  vi.mock('three/examples/jsm/postprocessing/OutputPass.js', () => ({
    OutputPass: class {},
  }))
})

// Mirrors GET /api/rcs/maps/templates — the database warehouse templates.
function tpl(key: string, name: string, nameEn: string, kind = 'warehouse') {
  return { map_id: `tpl-${key}`, name, name_en: nameEn, kind }
}

const TEMPLATES = [
  tpl('ecommerce_large', '大型电商仓', 'ecommerce_large'),
  tpl('multi_floor_demo', '多层仓', 'multi_floor_demo'),
]

// Mirrors GET /api/rcs/maps/{map_id} — geometry is the FloorShell.
const MAPS: Record<string, unknown> = {
  'tpl-ecommerce_large': {
    map_id: 'tpl-ecommerce_large',
    name: '大型电商仓',
    is_template: true,
    kind: 'warehouse',
    current_version: 1,
    bounds: { w: 160, d: 100 },
    geometry: {
      bounds: { w: 160, d: 100 },
      zones: [{ id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 }],
    },
    topology: { nodes: [], edges: [] },
    semantic: {},
  },
  'tpl-multi_floor_demo': {
    map_id: 'tpl-multi_floor_demo',
    name: '多层仓',
    is_template: true,
    kind: 'warehouse',
    current_version: 1,
    bounds: { w: 80, d: 60 },
    geometry: {
      bounds: { w: 80, d: 60, h: 12 },
      zones: [{ id: 'el1', ref: 'EL-1', type: 'elevator_shaft', x: 70, z: 50, w: 5, d: 5 }],
      floors: [
        { id: 'L1', z: 0, bounds: { w: 80, d: 60 }, zones: [] },
        { id: 'L2', z: 4, bounds: { w: 80, d: 60 }, zones: [] },
      ],
    },
    topology: { nodes: [], edges: [] },
    semantic: {},
  },
}

function routeFetch() {
  const fn = vi.fn(async (url: string) => {
    let body: unknown = {}
    if (url.endsWith('/maps/templates')) body = TEMPLATES
    else if (url.includes('/maps/tpl-')) {
      const id = url.split('/maps/')[1]
      body = MAPS[id] ?? {}
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
    const wrapper = mount(SiteMapView, { global: { plugins: [i18n, Antd] } })
    await new Promise((r) => setTimeout(r, 20))
    return wrapper
  }

  it('renders a scenario selector with the loaded templates', async () => {
    const wrapper = await mountView()
    const selects = wrapper.findAll('.ant-select')
    expect(selects.length).toBeGreaterThanOrEqual(1)
    // scenario options are rendered inside the select after templates load
    const { useScenarioStore } = await import('@/stores/scenario')
    expect(useScenarioStore().templates.length).toBeGreaterThan(0)
  })

  it('shows the 2D map by default and switches to 3D on toggle', async () => {
    const wrapper = await mountView()
    expect(wrapper.find('[data-testid="map2d"]').exists()).toBe(true)
    // click the underlying radio input for the 3D option so AntD change fires
    const threeD = wrapper.findAll('.ant-radio-button-wrapper').find((b) => b.text() === '三维视图')!
    await threeD.find('.ant-radio-button-input').trigger('change')
    await new Promise((r) => setTimeout(r, 10))
    expect(wrapper.find('[data-testid="map3d"]').exists()).toBe(true)
  })

  it('renders the scenario panel for the selected scenario', async () => {
    const wrapper = await mountView()
    expect(wrapper.find('.scenario-panel').exists()).toBe(true)
  })

  it('hides the floor selector when the shell has no floors', async () => {
    const wrapper = await mountView()
    // scenario a-select present, floor a-select (bound to floorIndex) absent for ecommerce
    const selects = wrapper.findAll('.ant-select')
    expect(selects.length).toBe(1)
  })

  it('shows a floor selector for multi_floor shells', async () => {
    routeFetch()
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: SiteMapView } = await import('./SiteMapView.vue')
    const { useScenarioStore } = await import('@/stores/scenario')
    const store = useScenarioStore()
    await store.loadTemplates()
    const wrapper = mount(SiteMapView, { global: { plugins: [i18n, Antd] } })
    await new Promise((r) => setTimeout(r, 10))
    await store.select('tpl-multi_floor_demo')
    await new Promise((r) => setTimeout(r, 20))
    // template select + floor select
    expect(wrapper.findAll('.ant-select').length).toBeGreaterThanOrEqual(2)
  })
})
