<script setup lang="ts">
/**
 * Scene map editor — CRUD over a map's `geometry` (wt_floor_shell).
 *
 * Master/detail: a table of every layout element (zones / docks / walls /
 * facilities), a side form to edit the selected row, plus Add / Delete. Saving
 * PUTs the whole geometry back to the backend; the 3D preview (ThreeMapViewer)
 * is cache-busted via `reloadKey` so it re-renders from the new geometry.
 */
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getMap, updateMap, type WtFloorShellGeometry } from '@/api/map'
import ThreeMapViewer from './ThreeMapViewer.vue'

const route = useRoute()
const router = useRouter()
const mapId = computed(() => String(route.params.id))
const loading = ref(false)
const error = ref('')
const saving = ref(false)
const savedAt = ref('')
const reloadKey = ref(0)

const CATEGORIES = ['zones', 'docks', 'walls', 'facilities'] as const
type Category = (typeof CATEGORIES)[number]

interface Elem {
  ref: string
  type: string
  x: number
  z: number
  w: number
  d: number
  h: number
  y: number
  rot: number
  color: string
  label: string
}

const draft = ref<WtFloorShellGeometry | null>(null)
const selected = reactive<{ cat: Category | null; idx: number }>({ cat: null, idx: -1 })
const editing = ref<Elem | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const m = await getMap(mapId.value)
    // deep clone so edits don't mutate the fetched DTO until saved
    draft.value = JSON.parse(JSON.stringify(m.geometry || { bounds: { w: 0, d: 0 } }))
    for (const c of CATEGORIES) if (!Array.isArray(draft.value![c])) draft.value![c] = []
  } catch (e) {
    error.value = (e as Error).message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)

const elements = computed(() => {
  const g = draft.value
  if (!g) return []
  const out: { cat: Category; idx: number; el: Elem }[] = []
  for (const c of CATEGORIES) {
    ;(g[c] as Elem[]).forEach((el, idx) => out.push({ cat: c, idx, el: el as Elem }))
  }
  return out
})

function selectRow(cat: Category, idx: number) {
  selected.cat = cat
  selected.idx = idx
  editing.value = { ...((draft.value![cat] as Elem[])[idx]) }
}

function newElement(cat: Category): Elem {
  const suffix = ((draft.value![cat] as Elem[]).length + 1)
  const defaults: Record<string, Partial<Elem>> = {
    zones: { type: 'staging', color: '#0ea5e9', h: 0.3, w: 10, d: 10 },
    docks: { type: 'truck_dock', color: '#fbbf24', h: 0.4, y: 0.3, w: 4, d: 20 },
    walls: { type: 'wall', color: '#6b7280', h: 6, w: 20, d: 1 },
    facilities: { type: 'rack', color: '#94a3b8', h: 3, w: 4, d: 4 },
  }
  const d = defaults[cat]
  return {
    ref: `${cat.slice(0, -1)}_${suffix}`,
    type: d.type!,
    x: 0, z: 0, w: d.w!, d: d.d!, h: d.h!,
    y: d.y ?? 0, rot: 0, color: d.color!, label: `${cat.slice(0, -1)} ${suffix}`,
  }
}

function addRow(cat: Category) {
  const arr = draft.value![cat] as Elem[]
  arr.push(newElement(cat))
  selectRow(cat, arr.length - 1)
}

function applyEdit() {
  if (!editing.value || !selected.cat || selected.idx < 0) return
  const arr = draft.value![selected.cat] as Elem[]
  arr[selected.idx] = { ...editing.value }
}

function deleteRow() {
  if (!selected.cat || selected.idx < 0) return
  const arr = draft.value![selected.cat] as Elem[]
  arr.splice(selected.idx, 1)
  selected.cat = null
  selected.idx = -1
  editing.value = null
}

async function save() {
  if (!draft.value) return
  saving.value = true
  error.value = ''
  try {
    await updateMap(mapId.value, { geometry: draft.value })
    reloadKey.value++
    savedAt.value = new Date().toLocaleTimeString()
  } catch (e) {
    error.value = (e as Error).message || String(e)
  } finally {
    saving.value = false
  }
}

function back() {
  router.push(`/maps/${encodeURIComponent(mapId.value)}`)
}
</script>

