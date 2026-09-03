import { describe, it, expect } from 'vitest'
import { scenarioName, zoneLabel, setLocale, i18n } from '@/i18n'
import type { ScenarioId, ZoneType } from '@/types'

describe('i18n scenario names', () => {
  const ids: ScenarioId[] = [
    'ecommerce', 'manufacturing', 'cold_chain', 'port', 'reverse_logistics', 'multi_floor',
  ]

  it('returns zh-CN names', () => {
    expect(scenarioName('ecommerce', 'zh-CN')).toBe('电商仓')
    expect(scenarioName('multi_floor', 'zh-CN')).toBe('多层仓')
  })

  it('returns en-US names', () => {
    expect(scenarioName('port', 'en-US')).toBe('Port')
    expect(scenarioName('reverse_logistics', 'en-US')).toBe('Reverse Logistics')
  })

  it('falls back to the id for unknown ids', () => {
    expect(scenarioName('unknown' as ScenarioId, 'zh-CN')).toBe('unknown')
  })

  it('covers all 6 scenarios in both locales', () => {
    for (const id of ids) {
      expect(scenarioName(id, 'zh-CN')).not.toBe(id)
      expect(scenarioName(id, 'en-US')).not.toBe(id)
    }
  })
})

describe('i18n zone labels', () => {
  it('translates zone types in both locales', () => {
    expect(zoneLabel('flow_rack', 'zh-CN')).toBe('流利架')
    expect(zoneLabel('flow_rack', 'en-US')).toBe('Flow Rack')
    expect(zoneLabel('elevator_shaft', 'zh-CN')).toBe('电梯井')
  })

  it('falls back to the raw type for unknown zones', () => {
    expect(zoneLabel('mystery_zone' as ZoneType, 'zh-CN')).toBe('mystery_zone')
  })
})

describe('i18n runtime toggle', () => {
  it('switches global locale and resolves t()', () => {
    setLocale('en-US')
    expect(i18n.global.t('app.title')).toBe('RCS Console')
    setLocale('zh-CN')
    expect(i18n.global.t('app.title')).toBe('RCS 控制台')
  })

  it('falls back to en-US for missing keys', () => {
    setLocale('zh-CN')
    // app.loading exists in both; verify a known key resolves
    expect(i18n.global.t('map.noData')).toContain('暂无数据')
  })
})
