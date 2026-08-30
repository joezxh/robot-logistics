<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useWarehouseStore } from '@/stores/warehouse'
import DeviceMap3D from '@/components/DeviceMap3D/DeviceMap3D.vue'

const { t } = useI18n()
const store = useWarehouseStore()
const { shell, importResult, loading, importing, error } = storeToRefs(store)

const view = ref<'3d' | 'info'>('3d')

const hasData = computed(() => !!shell.value)
const zoneList = computed(() => shell.value?.zones ?? [])
const facilityList = computed(() => shell.value?.facilities ?? [])
const dockList = computed(() => shell.value?.docks ?? [])

const ZONE_LABELS: Record<string, string> = {
  flow_rack: '流利条区', high_rack: '高位货架区', mezzanine: '夹层拆零区',
  automated: '自动化立库', temp: '临时存储区', temp_bagged: '袋装暂存区',
  returns: '退货处理区',
}

const FACILITY_LABELS: Record<string, string> = {
  charger: '充电桩', sorting: '分拣台', packing: '打包区',
  qc: '质检区', entrance: '大门',
}

onMounted(async () => {
  await store.loadWarehouse()
})

async function handleImport() {
  await store.doImport()
}

function onViewChange(e: { target: { value: '3d' | 'info' } }) {
  view.value = e.target.value
}

async function handlePreview() {
  await store.loadPreview()
}
</script>

<template>
  <div class="warehouse-view">
    <header class="wh-top">
      <h2>{{ t('warehouse.title') }}</h2>
      <div class="controls">
        <a-radio-group :value="view" @change="onViewChange">
          <a-radio-button value="3d">{{ t('map.view3d') }}</a-radio-button>
          <a-radio-button value="info">{{ t('warehouse.info') }}</a-radio-button>
        </a-radio-group>
        <a-button :loading="loading" @click="handlePreview">
          {{ loading ? t('app.loading') : t('warehouse.preview') }}
        </a-button>
        <a-button type="primary" :loading="importing" @click="handleImport">
          {{ importing ? t('warehouse.importing') : t('warehouse.import') }}
        </a-button>
      </div>
    </header>

    <p v-if="error" class="err">{{ t('app.error') }}: {{ error }}</p>

    <!-- Import result summary -->
    <div v-if="importResult" class="import-summary">
      <span class="badge ok">{{ t('warehouse.importOk') }}</span>
      <span>{{ t('warehouse.zones') }}: {{ importResult.zone_count }}</span>
      <span>{{ t('warehouse.nodes') }}: {{ importResult.node_count }}</span>
      <span>{{ t('warehouse.edges') }}: {{ importResult.edge_count }}</span>
    </div>

    <div class="wh-main">
      <!-- 3D Visualization -->
      <section v-show="view === '3d'" class="map">
        <div v-if="!hasData && !loading" class="empty">
          <p>{{ t('warehouse.noData') }}</p>
          <a-button type="primary" :loading="importing" @click="handleImport">{{ t('warehouse.import') }}</a-button>
        </div>
        <div v-else-if="loading" class="empty">{{ t('app.loading') }}</div>
        <DeviceMap3D v-else :shell="shell" />
      </section>

      <!-- Info Panel -->
      <aside v-if="view === 'info'" class="side">
        <div v-if="hasData" class="info-panel">
          <!-- Bounds -->
          <div class="info-section">
            <h3>{{ t('warehouse.layout') }}</h3>
            <div class="info-row">
              <span>{{ t('warehouse.bounds') }}</span>
              <strong>{{ shell!.bounds.w }}m × {{ shell!.bounds.d }}m</strong>
            </div>
            <div class="info-row">
              <span>{{ t('warehouse.walls') }}</span>
              <strong>{{ shell!.walls?.length ?? 0 }}</strong>
            </div>
          </div>

          <!-- Zones -->
          <div class="info-section">
            <h3>{{ t('warehouse.zones') }} ({{ zoneList.length }})</h3>
            <div v-for="z in zoneList" :key="z.id" class="info-row zone-row">
              <span class="zone-badge" :style="{ background: getZoneColor(z.type) }">
                {{ z.ref }}
              </span>
              <span class="zone-label">{{ ZONE_LABELS[z.type] || z.type }}</span>
              <span class="zone-size">{{ z.w }}×{{ z.d }}m</span>
            </div>
          </div>

          <!-- Facilities -->
          <div class="info-section">
            <h3>{{ t('warehouse.facilities') }} ({{ facilityList.length }})</h3>
            <div v-for="f in facilityList" :key="f.id" class="info-row">
              <span class="fac-badge">{{ f.ref }}</span>
              <span>{{ FACILITY_LABELS[f.type] || f.type }}</span>
            </div>
          </div>

          <!-- Docks -->
          <div class="info-section">
            <h3>{{ t('warehouse.docks') }} ({{ dockList.length }})</h3>
            <div v-for="d in dockList" :key="d.id" class="info-row">
              <span class="dock-badge">{{ d.ref }}</span>
              <span>{{ d.direction }} · ({{ d.x.toFixed(1) }}, {{ d.z.toFixed(1) }})</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script lang="ts">
const ZONE_COLORS: Record<string, string> = {
  flow_rack: '#38bdf8', high_rack: '#0ea5e9', mezzanine: '#22d3ee',
  automated: '#6366f1', temp: '#f59e0b', temp_bagged: '#f97316',
  returns: '#ef4444',
}
function getZoneColor(type: string): string {
  return ZONE_COLORS[type] ?? '#94a3b8'
}
export default { methods: { getZoneColor } }
</script>

<style scoped>
.warehouse-view { display: flex; flex-direction: column; height: 100%; padding: 12px; gap: 12px; box-sizing: border-box; }
.wh-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.wh-top h2 { margin: 0; font-size: 18px; }
.controls { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.err { color: var(--err); font-size: 13px; margin: 0; }
.import-summary { display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--fg-soft); padding: 6px 12px; background: var(--bg-card-alt); border-radius: var(--radius); border: 1px solid var(--border); }
.badge.ok { background: #16a34a; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.wh-main { flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 12px; min-height: 0; }
.wh-main:has(.side:empty) { grid-template-columns: 1fr; }
.map { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); min-height: 360px; }
.empty { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 16px; color: var(--fg-soft); }
.side { min-height: 0; overflow-y: auto; }
.info-panel { display: flex; flex-direction: column; gap: 12px; }
.info-section { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 10px 12px; }
.info-section h3 { margin: 0 0 8px; font-size: 14px; color: var(--fg); }
.info-row { display: flex; align-items: center; gap: 8px; font-size: 13px; padding: 3px 0; color: var(--fg-soft); }
.zone-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; color: #fff; font-size: 11px; font-weight: 600; min-width: 56px; text-align: center; }
.zone-label { flex: 1; }
.zone-size { color: var(--fg-soft); font-size: 12px; }
.fac-badge, .dock-badge { display: inline-block; padding: 1px 6px; border-radius: 3px; background: #475569; color: #fff; font-size: 11px; font-weight: 600; min-width: 48px; text-align: center; }
</style>
