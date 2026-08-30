// vue-i18n bootstrap for the RCS console.
//
// Four locales are supported: zh-CN (简体), zh-TW (繁體), en-US, ja-JP.
// The active locale and skin are persisted to localStorage by the app store;
// this module only owns the i18n instance and a few lookup helpers.
import { createI18n } from 'vue-i18n'
import { enUS, jaJP, messages, zhCN, zhTW } from './messages'
import type { AppLocale } from '@/types/sys'
import type { ScenarioId, ZoneType } from '@/types'

export const SUPPORTED_LOCALES = ['zh-CN', 'zh-TW', 'en-US', 'ja-JP'] as const
export type { AppLocale }

/** Human labels for the language switcher. */
export const LOCALE_LABELS: Record<AppLocale, string> = {
  'zh-CN': '简体中文',
  'zh-TW': '繁體中文',
  'en-US': 'English',
  'ja-JP': '日本語',
}

/** Short labels for compact switchers (e.g. a dropdown with limited width). */
export const LOCALE_SHORT: Record<AppLocale, string> = {
  'zh-CN': '简',
  'zh-TW': '繁',
  'en-US': 'EN',
  'ja-JP': '日',
}

const STORAGE_KEY = 'rcs.console.locale'
const DEFAULT_LOCALE: AppLocale = 'zh-CN'

export function isSupportedLocale(value: unknown): value is AppLocale {
  return typeof value === 'string' && (SUPPORTED_LOCALES as readonly string[]).includes(value)
}

/**
 * Read the persisted locale, then the browser hint, then fall back to zh-CN.
 *
 * Only locales that cannot be inferred from a later user choice are
 * auto-detected: a Traditional-Chinese or Japanese browser gets the matching
 * catalogue. Everything else keeps the project default (zh-CN) — the console
 * has an explicit language switcher and the choice persists, so silently
 * switching a first-time visitor to English would be more surprising than
 * helpful.
 */
export function detectLocale(): AppLocale {
  let stored: string | null = null
  try {
    stored = globalThis.localStorage?.getItem(STORAGE_KEY) ?? null
  } catch {
    /* storage unavailable */
  }
  if (isSupportedLocale(stored)) return stored

  const nav = globalThis.navigator?.language ?? ''
  // zh-Hant / zh-TW / zh-HK / zh-MO -> Traditional; other zh-* -> Simplified.
  if (nav.startsWith('zh')) return /hant|tw|hk|mo/i.test(nav) ? 'zh-TW' : 'zh-CN'
  if (nav.startsWith('ja')) return 'ja-JP'
  return DEFAULT_LOCALE
}

export const i18n = createI18n({
  legacy: false,
  locale: detectLocale(),
  fallbackLocale: 'en-US',
  messages,
})

/** Switch the active locale and persist the choice. */
export function setLocale(locale: AppLocale): void {
  i18n.global.locale.value = locale
  try {
    globalThis.localStorage?.setItem(STORAGE_KEY, locale)
  } catch {
    /* storage unavailable */
  }
  if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('lang', locale)
  }
}

export function currentLocale(): AppLocale {
  const value = i18n.global.locale.value
  return isSupportedLocale(value) ? value : DEFAULT_LOCALE
}

/**
 * Resolve a DB-backed menu title for the active locale.
 *
 * Menus store `{"zh-CN": ..., "en-US": ...}` in `sys_menu.i18n`; `name` is the
 * fallback rendered when the locale key is missing.
 */
export function localise(i18nMap: Partial<Record<AppLocale, string>> | undefined, fallback: string): string {
  if (!i18nMap) return fallback
  return i18nMap[currentLocale()] ?? i18nMap['en-US'] ?? fallback
}

// Convenience helpers usable outside <script setup> (e.g. in tests / plain TS).
export function scenarioName(id: ScenarioId, locale: AppLocale = 'zh-CN'): string {
  const catalogue = { 'zh-CN': zhCN, 'zh-TW': zhTW, 'en-US': enUS, 'ja-JP': jaJP }[locale]
  return catalogue.scenarios[id] ?? id
}

export function zoneLabel(type: ZoneType, locale: AppLocale = 'zh-CN'): string {
  const catalogue = { 'zh-CN': zhCN, 'zh-TW': zhTW, 'en-US': enUS, 'ja-JP': jaJP }[locale]
  return catalogue.zone[type] ?? type
}

export default i18n
