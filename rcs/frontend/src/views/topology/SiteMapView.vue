<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useScenarioStore } from '@/stores/scenario'
import { useFloorShellStore } from '@/stores/floorShell'
import DeviceMap2D from '@/components/DeviceMap2D/DeviceMap2D.vue'
import DeviceMap3D from '@/components/DeviceMap3D/DeviceMap3D.vue'
import ScenarioPanel from '@/components/scenarios/ScenarioPanel.vue'
import OrderPanel from '@/components/orders/OrderPanel.vue'
import { templateDisplayName } from '@/api/warehouseTemplates'

const { t, locale } = useI18n()
const scenarioStore = useScenarioStore()
const floorStore = useFloorShellStore()
const { templates, selected, selectedTemplate, error } = storeToRefs(scenarioStore)
const { shell } = storeToRefs(floorStore)

const view = ref<'2d' | '3d'>('2d')
const floorIndex = ref<number | undefined>(undefined)

const floorCount = computed(() => shell.value?.floors?.length ?? 0)
const showFloorSelector = computed(() => floorCount.value > 0)

/**
 * Load a database template. The FloorShell is stored under the template's
 * `site_id` (identical to its `map_id`), so it comes from the shell endpoint
 * rather than from a hard-coded scenario bundle.
 */
async function selectTemplate(key: string) {
  scenarioStore.select(key)
  floorIndex.value = undefined
  const tpl = scenarioStore.templateByKey(key)
  if (tpl) await floorStore.loadBySite(tpl.site_id)
}

function onViewModeChange(e: { target: { value: '2d' | '3d' } }) {
  view.value = e.target.value
}

onMounted(async () => {
  await scenarioStore.loadTemplates()
  if (selected.value) await selectTemplate(selected.value)
})

watch(selected, (key) => {
  if (key) selectTemplate(key)
})

// Names come from the backend (zh + en), so no i18n key is needed per template.
const templateOptions = computed(() =>
  templates.value.map((tpl) => ({
    key: tpl.key,
    name: templateDisplayName(tpl, locale.value),
  })),
)
</script>

<template>
  <div class="sitemap">
    <header class="sm-top">
      <h2>{{ t('app.title') }}</h2>
      <div class="controls">
        <a-select
          :value="selected"
          style="width: 260px"
          :placeholder="t('scenario.select')"
          @change="selectTemplate($event as string)"
        >
          <a-select-option v-for="o in templateOptions" :key="o.key" :value="o.key">
            {{ o.name }}
          </a-select-option>
        </a-select>
        <a-radio-group :value="view" @change="onViewModeChange">
          <a-radio-button value="2d">{{ t('map.view2d') }}</a-radio-button>
          <a-radio-button value="3d">{{ t('map.view3d') }}</a-radio-button>
        </a-radio-group>
        <a-select
          v-if="showFloorSelector"
          v-model:value.number="floorIndex"
          style="width: 140px"
          :placeholder="t('map.floor')"
        >
          <a-select-option :value="undefined">—</a-select-option>
          <a-select-option v-for="(f, i) in shell?.floors" :key="f.id" :value="i">
            {{ f.id }}
          </a-select-option>
        </a-select>
      </div>
    </header>

    <p v-if="error" class="err">{{ t('app.error') }}: {{ error }}</p>

    <div class="sm-main">
      <section class="map">
        <DeviceMap2D v-if="view === '2d'" :shell="shell" :floor-index="floorIndex" />
        <DeviceMap3D v-else :shell="shell" :floor-index="floorIndex" />
      </section>
      <aside class="side">
        <ScenarioPanel
          v-if="selectedTemplate"
          :category="selectedTemplate.category"
          :title="templateDisplayName(selectedTemplate, locale)"
          :shell="shell"
        />
        <OrderPanel v-if="selected" :scenario-id="selected" />
      </aside>
    </div>
  </div>
</template>

<style scoped>
.sitemap { display: flex; flex-direction: column; height: 100%; padding: 12px; gap: 12px; box-sizing: border-box; }
.sm-top { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; }
.sm-top h2 { margin: 0; font-size: 18px; }
.controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.err { color: var(--err); font-size: 13px; margin: 0; }
.sm-main { flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 12px; min-height: 0; }
.map { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); min-height: 360px; }
.side { min-height: 0; overflow-y: auto; }
</style>
