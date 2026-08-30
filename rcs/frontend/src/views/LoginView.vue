<script setup lang="ts">
// Sign-in page.
//
// Deliberately outside the console shell: it owns the full viewport, shows the
// animated grid backdrop, and redirects to the requested route (or the first
// permitted page) once the session is established.
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LockOutlined, UserOutlined } from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { useAppStore } from '@/stores/app'
import { LOCALE_LABELS, SUPPORTED_LOCALES } from '@/i18n'
import { useI18n } from 'vue-i18n'
import { registerDynamicRoutes } from '@/router'
import type { AppLocale } from '@/types'

const { t } = useI18n()
const auth = useAuthStore()
const app = useAppStore()
const route = useRoute()
const router = useRouter()

const form = reactive({ username: '', password: '' })
const submitting = computed(() => auth.loading)
const errorMessage = ref('')

onMounted(() => {
  // Arriving here with a live session means the user signed out elsewhere.
  if (auth.isAuthenticated) auth.reset()
})

async function onSubmit() {
  errorMessage.value = ''
  try {
    await auth.login(form.username.trim(), form.password)
    registerDynamicRoutes()
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : null
    await router.replace(redirect ?? '/')
  } catch (err) {
    errorMessage.value = err instanceof Error ? err.message : String(err)
  }
}

function onLocale({ key }: { key: string }) {
  app.setAppLocale(key as AppLocale)
}
</script>

<template>
  <div class="login-page">
    <div class="grid-backdrop" aria-hidden="true" />
    <div class="glow glow-a" aria-hidden="true" />
    <div class="glow glow-b" aria-hidden="true" />

    <div class="lang-switch">
      <a-dropdown>
        <button class="lang-btn" type="button">
          <span class="globe">🌐</span>
          {{ LOCALE_LABELS[app.locale] }}
        </button>
        <template #overlay>
          <a-menu :selected-keys="[app.locale]" @click="onLocale">
            <a-menu-item v-for="loc in SUPPORTED_LOCALES" :key="loc">{{ LOCALE_LABELS[loc] }}</a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>

    <div class="panel">
      <div class="brand-row">
        <span class="brand-mark">R</span>
        <div>
          <h1 class="title">{{ t('sys.login.title') }}</h1>
          <p class="subtitle">{{ t('sys.login.subtitle') }}</p>
        </div>
      </div>

      <a-form layout="vertical" @submit.prevent="onSubmit">
        <a-form-item>
          <a-input
            v-model:value="form.username"
            size="large"
            :placeholder="t('sys.login.username')"
            autocomplete="username"
          >
            <template #prefix><UserOutlined /></template>
          </a-input>
        </a-form-item>

        <a-form-item>
          <a-input-password
            v-model:value="form.password"
            size="large"
            :placeholder="t('sys.login.password')"
            autocomplete="current-password"
            @press-enter="onSubmit"
          >
            <template #prefix><LockOutlined /></template>
          </a-input-password>
        </a-form-item>

        <a-alert v-if="errorMessage" class="alert" type="error" show-icon :message="errorMessage" />

        <a-button
          type="primary"
          size="large"
          block
          html-type="submit"
          :loading="submitting"
          @click="onSubmit"
        >
          {{ submitting ? t('sys.login.submitting') : t('sys.login.submit') }}
        </a-button>
      </a-form>

      <p class="hint">{{ t('sys.login.demoHint') }}</p>
    </div>

    <footer class="footer">RCS · Robot Control System</footer>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100%;
  display: grid;
  place-items: center;
  padding: 24px;
  background: var(--bg-base);
  overflow: hidden;
}

.grid-backdrop {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 44px 44px, 44px 44px;
  mask-image: radial-gradient(ellipse at center, #000 30%, transparent 78%);
  -webkit-mask-image: radial-gradient(ellipse at center, #000 30%, transparent 78%);
}

.glow {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  filter: blur(90px);
  opacity: 0.35;
  pointer-events: none;
}

.glow-a {
  background: var(--accent);
  top: -180px;
  left: -140px;
}

.glow-b {
  background: var(--accent-2);
  bottom: -220px;
  right: -160px;
}

.lang-switch {
  position: absolute;
  top: 20px;
  right: 24px;
  z-index: 2;
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: var(--bg-surface);
  color: var(--fg-secondary);
  cursor: pointer;
  font-size: 13px;
}

.lang-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
}

.panel {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  padding: 32px;
  border-radius: 16px;
  background: color-mix(in srgb, var(--bg-surface) 82%, transparent);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(12px);
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 26px;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 20px;
  color: var(--fg-inverse);
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  box-shadow: var(--glow);
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 680;
  color: var(--fg);
}

.subtitle {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--fg-secondary);
}

.alert {
  margin-bottom: 14px;
}

.hint {
  margin: 18px 0 0;
  text-align: center;
  font-size: 12px;
  color: var(--fg-muted);
}

.footer {
  position: absolute;
  bottom: 20px;
  font-size: 12px;
  letter-spacing: 1px;
  color: var(--fg-muted);
}
</style>
