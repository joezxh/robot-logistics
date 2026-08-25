import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shellToRects, buildMapOption, zoneColor } from './option'
import type { FloorShell } from '@/types'

const sampleShell: FloorShell = {
  bounds: { w: 160, d: 100 },
  zones: [
    { id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 },
    { id: 'z2', ref: 'R2', type: 'high_rack', x: 60, z: 0, w: 60, d: 40 },
  ],
}

describe('option builder', () => {
  it('zoneColor returns palette colors and a fallback', () => {
    expect(zoneColor('flow_rack')).toBe('#38bdf8')
    expect(zoneColor('unknown_zzz')).toBe('#94a3b8')
  })

  it('shellToRects maps zone x/z/w/d to axis rectangles', () => {
    const rects = shellToRects(sampleShell)
    expect(rects).toHaveLength(2)
    expect(rects[0]).toMatchObject({ id: 'z1', ref: 'R1', x: 0, y: 0, w: 60, h: 40, color: '#38bdf8' })
  })

  it('buildMapOption sets axis bounds from shell.bounds', () => {
    const opt = buildMapOption({ shell: sampleShell }) as any
    expect(opt.xAxis.max).toBe(160)
    expect(opt.yAxis.max).toBe(100)
    expect(opt.yAxis.inverse).toBe(true)
  })

  it('buildMapOption encodes one data item per zone', () => {
    const opt = buildMapOption({ shell: sampleShell }) as any
    expect(opt.series[0].data).toHaveLength(2)
    expect(opt.series[0].data[1].value).toEqual([60, 0, 60, 40])
  })

  it('floorIndex switches to the floor bounds and zone set', () => {
    const multi: FloorShell = {
      bounds: { w: 80, d: 60, h: 12 },
      zones: [{ id: 'el1', ref: 'EL-1', type: 'elevator_shaft', x: 70, z: 50, w: 5, d: 5 }],
      floors: [
        {
          id: 'L1', z: 0, bounds: { w: 80, d: 60 },
          zones: [{ id: 'f1', ref: 'STG-1', type: 'staging', x: 0, z: 0, w: 30, d: 20 }],
        },
      ],
    }
    const opt = buildMapOption({ shell: multi, floorIndex: 0 }) as any
    expect(opt.xAxis.max).toBe(80)
    expect(opt.series[0].data).toHaveLength(1)
    expect(opt.series[0].data[0].name).toBe('STG-1')
  })
})

describe('DeviceMap2D component', () => {
  beforeEach(() => {
    // Mock echarts.init so jsdom (no canvas) doesn't crash.
    vi.mock('echarts', () => ({
      init: vi.fn(() => ({
        setOption: vi.fn(),
        resize: vi.fn(),
        dispose: vi.fn(),
      })),
    }))
  })

  it('initializes a chart and renders when a shell is provided', async () => {
    const echarts = await import('echarts')
    const { mount } = await import('@vue/test-utils')
    const { default: DeviceMap2D } = await import('./DeviceMap2D.vue')
    const wrapper = mount(DeviceMap2D, { props: { shell: sampleShell } })
    // allow onMounted to run
    await new Promise((r) => setTimeout(r, 0))
    expect((echarts.init as unknown as ReturnType<typeof vi.fn>)).toHaveBeenCalled()
    expect(wrapper.find('[data-testid="map2d"]').exists()).toBe(true)
    wrapper.unmount()
  })

  it('shows placeholder when shell is null', async () => {
    const { mount } = await import('@vue/test-utils')
    const { default: DeviceMap2D } = await import('./DeviceMap2D.vue')
    const wrapper = mount(DeviceMap2D, { props: { shell: null } })
    expect(wrapper.find('.empty').exists()).toBe(true)
  })
})
