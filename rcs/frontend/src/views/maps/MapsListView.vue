<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  listTemplates,
  seedTemplates,
  cloneMap,
  templateDisplayName,
  type MapTemplateInfo,
} from '@/api/map'

const { t } = useI18n()

const router = useRouter()
const templates = ref<MapTemplateInfo[]>([])
const loading = ref(false)
const seeding = ref(false)
const locale = ref((navigator.language || 'zh').slice(0, 2))

async function load() {
  loading.value = true
  try {
    templates.value = await listTemplates()
  } finally {
    loading.value = false
  }
}

async function seed() {
  seeding.value = true
  try {
    await seedTemplates()
    await load()
  } finally {
    seeding.value = false
  }
}

async function clone(tpl: MapTemplateInfo) {
  const m = await cloneMap(tpl.map_id, `${tpl.name || tpl.map_id} (副本)`)
  router.push(`/maps/${encodeURIComponent(m.map_id)}`)
}

function open(tpl: MapTemplateInfo) {
  router.push(`/maps/${encodeURIComponent(tpl.map_id)}`)
}

onMounted(load)
defineExpose({ reload: load })
</script>

<template>
  <div class="maps-page">
    <header class="maps-head">
      <div>
        <h2>{{ t('maps.list') }}</h2>
        <p class="muted">
          统一地图表（robot_unified_maps）中的场景 / 仓储模板，可 3D 预览并从模板克隆为可编辑地图。
        </p>
      </div>
      <div class="maps-actions">
        <button class="btn" :disabled="seeding" @click="seed">
          {{ seeding ? t('maps.loading') : t('maps.resync') }}
        </button>
        <button class="btn btn-primary" :disabled="loading" @click="load">{{ t('maps.refresh') }}</button>
      </div>
    </header>

    <div v-if="loading" class="muted">{{ t('maps.loading') }}</div>
    <div v-else-if="!templates.length" class="muted">{{ t('maps.empty') }}</div>
    <div v-else class="cards">
      <article
        v-for="tpl in templates"
        :key="tpl.map_id"
        class="card"
        @click="open(tpl)"
      >
        <div class="card-badge" :class="{ 'card-badge--tpl': tpl.is_template }">
          {{ tpl.is_template ? t('maps.template') : t('maps.map') }}
        </div>
        <div class="card-title">{{ templateDisplayName(tpl, locale) }}</div>
        <div class="card-sub muted">{{ tpl.map_id }} · {{ tpl.kind }}</div>
        <div class="card-actions">
          <button class="btn btn-sm" @click.stop="open(tpl)">{{ t('maps.preview') }}</button>
          <button class="btn btn-sm" @click.stop="clone(tpl)">{{ t('maps.clone') }}</button>
        </div>
      </article>
    </div>
  </div>
</template>

<style scoped>
.maps-page {
  padding: 20px 24px;
  height: 100%;
  overflow: auto;
}
.maps-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}
.maps-head h2 {
  margin: 0 0 4px;
  font-size: 18px;
  color: var(--fg);
}
.maps-actions {
  display: flex;
  gap: 8px;
  flex: 0 0 auto;
}
.muted {
  color: var(--fg-muted);
  font-size: 13px;
}
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 14px;
}
.card {
  position: relative;
  padding: 14px 14px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-surface);
  cursor: pointer;
  transition: border-color var(--transition), transform var(--transition);
}
.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}
.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--fg);
  margin-bottom: 4px;
}
.card-sub {
  font-family: var(--font-mono);
  font-size: 12px;
}
.card-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 11px;
  padding: 1px 8px;
  border-radius: 999px;
  background: var(--bg-input);
  color: var(--fg-muted);
}
.card-badge--tpl {
  background: var(--accent-soft, #1e293b);
  color: var(--accent);
}
.card-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
.btn {
  appearance: none;
  border: 1px solid var(--border);
  background: var(--bg-input);
  color: var(--fg-secondary);
  padding: 7px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  transition: color var(--transition), border-color var(--transition);
}
.btn:hover {
  color: var(--accent);
  border-color: var(--border-strong);
}
.btn:disabled {
  opacity: 0.6;
  cursor: default;
}
.btn-primary {
  background: var(--accent);
  border-color: var(--accent);
  color: var(--fg-inverse);
}
.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}
</style>
