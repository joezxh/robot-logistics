<template>
  <div id="wt-sb">
    <div class="wt-sb-brand">
      {{ t.title }}
    </div>

    <span class="wt-sb-label">{{ t.groups }}</span>
    <div
      v-for="g in store.groups"
      :key="g.id"
      class="wt-g-item"
      :class="{ act: store.selGroup?.id === g.id }"
      @click="selectGroup(g)"
    >
      <span class="wt-g-name">{{ g.name }}</span>
      <span class="wt-g-meta">{{ g.slot_count }} {{ t.slots }}</span>
    </div>

    <div class="wt-sb-foot">
      <button class="wt-sb-btn" @click="openFloorPlan">
        {{ t.floor_plan }}
      </button>
      <button class="wt-sb-btn" @click="openAGV">
        {{ t.agv }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'
import type { WarehouseGroup } from '../types'

const store = useWarehouseStore()

const t = computed(() => ({
  title: store.lang === 'zh' ? '仓库导航' : 'Warehouse Navigator',
  groups: store.lang === 'zh' ? '仓库组' : 'Groups',
  slots: store.lang === 'zh' ? '库位' : 'Slots',
  floor_plan: store.lang === 'zh' ? '编辑布局' : 'Edit Layout',
  agv: store.lang === 'zh' ? 'AGV 路径' : 'AGV Paths',
}))

function selectGroup(g: WarehouseGroup) {
  store.setGroup(g)
}

function openFloorPlan() {
  store.fpOpen = true
}

function openAGV() {
  store.agvOpen = true
}
</script>

<style scoped>
#wt-sb {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 148px;
  background: var(--wt-sb);
  border-right: 1px solid var(--wt-border);
  overflow-y: auto;
  z-index: 15;
  display: flex;
  flex-direction: column;
  transition: background 0.3s, border-color 0.3s;
}

#wt-sb::-webkit-scrollbar {
  width: 3px;
}

#wt-sb::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.wt-sb-brand {
  padding: 10px 10px 7px;
  font-size: 12px;
  font-weight: 800;
  color: var(--wt-text);
  border-bottom: 1px solid var(--wt-border);
  flex-shrink: 0;
}

.wt-sb-label {
  padding: 9px 10px 2px;
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1.2px;
  color: var(--wt-text3);
  text-transform: uppercase;
  display: block;
}

.wt-g-item {
  padding: 7px 10px;
  cursor: pointer;
  border-left: 3px solid transparent;
  border-bottom: 1px solid var(--wt-border);
  transition: background 0.1s;
}

.wt-g-item:hover {
  background: var(--wt-card);
}

.wt-g-item.act {
  background: var(--wt-pill);
  border-left-color: var(--wt-accent);
}

.wt-g-name {
  font-size: 11px;
  font-weight: 700;
  color: var(--wt-text);
  display: block;
}

.wt-g-item.act .wt-g-name {
  color: var(--wt-accent2);
}

.wt-g-meta {
  font-size: 9px;
  color: var(--wt-text3);
}

.wt-sb-foot {
  margin-top: auto;
  padding: 8px 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.wt-sb-btn {
  width: 100%;
  height: 28px;
  border-radius: 6px;
  border: 1px solid rgba(59, 130, 246, 0.4);
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  line-height: 1;
}

.wt-sb-btn:hover {
  background: rgba(59, 130, 246, 0.2);
}
</style>
