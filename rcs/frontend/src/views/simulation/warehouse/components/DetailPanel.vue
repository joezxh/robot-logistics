<template>
  <div id="wt-dp" :class="{ open: store.dpOpen }">
    <button id="wt-dp-x" @click="store.closeDetailPanel()">✕</button>
    <div class="wt-dp-title">{{ store.dpData?.ref || '' }}</div>
    <div class="wt-dp-sub">{{ t.type }}: {{ store.dpData?.kind || '' }}</div>

    <div class="wt-dp-sec">{{ t.location }}</div>
    <div class="wt-dp-lv" v-if="store.dpData?.slot">
      <div class="wt-dp-lv-name">{{ store.dpData?.slot }}</div>
    </div>

    <template v-if="store.dpData?.lv">
      <div class="wt-dp-sec">{{ t.level }}</div>
      <div class="wt-dp-lv">
        <div class="wt-dp-lv-name">{{ store.dpData?.lv }}</div>
        <div class="wt-dp-lv-pct" :style="{ color: fillColor }">
          {{ fillPct }}%
        </div>
      </div>
    </template>

    <template v-if="store.dpData?.kind === 'vehicle'">
      <div class="wt-dp-sec">{{ t.vehicle }}</div>
      <div class="wt-dp-lv">
        <div class="wt-dp-lv-name">{{ store.dpData?.ref }}</div>
        <div class="wt-dp-lv-pct">{{ store.dpData?.flow || 'internal' }}</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'

const store = useWarehouseStore()

const t = computed(() => ({
  type: store.lang === 'zh' ? '类型' : 'Type',
  location: store.lang === 'zh' ? '位置' : 'Location',
  level: store.lang === 'zh' ? '层级' : 'Level',
  vehicle: store.lang === 'zh' ? '车辆' : 'Vehicle',
}))

const fillPct = computed(() => {
  return store.dpData?.fillPct || 0
})

const fillColor = computed(() => {
  const p = fillPct.value
  if (p >= 90) return '#f87171'
  if (p >= 70) return '#fb923c'
  if (p >= 40) return '#facc15'
  return '#4ade80'
})
</script>

<style scoped>
#wt-dp {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 216px;
  background: var(--wt-bg2);
  border-left: 1px solid var(--wt-border);
  transform: translateX(100%);
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  z-index: 20;
  overflow-y: auto;
  padding: 12px;
}

#wt-dp.open {
  transform: translateX(0);
}

#wt-dp::-webkit-scrollbar {
  width: 3px;
}

#wt-dp::-webkit-scrollbar-thumb {
  background: var(--wt-border);
  border-radius: 10px;
}

#wt-dp-x {
  position: absolute;
  top: 8px;
  right: 8px;
  background: var(--wt-card);
  border: none;
  border-radius: 5px;
  color: var(--wt-text2);
  width: 22px;
  height: 22px;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  flex-shrink: 0;
}

#wt-dp-x:hover {
  background: var(--wt-cb);
}

.wt-dp-title {
  font-size: 13px;
  font-weight: 800;
  margin-bottom: 1px;
  padding-right: 26px;
  color: var(--wt-text);
}

.wt-dp-sub {
  font-size: 9px;
  color: var(--wt-text3);
  margin-bottom: 12px;
}

.wt-dp-sec {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--wt-text3);
  margin-bottom: 6px;
  margin-top: 10px;
  display: block;
}

.wt-dp-lv {
  background: var(--wt-card);
  border: 1px solid var(--wt-cb);
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 6px;
  cursor: pointer;
  transition: border-color 0.15s;
}

.wt-dp-lv:hover {
  border-color: var(--wt-accent);
}

.wt-dp-lv-hdr {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 5px;
}

.wt-dp-lv-name {
  font-size: 10px;
  font-weight: 700;
  color: var(--wt-text);
}

.wt-dp-lv-pct {
  font-size: 10px;
  font-weight: 800;
}
</style>
