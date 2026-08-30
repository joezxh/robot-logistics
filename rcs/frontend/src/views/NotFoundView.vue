<script setup lang="ts">
// Fallback page for unknown routes and paths the user is not allowed to open.
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
</script>

<template>
  <div class="notfound">
    <div class="code">404</div>
    <p class="desc">{{ t('common.noData') }}</p>
    <a-button type="primary" @click="router.push('/')">{{ t('sys.dashboard.title') }}</a-button>
  </div>
</template>

<style scoped>
.notfound {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: var(--bg-page);
}

.code {
  font-size: 72px;
  font-weight: 800;
  letter-spacing: 4px;
  background: linear-gradient(135deg, var(--accent), var(--accent-2));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.desc {
  color: var(--fg-secondary);
  margin: 0;
}
</style>
