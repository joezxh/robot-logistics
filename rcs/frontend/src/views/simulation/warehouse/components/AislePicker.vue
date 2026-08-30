<template>
  <div id="wt-aisle-picker" @click.self="store.aislePickerOpen = false">
    <div id="wt-aisle-picker-box">
      <div class="wt-aisle-picker-title">{{ t.title }}</div>
      <div class="wt-aisle-picker-sub">{{ t.subtitle }}</div>
      <button
        v-for="(gap, i) in store.aisleGaps"
        :key="i"
        class="wt-aisle-gap-btn"
        @click="enterAisle(i)"
      >
        <span class="wt-aisle-gap-icon">🚶</span>
        {{ gap.label }}
      </button>
      <button class="wt-aisle-cancel" @click="store.aislePickerOpen = false">
        {{ t.cancel }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'

const store = useWarehouseStore()

const t = computed(() => ({
  title: store.lang === 'zh' ? '选择巷道' : 'Choose an Aisle',
  subtitle: store.lang === 'zh' ? '选择要进入的巷道' : 'Select which aisle to walk through',
  cancel: store.lang === 'zh' ? '取消' : 'Cancel',
}))

function enterAisle(index: number) {
  const gap = store.aisleGaps[index]
  if (gap) {
    store.aislePickerOpen = false
  }
}
</script>

<style scoped>
#wt-aisle-picker {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  z-index: 80;
  display: flex;
  align-items: center;
  justify-content: center;
}

#wt-aisle-picker-box {
  background: #13151e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 20px;
  min-width: 280px;
  max-width: 360px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.6);
  animation: wtCfgIn 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes wtCfgIn {
  from {
    opacity: 0;
    transform: scale(0.93);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.wt-aisle-picker-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  margin-bottom: 4px;
}

.wt-aisle-picker-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.35);
  margin-bottom: 14px;
}

.wt-aisle-gap-btn {
  width: 100%;
  height: 40px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0 14px;
  gap: 10px;
  margin-bottom: 6px;
  transition: all 0.15s;
}

.wt-aisle-gap-btn:hover {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #93c5fd;
}

.wt-aisle-gap-icon {
  font-size: 16px;
}

.wt-aisle-cancel {
  width: 100%;
  height: 32px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: transparent;
  color: rgba(255, 255, 255, 0.4);
  font-size: 11px;
  cursor: pointer;
  margin-top: 6px;
}

.wt-aisle-cancel:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(255, 255, 255, 0.7);
}
</style>
