import { describe, it, expect } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { SCENARIO_CONFIG, relevantZonesFor } from './scenarioConfig'
import type { FloorShell, ScenarioId } from '@/types'

const shell: FloorShell = {
  bounds: { w: 160, d: 100 },
  zones: [
    { id: 'z1', ref: 'R1', type: 'flow_rack', x: 0, z: 0, w: 60, d: 40 },
    { id: 'z2', ref: 'R2', type: 'high_rack', x: 60, z: 0, w: 60, d: 40 },
    { id: 'z3', ref: 'PL', type: 'production_line', x: 0, z: 40, w: 80, d: 30 },
    { id: 'z4', ref: 'FZ', type: 'frozen_zone', x: 0, z: 70, w: 40, d: 20 },
  ],
}

describe('scenarioConfig', () => {
  it('ecommerce cares about flow/high rack, mezzanine, automated, temp, returns', () => {
    const cfg = SCENARIO_CONFIG.ecommerce
    expect(cfg.relevantZones).toEqual(
      expect.arrayContaining(['flow_rack', 'high_rack', 'mezzanine', 'automated', 'temp', 'temp_bagged', 'returns']),
    )
  })

  it('manufacturing cares about production_line, wip_buffer, parts_storage, staging', () => {
    expect(SCENARIO_CONFIG.manufacturing.relevantZones).toEqual(
      expect.arrayContaining(['production_line', 'wip_buffer', 'parts_storage', 'staging']),
    )
  })

  it('cold_chain cares about cold_zone, frozen_zone, ambient_zone, loading_bay', () => {
    expect(SCENARIO_CONFIG.cold_chain.relevantZones).toEqual(
      expect.arrayContaining(['cold_zone', 'frozen_zone', 'ambient_zone', 'loading_bay']),
    )
  })

  it('port / reverse_logistics / multi_floor have distinct relevant zones', () => {
    expect(SCENARIO_CONFIG.port.relevantZones).toEqual(expect.arrayContaining(['container_yard', 'customs_area']))
    expect(SCENARIO_CONFIG.reverse_logistics.relevantZones).toEqual(
      expect.arrayContaining(['returns_received', 'qc_staging', 'reshelving', 'disposal']),
    )
    expect(SCENARIO_CONFIG.multi_floor.relevantZones).toEqual(
      expect.arrayContaining(['floor_1', 'floor_2', 'floor_3', 'elevator_shaft']),
    )
  })

  it('relevantZonesFor filters a zone-type list for a scenario', () => {
    const types = ['flow_rack', 'production_line', 'frozen_zone']
    expect(relevantZonesFor('ecommerce', types)).toEqual(['flow_rack'])
    expect(relevantZonesFor('manufacturing', types)).toEqual(['production_line'])
    expect(relevantZonesFor('cold_chain', types)).toEqual(['frozen_zone'])
  })
})

describe('ScenarioPanel (Tasks 8 & 9)', () => {
  beforeEach(() => { setActivePinia(createPinia()) })

  const ids: ScenarioId[] = ['ecommerce', 'manufacturing', 'cold_chain', 'port', 'reverse_logistics', 'multi_floor']

  it('every scenario renders a panel without crashing', async () => {
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: ScenarioPanel } = await import('./ScenarioPanel.vue')
    for (const id of ids) {
      const wrapper = mount(ScenarioPanel, { props: { scenarioId: id, shell }, global: { plugins: [i18n] } })
      expect(wrapper.find('.scenario-panel').exists()).toBe(true)
      expect(wrapper.find('.sp-head h3').text()).toBeTruthy()
    }
  })

  it('ecommerce panel counts only relevant zones from the shell', async () => {
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: ScenarioPanel } = await import('./ScenarioPanel.vue')
    const wrapper = mount(ScenarioPanel, { props: { scenarioId: 'ecommerce', shell }, global: { plugins: [i18n] } })
    // shell has 1 flow_rack + 1 high_rack = 2 ecommerce-relevant zones
    expect(wrapper.find('.num').text()).toBe('2')
    expect(wrapper.findAll('.sp-zones li')).toHaveLength(2)
  })

  it('shows noData placeholder when shell is null', async () => {
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: ScenarioPanel } = await import('./ScenarioPanel.vue')
    const wrapper = mount(ScenarioPanel, { props: { scenarioId: 'port', shell: null }, global: { plugins: [i18n] } })
    expect(wrapper.find('.sp-empty').exists()).toBe(true)
  })
})
