<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getMap, cloneMap, type UnifiedMapDTO } from '@/api/map'
import ThreeMapViewer from './ThreeMapViewer.vue'

const { t } = useI18n()

const route = useRoute()
const router = useRouter()
const mapId = computed(() => String(route.params.id))
const map = ref<UnifiedMapDTO | null>(null)
const loading = ref(false)
const error = ref('')

const bounds = computed(() => {
  const g = map.value?.geometry as { bounds?: { w: number; d: number; h?: number } } | undefined
  return g?.bounds ?? null
})
const zoneCount = computed(() => {
  const g = map.value?.geometry as { zones?: any[]; docks?: any[] } | undefined
  return (g?.zones?.length ?? 0) + (g?.docks?.length ?? 0)
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    map.value = await getMap(mapId.value)
  } catch (e) {
    map.value = null
    error.value = (e as Error).message
  } finally {
    loading.value = false
  }
}

async function clone() {
  if (!map.value) return
  const m = await cloneMap(map.value.map_id, `${map.value.name} (副本)`)
  router.push(`/maps/${encodeURIComponent(m.map_id)}`)
}

onMounted(load)
defineExpose({ reload: load })
</script>

<template>
  <div class="map-detail">
    <header class="detail-head">
      <button class="btn btn-sm" @click="router.push('/maps')">← {{ t('maps.back') }}</button>
      <div class="detail-title">
        <h2>{{ map?.name ?? mapId }}</h2>
        <span class="muted">{{ map?.map_id }} · {{ map?.kind }}</span>
      </div>
      <button class="btn btn-sm" :disabled="!map" @click="clone">{{ t('maps.cloneEditable') }}</button>
      <button class="btn btn-sm" :disabled="!map" @click="router.push(`/maps/${mapId}/edit`)">{{ t('maps.editLayout') }}</button>
    </header>

    <div v-if="loading" class="muted detail-msg">{{ t('maps.loading') }}</div>
    <div v-else-if="error" class="detail-msg err">{{ t('common.failed') }}：{{ error }}</div>
    <div v-else-if="map" class="detail-body">
      <div class="viewer">
        <ThreeMapViewer :map-id="map.map_id" />
      </div>
      <aside class="meta">
        <section v-if="bounds">
          <h4>{{ t('maps.bounds') }} (m)</h4>
          <p class="muted">W={{ bounds.w }} · D={{ bounds.d }}<template v-if="bounds.h"> · H={{ bounds.h }}</template></p>
        </section>
        <section>
          <h4>{{ t('maps.view3d') }}</h4>
          <p class="muted">{{ zoneCount }} ({{ t('maps.zones') }} + {{ t('maps.docks') }})</p>
        </section>
        <section v-if="map.semantic">
          <h4>语义</h4>
          <p class="muted">{{ map.semantic.scenario ?? '—' }}</p>
        </section>
        <section v-if="map.name_en">
          <h4>英文</h4>
          <p class="muted">{{ map.name_en }}</p>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.map-detail {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.detail-head {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--divider);
}
.detail-title {
  flex: 1;
  min-width: 0;
}
.detail-title h2 {
  margin: 0;
  font-size: 17px;
  color: var(--fg);
}
.detail-msg {
  padding: 24px;
}
.err {
  color: var(--danger, #ef4444);
}
.detail-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 280px;
  min-height: 0;
}
.viewer {
  min-height: 0;
  position: relative;
}
.meta {
  border-left: 1px solid var(--divider);
  padding: 16px;
  overflow: auto;
}
.meta h4 {
  margin: 0 0 4px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--fg-secondary);
}
.meta section {
  margin-bottom: 18px;
}
.muted {
  color: var(--fg-muted);
  font-size: 13px;
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
.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}
</style>
