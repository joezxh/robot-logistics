import { createI18n } from 'vue-i18n'
import { messages } from './messages'
import type { ScenarioId, ZoneType } from '@/types'

export const SUPPORTED_LOCALES = ['zh-CN', 'en-US'] as const
export type AppLocale = (typeof SUPPORTED_LOCALES)[number]

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages,
})

export function setLocale(locale: AppLocale): void {
  i18n.global.locale.value = locale
}

// Convenience helpers usable outside <script setup> (e.g. in tests / plain TS).
export function scenarioName(id: ScenarioId, locale: AppLocale = 'zh-CN'): string {
  return messages[locale].scenarios[id] ?? id
}

export function zoneLabel(type: ZoneType, locale: AppLocale = 'zh-CN'): string {
  return messages[locale].zone[type] ?? type
}
