// Message catalogue assembly.
//
// The console ships four locales (简体中文 / 繁體中文 / English / 日本語).
// Each locale file is a complete, flat catalogue so that a missing key in one
// language never silently falls back at runtime — only genuinely absent keys
// fall back to `en-US` (configured as `fallbackLocale`).
import zhCN from './locales/zh-CN'
import zhTW from './locales/zh-TW'
import enUS from './locales/en-US'
import jaJP from './locales/ja-JP'

export { zhCN, zhTW, enUS, jaJP }

export const messages = {
  'zh-CN': zhCN,
  'zh-TW': zhTW,
  'en-US': enUS,
  'ja-JP': jaJP,
}

export default messages
