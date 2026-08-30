<template>
  <div id="wt-fp-ov" class="wt-modal-overlay" @click.self="close">
    <div id="wt-fp-modal" class="wt-modal wt-modal-lg">
      <div class="wt-modal-hdr">
        <div>
          <div class="wt-modal-title">{{ t.title }}</div>
          <div class="wt-modal-sub">{{ t.subtitle }}</div>
        </div>
        <button class="wt-x-btn" @click="close">✕</button>
      </div>
      <div class="wt-modal-body">
        <div class="wt-fp-layers">
          <button
            v-for="ly in layers"
            :key="ly.key"
            class="wt-layer-btn"
            :class="{ act: store.fpLayer === ly.key }"
            @click="store.fpLayer = ly.key"
          >
            {{ ly.label }}
          </button>
        </div>
        <div class="wt-fp-preview" v-if="store.fpLayer === 'paint'">
          <div class="wt-fp-preview-lbl">{{ t.preview }}</div>
          <div class="wt-fp-preview-grid">
            <div v-if="!store.fpRows.length" class="wt-fp-empty">{{ t.no_rows }}</div>
            <div v-else v-for="(row, ri) in store.fpRows" :key="ri" class="wt-fp-prev-row">
              <div
                v-for="(cell, ci) in row.cells"
                :key="ci"
                :class="['wt-fp-prev-cell', cell.aisle ? 'aisle' : cell.wh ? 'filled' : 'empty']"
                :style="{ flex: cell.span }"
              >
                {{ cell.aisle ? '▥' : cell.wh ? shortName(cell.wh) : '·' }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="wt-modal-footer">
        <div class="wt-footer-left">{{ t.hint }}</div>
        <div class="wt-footer-right">
          <button class="wt-btn-cancel" @click="close">{{ t.cancel }}</button>
          <button class="wt-btn-save" :disabled="store.fpSaving" @click="save">{{ t.save }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'

const store = useWarehouseStore()

const t = computed(() => ({
  title: store.lang === 'zh' ? `楼层布局 - ${store.fpGroup?.name}` : `Floor Plan - ${store.fpGroup?.name}`,
  subtitle: store.lang === 'zh' ? `${store.fpAllSlots.length} 个可用库位` : `${store.fpAllSlots.length} slots available`,
  preview: store.lang === 'zh' ? '布局预览' : 'Layout Preview',
  no_rows: store.lang === 'zh' ? '暂无行' : 'No rows yet',
  hint: store.lang === 'zh' ? '拖拽行以重新排序 · 分配库位到单元格' : 'Drag rows to reorder · Assign slots to cells',
  cancel: store.lang === 'zh' ? '取消' : 'Cancel',
  save: store.lang === 'zh' ? '保存布局' : 'Save Layout',
}))

// Typed so `ly.key` narrows to the same union as `store.fpLayer`; a bare string
// array is not assignable to it.
const layers: Array<{ key: 'paint' | 'zone' | 'wall'; label: string }> = [
  { key: 'paint', label: store.lang === 'zh' ? '货架布局' : 'Rack Layout' },
  { key: 'zone', label: store.lang === 'zh' ? '区域设施' : 'Zones & Facilities' },
  { key: 'wall', label: store.lang === 'zh' ? '墙壁走廊' : 'Walls & Corridors' },
]

function shortName(wh: string): string {
  return wh.replace(/\s*-\s*[A-Z]{2,6}$/, '').split('/').pop()?.trim() || ''
}

function close() {
  store.fpOpen = false
}

async function save() {
  store.fpSaving = true
  try {
    store.fpSaveOk = true
    setTimeout(() => {
      store.fpSaveOk = false
    }, 2000)
  } finally {
    store.fpSaving = false
  }
}
</script>

<style scoped>
.wt-modal-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 95;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wt-modal {
  background: #13151e;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  width: 680px;
  max-width: 95vw;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.6);
  overflow: hidden;
  animation: wtFpIn 0.22s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes wtFpIn {
  from {
    opacity: 0;
    transform: scale(0.94);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.wt-modal-lg {
  width: 680px;
}

.wt-modal-hdr {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
  flex-shrink: 0;
}

.wt-modal-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.wt-modal-sub {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.35);
  margin-top: 2px;
}

.wt-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.wt-modal-body::-webkit-scrollbar {
  width: 4px;
}

.wt-modal-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.wt-modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.07);
  flex-shrink: 0;
}

.wt-footer-left {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.3);
}

.wt-footer-right {
  display: flex;
  gap: 8px;
}

.wt-fp-layers {
  display: flex;
  gap: 6px;
  margin-bottom: 12px;
}

.wt-layer-btn {
  height: 24px;
  padding: 0 12px;
  border-radius: 6px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s;
}

.wt-layer-btn.act {
  background: #3b82f6;
}

.wt-fp-preview {
  margin-bottom: 12px;
}

.wt-fp-preview-lbl {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.8px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.25);
  margin-bottom: 6px;
}

.wt-fp-preview-grid {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.wt-fp-empty {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.2);
  text-align: center;
  padding: 8px;
}

.wt-fp-prev-row {
  display: flex;
  gap: 4px;
}

.wt-fp-prev-cell {
  height: 28px;
  border-radius: 4px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  color: #fff;
  flex: 1;
  overflow: hidden;
  white-space: nowrap;
  padding: 0 4px;
}

.wt-fp-prev-cell.empty {
  background: rgba(255, 255, 255, 0.03);
  color: rgba(255, 255, 255, 0.2);
  border-style: dashed;
}

.wt-fp-prev-cell.filled {
  background: rgba(59, 130, 246, 0.2);
  border-color: rgba(59, 130, 246, 0.5);
  color: #93c5fd;
}

.wt-fp-prev-cell.aisle {
  background: repeating-linear-gradient(
    -45deg,
    rgba(255, 255, 255, 0.03) 0,
    rgba(255, 255, 255, 0.03) 2px,
    transparent 2px,
    transparent 6px
  );
  color: rgba(255, 255, 255, 0.2);
}

.wt-x-btn {
  width: 22px;
  height: 22px;
  border-radius: 5px;
  border: 1px solid var(--wt-cb);
  background: var(--wt-card);
  color: var(--wt-text2);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}

.wt-x-btn:hover {
  background: rgba(255, 255, 255, 0.14);
}

.wt-btn-cancel {
  height: 32px;
  padding: 0 14px;
  border-radius: 7px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.6);
  font-size: 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wt-btn-cancel:hover {
  background: rgba(255, 255, 255, 0.08);
}

.wt-btn-save {
  height: 32px;
  padding: 0 16px;
  border-radius: 7px;
  border: none;
  background: #3b82f6;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.wt-btn-save:hover {
  background: #2563eb;
}

.wt-btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