<template>
  <div class="editor">
    <header class="editor-head">
      <button class="btn" @click="back">← 返回</button>
      <h2>地图编辑器 · {{ mapId }}</h2>
      <div class="spacer" />
      <span v-if="savedAt" class="saved">已保存 {{ savedAt }}</span>
      <button class="btn primary" :disabled="saving || !draft" @click="save">
        {{ saving ? '保存中…' : '保存到服务器' }}
      </button>
    </header>

    <p v-if="error" class="err">{{ error }}</p>
    <p v-if="loading" class="muted">加载中…</p>

    <div v-if="draft" class="editor-body">
      <!-- 3D preview -->
      <section class="preview">
        <ThreeMapViewer :map-id="mapId" :reload-key="reloadKey" />
      </section>

      <!-- element CRUD -->
      <section class="panel">
        <div class="bounds">
          <label>画布尺寸 w</label>
          <input type="number" v-model.number="draft.bounds.w" />
          <label>d</label>
          <input type="number" v-model.number="draft.bounds.d" />
        </div>

        <div class="cat-actions">
          <span class="muted">元素（{{ elements.length }}）</span>
          <span v-for="c in CATEGORIES" :key="c">
            <button class="btn sm" @click="addRow(c)">+ {{ c }}</button>
          </span>
        </div>

        <table class="grid">
          <thead>
            <tr>
              <th>类别</th><th>ref</th><th>type</th><th>x</th><th>z</th>
              <th>w</th><th>d</th><th>h</th><th>color</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in elements"
              :key="row.cat + row.idx"
              :class="{ active: selected.cat === row.cat && selected.idx === row.idx }"
              @click="selectRow(row.cat, row.idx)"
            >
              <td>{{ row.cat }}</td>
              <td>{{ row.el.ref }}</td>
              <td>{{ row.el.type }}</td>
              <td>{{ row.el.x }}</td>
              <td>{{ row.el.z }}</td>
              <td>{{ row.el.w }}</td>
              <td>{{ row.el.d }}</td>
              <td>{{ row.el.h }}</td>
              <td><span class="sw" :style="{ background: row.el.color }" /></td>
            </tr>
          </tbody>
        </table>

        <div v-if="editing" class="form">
          <h4>编辑：{{ editing.ref }}</h4>
          <div class="form-grid">
            <label>ref<input v-model="editing.ref" /></label>
            <label>type<input v-model="editing.type" /></label>
            <label>x<input type="number" v-model.number="editing.x" /></label>
            <label>z<input type="number" v-model.number="editing.z" /></label>
            <label>w<input type="number" v-model.number="editing.w" /></label>
            <label>d<input type="number" v-model.number="editing.d" /></label>
            <label>h<input type="number" v-model.number="editing.h" /></label>
            <label>y<input type="number" v-model.number="editing.y" /></label>
            <label>rot<input type="number" v-model.number="editing.rot" /></label>
            <label>color<input v-model="editing.color" /></label>
            <label>label<input v-model="editing.label" /></label>
          </div>
          <div class="form-actions">
            <button class="btn" @click="applyEdit">应用修改</button>
            <button class="btn danger" @click="deleteRow">删除此元素</button>
          </div>
        </div>
        <p v-else class="muted">点击表格中的一行进行编辑。</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.editor { display: flex; flex-direction: column; height: 100%; padding: 12px; gap: 10px; }
.editor-head { display: flex; align-items: center; gap: 10px; }
.editor-head h2 { margin: 0; font-size: 16px; }
.spacer { flex: 1; }
.saved { color: #4ade80; font-size: 12px; }
.err { color: #f87171; }
.muted { color: #94a3b8; font-size: 12px; }
.editor-body { flex: 1; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; min-height: 0; }
.preview { min-height: 360px; border: 1px solid #1e293b; border-radius: 8px; overflow: hidden; }
.panel { overflow: auto; border: 1px solid #1e293b; border-radius: 8px; padding: 10px; }
.bounds { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; }
.bounds input { width: 70px; }
.cat-actions { display: flex; align-items: center; gap: 6px; margin-bottom: 8px; flex-wrap: wrap; }
.grid { width: 100%; border-collapse: collapse; font-size: 12px; }
.grid th, .grid td { border: 1px solid #1e293b; padding: 3px 6px; text-align: left; }
.grid tr.active { background: #1e3a5f; cursor: pointer; }
.grid tbody tr:hover { background: #16233a; }
.sw { display: inline-block; width: 14px; height: 14px; border-radius: 3px; }
.form { margin-top: 10px; border-top: 1px solid #1e293b; padding-top: 8px; }
.form-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px 10px; }
.form-grid label { display: flex; flex-direction: column; font-size: 11px; color: #94a3b8; }
.form-grid input { background: #0f1320; border: 1px solid #1e293b; color: #e2e8f0; border-radius: 4px; padding: 3px 6px; }
.form-actions { margin-top: 8px; display: flex; gap: 8px; }
.btn { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px; padding: 5px 10px; cursor: pointer; }
.btn:hover { background: #273449; }
.btn.sm { padding: 3px 8px; font-size: 12px; }
.btn.primary { background: #2563eb; border-color: #2563eb; }
.btn.danger { background: #7f1d1d; border-color: #7f1d1d; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
