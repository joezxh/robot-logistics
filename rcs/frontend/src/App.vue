<script setup lang="ts">
// Application root.
//
// Responsibilities:
//   * provide the Ant Design theme (algorithm + component tokens) that follows
//     the dark/light skin from the app store
//   * provide the matching Ant Design *locale* so built-in component strings
//     (pagination, empty state, date picker) follow the active language
//   * keep <html data-theme> in sync so the CSS variables switch
import { computed, watchEffect } from 'vue'
import { theme as antdTheme } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import zhTW from 'ant-design-vue/es/locale/zh_TW'
import enUS from 'ant-design-vue/es/locale/en_US'
import jaJP from 'ant-design-vue/es/locale/ja_JP'
import { useAppStore } from '@/stores/app'
import type { AppLocale } from '@/types'

const app = useAppStore()

/** Ant Design locale packs, keyed by our own locale codes. */
const ANTD_LOCALES: Record<AppLocale, unknown> = {
  'zh-CN': zhCN,
  'zh-TW': zhTW,
  'en-US': enUS,
  'ja-JP': jaJP,
}

const antdLocale = computed(() => ANTD_LOCALES[app.locale] ?? enUS)

/**
 * Component token overrides. Colours come from the CSS variables so a skin
 * switch is a single attribute change; only the structural tokens are set here.
 */
const componentTokens = computed(() => ({
  borderRadius: 8,
  fontSize: 14,
  controlHeight: 32,
  // Let surfaces pick up our palette instead of AntD's fixed whites/greys.
  colorBgContainer: 'var(--bg-surface)',
  colorBgElevated: 'var(--bg-elevated)',
  colorBorder: 'var(--border)',
  colorBorderSecondary: 'var(--border)',
  colorPrimary: 'var(--accent)',
  colorText: 'var(--fg)',
  colorTextSecondary: 'var(--fg-secondary)',
}))

const algorithm = computed(() =>
  app.isDark ? [antdTheme.darkAlgorithm, antdTheme.compactAlgorithm] : [antdTheme.defaultAlgorithm],
)

// Mirror the skin onto <html> so `tokens.css` selects the right palette.
watchEffect(() => {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', app.theme)
  document.documentElement.style.colorScheme = app.theme
})
</script>

<template>
  <a-config-provider
    :locale="antdLocale"
    :theme="{ algorithm, token: componentTokens, cssVar: true, hashed: false }"
  >
    <a-app class="app-root">
      <router-view />
    </a-app>
  </a-config-provider>
</template>

<style>
.app-root {
  height: 100%;
}
</style>
