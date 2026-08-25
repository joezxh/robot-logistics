<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { storeToRefs } from 'pinia'
import { useScenarioStore } from '@/stores/scenario'
import { useFloorShellStore } from '@/stores/floorShell'
import { useSiteGridStore } from '@/stores/siteGrid'
import DeviceMap2D from '@/components/DeviceMap2D/DeviceMap2D.vue'
import DeviceMap3D from '@/components/DeviceMap3D/DeviceMap3D.vue'
import ScenarioPanel from '@/components/scenarios/ScenarioPanel.vue'
import OrderPanel from '@/components/orders/OrderPanel.vue'
import { scenarioName } from '@/i18n'
import type { ScenarioId } from '@/types'

const { t, locale } = useI18n()
const scenarioStore = useScenarioStore()
const floorStore = useFloorShellStore()
const gridStore = useSiteGridStore()
const { templates, selected, error } = storeToRefs(scenarioStore)
const { shell } = storeToRefs(floorStore)

const view = ref<'2d' | '3d'>('2d')
const floorIndex = ref<number | undefined>(undefined)

const floorCount = computed(() => shell.value?.floors?.length ?? 0)
const showFloorSelector = computed(() => floorCount.value > 0)

async function selectScenario(id: ScenarioId) {
  scenarioStore.select(id)
  floorIndex.value = undefined
  await Promise.all([floorStore.loadByScenario(id), gridStore.loadByScenario(id)])
}

onMounted(async () => {
  await scenarioStore.loadTemplates()
  if (selected.value) await selectScenario(selected.value)
})

watch(selected, (id) => {
  if (id) selectScenario(id)
})

const scenarioOptions = computed(() =>
  templates.value.map((tpl) => ({
    id: tpl.scenario_id,
    name: scenarioName(tpl.scenario_id, locale.value as 'zh-CN' | 'en-US'),
  })),
)
</script>

<template>
  <div class="sitemap">
    <header class="sm-top">
      <h2>{{ t('app.title') }}</h2>
      <div class="controls">
        <label class="ctrl">
          <span>{{ t('scenario.label') }}</span>
          <select :value="selected" @change="selectScenario(($event.target as HTMLSelectElement).value as ScenarioId)">
            <option v-for="o in scenarioOptions" :key="o.id" :value="o.id">{{ o.name }}</option>
          </select>
        </label>
        <div class="toggle">
          <button :class="{ active: view === '2d' }" @click="view = '2d'">{{ t('map.view2d') }}</button>
          <button :class="{ active: view === '3d' }" @click="view = '3d'">{{ t('map.view3d') }}</button>
        </div>
        <label v-if="showFloorSelector" class="ctrl">
          <span>{{ t('map.floor') }}</span>
          <select v-model.number="floorIndex">
            <option :value="undefined">—</option>
            <option v-for="(f, i) in shell?.floors" :key="f.id" :value="i">{{ f.id }}</option>
          </select>
        </label>
      </div>
    </header>

    <p v-if="error" class="err">{{ t('app.error') }}: {{ error }}</p>

    <div class="sm-main">
      <section class="map">
        <DeviceMap2D v-if="view === '2d'" :shell="shell" :floor-index="floorIndex" />
        <DeviceMap3D v-else :shell="shell" :floor-index="floorIndex" />
      </section>
      <aside class="side">
        <ScenarioPanel v-if="selected" :scenario-id="selected" :shell="shell" />
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
.ctrl { display: flex; align-items: center; gap: 6px; font-size: 13px; color: var(--fg-soft); }
.ctrl select { background: var(--bg-card-alt); color: var(--fg); border: 1px solid var(--border); border-radius: 4px; padding: 4px 8px; }
.toggle { display: inline-flex; border: 1px solid var(--border); border-radius: 4px; overflow: hidden; }
.toggle button { background: var(--bg-card-alt); color: var(--fg); border: none; padding: 5px 12px; cursor: pointer; }
.toggle button.active { background: var(--accent); color: #0b1120; }
.err { color: var(--err); font-size: 13px; margin: 0; }
.sm-main { flex: 1; display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 12px; min-height: 0; }
.map { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); min-height: 360px; }
.side { min-height: 0; overflow-y: auto; }
</style>
