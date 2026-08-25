<template>
  <div class="admin-view">
    <h2>场景地图（查看器 + JSON 导入/导出）</h2>
    <div class="row">
      <button @click="store.load()" :disabled="store.loading">刷新</button>
      <button @click="createMap">新建</button>
    </div>
    <table class="grid" v-if="store.maps.length">
      <thead><tr><th>ID</th><th>名称</th><th>版本</th><th>节点数</th><th>边数</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="m in store.maps" :key="m.map_id"
            :class="{ active: store.current?.map_id === m.map_id }"
            @click="store.select(m.map_id)">
          <td>{{ m.map_id }}</td>
          <td>{{ m.name }}</td>
          <td>v{{ m.current_version }}</td>
          <td>{{ m.nodes.length }}</td>
          <td>{{ m.edges.length }}</td>
          <td><button @click.stop="remove(m.map_id)">删</button></td>
        </tr>
      </tbody>
    </table>

    <div v-if="store.current" class="viewer">
      <h3>{{ store.current.name || store.current.map_id }} (v{{ store.current.current_version }})</h3>
      <svg :viewBox="`0 0 ${vbW} ${vbH}`" width="100%" height="320" class="canvas">
        <g v-for="e in store.current.edges" :key="`${e.from}-${e.to}`">
          <line :x1="nodeXY(e.from).x" :y1="nodeXY(e.from).y"
                :x2="nodeXY(e.to).x" :y2="nodeXY(e.to).y"
                stroke="#888" stroke-width="1" />
        </g>
        <g v-for="n in store.current.nodes" :key="n.id">
          <circle :cx="nodeXY(n.id).x" :cy="nodeXY(n.id).y" r="6" fill="#3b82f6" />
          <text :x="nodeXY(n.id).x + 8" :y="nodeXY(n.id).y + 4" font-size="10">{{ n.id }}</text>
        </g>
      </svg>

      <div class="import-export">
        <h4>导入（JSON）</h4>
        <textarea v-model="jsonText" rows="8"></textarea>
        <button @click="doImport" :disabled="!jsonText">导入</button>
        <button @click="doExport">导出</button>
        <pre v-if="exportedText">{{ exportedText }}</pre>

        <h4>版本历史</h4>
        <ul>
          <li v-for="v in store.versions" :key="v.version_id">
            v{{ v.version }} — {{ v.note || '' }}
            <button v-if="v.note !== 'initial'" @click="store.restore(store.current!.map_id, v.version_id)">恢复</button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useAdminMapStore } from '@/stores/adminMaps'
import type { SiteNode } from '@/types'

const store = useAdminMapStore()
onMounted(() => store.load())

const jsonText = ref('')
const exportedText = ref('')

const vbW = computed(() => Math.max(800, ...(store.current?.nodes.map(n => (n.pos[0] || 0) + 60) || [0])))
const vbH = computed(() => Math.max(400, ...(store.current?.nodes.map(n => (n.pos[1] || 0) + 60) || [0])))

function nodeXY(id: string): { x: number; y: number } {
  const n: SiteNode | undefined = store.current?.nodes.find(x => x.id === id)
  if (!n) return { x: 0, y: 0 }
  return { x: (n.pos[0] || 0) + 20, y: (n.pos[1] || 0) + 20 }
}

async function doImport() {
  if (!store.current) return
  try {
    const payload = JSON.parse(jsonText.value)
    await store.importJson(store.current.map_id, payload)
    jsonText.value = ''
  } catch (e) {
    alert('JSON 格式错误: ' + (e as Error).message)
  }
}

async function doExport() {
  if (!store.current) return
  const data = await store.exportJson(store.current.map_id)
  exportedText.value = JSON.stringify(data, null, 2)
}

async function createMap() {
  const name = prompt('地图名称?') || ''
  if (!name) return
  await store.create({ name })
}

async function remove(id: string) {
  if (!confirm(`删除 ${id}?`)) return
  await store.remove(id)
}
</script>

<style scoped>
.admin-view { padding: 16px; }
.row { display: flex; gap: 8px; margin-bottom: 8px; }
.grid { width: 100%; border-collapse: collapse; }
.grid th, .grid td { border: 1px solid #ddd; padding: 6px 8px; }
.grid tr.active { background: #f0f7ff; }
.viewer { margin-top: 16px; }
.canvas { background: #fafafa; border: 1px solid #ddd; }
.import-export { margin-top: 16px; max-width: 720px; }
textarea { width: 100%; font-family: monospace; }
pre { background: #f6f8fa; padding: 8px; overflow: auto; max-height: 240px; }
</style>