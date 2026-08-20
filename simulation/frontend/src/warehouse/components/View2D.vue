<template>
  <div id="wt-view2d">
    <div class="wt-2d-wrap">
      <template v-if="sections.length">
        <div v-for="sec in sections" :key="sec.key" class="wt-2d-sec">
          <div class="wt-2d-sec-hdr">
            <div class="wt-2d-sec-name">{{ sec.key }}</div>
            <div :class="['wt-2d-sec-cnt', sec.cntCls]">{{ sec.occ }}/{{ sec.tiles.length }}</div>
          </div>
          <div class="wt-2d-sec-cap">
            <div class="wt-2d-sec-cap-fill" :style="{ width: sec.avgFp + '%', background: sec.barClr }"></div>
          </div>
          <div class="wt-2d-slots" :style="{ 'grid-template-columns': 'repeat(' + sec.cols + ',1fr)' }">
            <div
              v-for="(sl, ti) in sec.tiles"
              :key="sl.wh"
              :class="['wt-2d-tile', tileCls(sl)]"
              :style="{ 'animation-delay': ti * 30 + 'ms' }"
              @click="onTileClick(sl)"
            >
              <div class="wt-2d-tile-name">{{ sl.label }}</div>
              <div class="wt-2d-tile-qty">{{ tileQty(sl) > 0 ? fmtK(tileQty(sl)) : '—' }}</div>
            </div>
          </div>
        </div>
      </template>
      <div v-else style="padding: 32px; color: var(--wt-text3); font-size: 13px">
        {{ t.no_data }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useWarehouseStore } from '../store/warehouse'
import type { Slot } from '../types'

const store = useWarehouseStore()

const t = computed(() => ({
  no_data: store.lang === 'zh' ? '暂无数据' : 'No data',
}))

const sections = computed(() => {
  const slots = store.filteredSlots
  const secMap: Record<string, any[]> = {}
  const secOrder: string[] = []

  slots.forEach((sl) => {
    const nm = (sl.label || sl.wh || '').replace(/\s*-\s*[A-Z]{1,8}$/, '').split('/').pop()?.trim() || ''
    const key = nm.match(/^([A-Za-z]+)/)?.[1] || nm.substring(0, 2)
    if (!secMap[key]) {
      secMap[key] = []
      secOrder.push(key)
    }
    secMap[key].push({ ...sl, shortName: nm })
  })

  secOrder.sort((a, b) => a.localeCompare(b))
  secOrder.forEach((key) => {
    if (secMap[key]) secMap[key].sort((a, b) => a.shortName.localeCompare(b.shortName))
  })

  return secOrder.map((key) => {
    const tiles = secMap[key]
    const cols = tiles.length <= 1 ? 1 : tiles.length <= 4 ? 2 : 3
    const occ = tiles.filter((s) => hasStock(s)).length
    const pct = tiles.length ? Math.round((occ / tiles.length) * 100) : 0
    const cntCls = pct >= 80 ? 'red' : pct >= 50 ? 'org' : 'grn'
    const avgFp = tiles.length ? Math.round(tiles.reduce((s, t) => s + slotFill(t), 0) / tiles.length) : 0
    const barClr = avgFp > 0 ? FCH(avgFp) : 'var(--wt-border)'
    return { key, tiles, cols, occ, cntCls, avgFp, barClr }
  })
})

function tileCls(sl: Slot): string {
  const fp = slotFill(sl)
  const hs = hasStock(sl)
  return !hs ? 'empty' : fp >= 90 ? 'full' : fp >= 70 ? 'high' : fp >= 40 ? 'mid' : 'low'
}

function tileQty(sl: Slot): number {
  return sl.levels.reduce((s, l) => s + (l.uoms || []).reduce((ss, u) => ss + (u.qty || 0), 0), 0)
}

function hasStock(sl: Slot): boolean {
  return sl.levels.some((l) => (l.uoms || []).some((u) => u.qty > 0))
}

function slotFill(sl: Slot): number {
  return sl.levels.length ? Math.round(sl.levels.reduce((s, l) => s + lvFill(l), 0) / sl.levels.length) : 0
}

function lvFill(lv: any): number {
  const wc = (lv.uoms || []).filter((u: any) => u.cap > 0)
  if (!wc.length) return (lv.uoms || []).some((u: any) => u.qty > 0) ? 50 : 0
  return Math.round(wc.reduce((s: number, u: any) => s + Math.min(100, Math.round((u.qty / u.cap) * 100)), 0) / wc.length)
}

