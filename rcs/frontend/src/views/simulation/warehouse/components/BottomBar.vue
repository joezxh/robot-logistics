<template>
  <div id="wt-bot">
    <div id="wt-hint">
      {{ t.hint }}
    </div>
    <div id="wt-legend">
      <div class="wt-li">
        <span class="wt-lb" style="background: #4ade80"></span>
        <span>{{ t.free }}</span>
      </div>
      <div class="wt-li">
        <span class="wt-lb" style="background: #facc15"></span>
        <span>{{ t.medium }}</span>
      </div>
      <div class="wt-li">
        <span class="wt-lb" style="background: #fb923c"></span>
        <span>{{ t.high }}</span>
      </div>
      <div class="wt-li">
        <span class="wt-lb" style="background: #f87171"></span>
        <span>{{ t.full }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'

const store = useWarehouseStore()

const t = computed(() => ({
  hint: store.lang === 'zh' ? '拖拽旋转 · 滚轮缩放 · 右键平移' : 'Drag to rotate · Scroll to zoom · Right-click to pan',
  free: store.lang === 'zh' ? '空闲' : 'Free',
  medium: store.lang === 'zh' ? '中等' : 'Medium',
  high: store.lang === 'zh' ? '较高' : 'High',
  full: store.lang === 'zh' ? '满载' : 'Full',
}))
</script>

<style scoped>
#wt-bot {
  position: absolute;
  bottom: 0;
  left: 148px;
  right: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 9px 14px;
  background: linear-gradient(to top, rgba(12, 14, 20, 0.97) 55%, transparent);
  z-index: 10;
  pointer-events: none;
}

#wt-hint {
  font-size: 9px;
  color: rgba(255, 255, 255, 0.25);
  line-height: 1.8;
}

#wt-legend {
  display: flex;
  gap: 8px;
  align-items: center;
}

.wt-li {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 9px;
  color: rgba(255, 255, 255, 0.4);
}

.wt-lb {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}
</style>
