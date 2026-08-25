<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { FloorShell, ScenarioId } from '@/types'
import { SCENARIO_CONFIG, relevantZonesFor } from './scenarioConfig'
import { zoneLabel, scenarioName } from '@/i18n'

const props = defineProps<{
  scenarioId: ScenarioId
  shell: FloorShell | null
}>()

const { locale } = useI18n()
const cfg = computed(() => SCENARIO_CONFIG[props.scenarioId])

const relevantZones = computed(() => {
  const types = (props.shell?.zones ?? []).map((z) => z.type)
  return relevantZonesFor(props.scenarioId, types)
})

const zoneBreakdown = computed(() => {
  const counts = new Map<string, number>()
  for (const z of props.shell?.zones ?? []) {
    if (cfg.value.relevantZones.includes(z.type as never)) {
      counts.set(z.type, (counts.get(z.type) ?? 0) + 1)
    }
  }
  return [...counts.entries()].map(([type, count]) => ({
    type,
    count,
    label: zoneLabel(type as never, (locale.value as 'zh-CN' | 'en-US')),
  }))
})

const title = computed(() => scenarioName(props.scenarioId, locale.value as 'zh-CN' | 'en-US'))
</script>

<template>
  <div class="scenario-panel" :style="{ '--theme': cfg.themeColor }">
    <header class="sp-head">
      <span class="dot"></span>
      <h3>{{ title }}</h3>
    </header>
    <div v-if="shell" class="sp-body">
      <div class="sp-stat">
        <span class="num">{{ relevantZones.length }}</span>
        <span class="lbl">{{ $t('map.zones') }}</span>
      </div>
      <ul class="sp-zones">
        <li v-for="zb in zoneBreakdown" :key="zb.type">
          <span class="ztype">{{ zb.label }}</span>
          <span class="zcount">×{{ zb.count }}</span>
        </li>
      </ul>
      <div class="sp-alerts">
        <span v-for="a in cfg.alertTypes" :key="a" class="alert-chip">{{ a }}</span>
      </div>
    </div>
    <div v-else class="sp-empty">{{ $t('map.noData') }}</div>
  </div>
</template>

<style scoped>
.scenario-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; }
.sp-head { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.dot { width: 10px; height: 10px; border-radius: 50%; background: var(--theme); }
.sp-head h3 { margin: 0; font-size: 15px; }
.sp-stat { display: flex; align-items: baseline; gap: 6px; margin-bottom: 8px; }
.num { font-size: 24px; font-weight: 700; color: var(--theme); }
.lbl { color: var(--fg-soft); font-size: 12px; }
.sp-zones { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 4px; }
.sp-zones li { display: flex; justify-content: space-between; font-size: 13px; }
.zcount { color: var(--fg-soft); }
.sp-alerts { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
.alert-chip { font-size: 11px; padding: 2px 8px; border-radius: 999px; background: var(--bg-card-alt); border: 1px solid var(--border); color: var(--warn); }
.sp-empty { color: var(--fg-soft); font-size: 13px; }
</style>