function FCH(p: number): string {
  return p >= 90 ? '#f87171' : p >= 70 ? '#fb923c' : p >= 40 ? '#facc15' : '#4ade80'
}

function fmtK(n: number): string {
  return n >= 1000 ? (n / 1000).toFixed(1) + 'K' : n.toLocaleString()
}

function onTileClick(sl: Slot) {
  store.openDetailPanel({ kind: 'slot', ref: sl.wh, slot: sl.wh })
}
</script>

<style scoped>
#wt-view2d {
  position: absolute;
  left: 148px;
  right: 0;
  top: 44px;
  bottom: 0;
  overflow: auto;
  display: block;
  background: var(--wt-bg);
}

#wt-view2d::-webkit-scrollbar {
  width: 5px;
}

#wt-view2d::-webkit-scrollbar-thumb {
  background: var(--wt-border);
  border-radius: 10px;
}

.wt-2d-wrap {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
  padding: 16px;
}

.wt-2d-sec {
  background: var(--wt-bg2);
  border-radius: 14px;
  padding: 12px;
  border: 1.5px solid var(--wt-cb);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  transition: border-color 0.15s, box-shadow 0.15s;
}

.wt-2d-sec:hover {
  border-color: var(--wt-accent);
  box-shadow: 0 4px 14px rgba(49, 130, 206, 0.1);
}

.wt-2d-sec-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 7px;
  border-bottom: 1px solid var(--wt-border);
}

.wt-2d-sec-name {
  font-size: 11px;
  font-weight: 800;
  color: var(--wt-text);
}

.wt-2d-sec-cnt {
  font-size: 9px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 4px;
  white-space: nowrap;
}

.wt-2d-sec-cnt.red {
  background: #fff5f5;
  color: #c53030;
}
.wt-2d-sec-cnt.org {
  background: #fffaf0;
  color: #c05621;
}
.wt-2d-sec-cnt.grn {
  background: #f0fff4;
  color: #276749;
}

#wt-app.dark .wt-2d-sec-cnt.red {
  background: rgba(197, 48, 48, 0.15);
  color: #fc8181;
}
#wt-app.dark .wt-2d-sec-cnt.org {
  background: rgba(192, 86, 33, 0.15);
  color: #fbd38d;
}
#wt-app.dark .wt-2d-sec-cnt.grn {
  background: rgba(39, 103, 73, 0.15);
  color: #68d391;
}

.wt-2d-sec-cap {
  height: 3px;
  background: var(--wt-cb);
  border-radius: 2px;
  margin-bottom: 8px;
  overflow: hidden;
}

.wt-2d-sec-cap-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.7s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.wt-2d-slots {
  display: grid;
  gap: 5px;
}

.wt-2d-tile {
  border-radius: 8px;
  padding: 7px 5px 5px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  text-align: center;
  border: 1.5px solid var(--wt-cb);
  background: var(--wt-card);
  transition: transform 0.15s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.12s;
  position: relative;
  animation: wt2dIn 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  height: auto;
}

@keyframes wt2dIn {
  from {
    opacity: 0;
    transform: scale(0.88);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.wt-2d-tile:hover {
  transform: translateY(-2px) scale(1.04);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.14);
  z-index: 2;
}

.wt-2d-tile.empty {
  background: repeating-linear-gradient(
    -45deg,
    rgba(0, 0, 0, 0.04) 0,
    rgba(0, 0, 0, 0.04) 2px,
    transparent 2px,
    transparent 7px
  );
  border-color: var(--wt-cb);
}

.wt-2d-tile.low {
  background: rgba(74, 222, 128, 0.12);
  border-color: #4ade80;
}
.wt-2d-tile.mid {
  background: rgba(250, 204, 21, 0.12);
  border-color: #facc15;
}
.wt-2d-tile.high {
  background: rgba(251, 146, 60, 0.12);
  border-color: #fb923c;
}
.wt-2d-tile.full {
  background: rgba(248, 113, 113, 0.12);
  border-color: #f87171;
}

.wt-2d-tile-name {
  font-size: 10px;
  font-weight: 800;
  color: var(--wt-text);
  line-height: 1.2;
  word-break: break-all;
}

.wt-2d-tile.empty .wt-2d-tile-name {
  color: var(--wt-text3);
}

.wt-2d-tile-qty {
  font-size: 8px;
  font-weight: 600;
  color: var(--wt-text2);
  margin-top: 2px;
}

.wt-2d-tile.empty .wt-2d-tile-qty {
  color: var(--wt-border);
}
</style>
