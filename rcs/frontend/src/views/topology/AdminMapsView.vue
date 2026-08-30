<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">{{ t('admin.maps.title') }}</h1>
        <p class="hero-sub">{{ t('admin.maps.subtitle') }}</p>
      </div>
      <div class="hero-actions">
        <a-button :loading="store.loading" @click="store.load()">
          <template #icon><ReloadOutlined /></template>
          {{ t('common.refresh') }}
        </a-button>
        <a-button type="primary" @click="openCreate">
          <template #icon><PlusOutlined /></template>
          {{ t('admin.maps.create') }}
        </a-button>
      </div>
    </header>

    <div class="data-panel">
      <div class="panel-head">
        <h3>{{ t('admin.maps.title') }}</h3>
      </div>
      <a-table
        :columns="columns"
        :data-source="store.maps"
        :loading="store.loading"
        :pagination="{ pageSize: 10, showSizeChanger: true }"
        :row-class-name="rowClass"
        :custom-row="mapCustomRow"
        row-key="map_id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'current_version'">
            <a-tag>v{{ (record as SiteMapRow).current_version }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'nodes'">
            {{ ((record as SiteMapRow).nodes ?? []).length }}
          </template>
          <template v-else-if="column.dataIndex === 'edges'">
            {{ ((record as SiteMapRow).edges ?? []).length }}
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-popconfirm :title="t('common.deleteConfirm')" @confirm="remove((record as SiteMapRow).map_id)">
              <a-button size="small" type="link" danger @click.stop>{{ t('common.delete') }}</a-button>
            </a-popconfirm>
          </template>
        </template>
        <template #emptyText>
          <span class="text-muted">{{ t('common.noData') }}</span>
        </template>
      </a-table>
    </div>

    <div v-if="store.current" class="data-panel">
      <div class="panel-head">
        <h3>{{ store.current.name || store.current.map_id }} (v{{ store.current.current_version }})</h3>
      </div>
      <svg :viewBox="`0 0 ${vbW} ${vbH}`" width="100%" height="320" class="canvas">
        <g v-for="e in store.current.edges" :key="`${e.from}-${e.to}`">
          <line :x1="nodeXY(e.from).x" :y1="nodeXY(e.from).y"
                :x2="nodeXY(e.to).x" :y2="nodeXY(e.to).y"
                stroke="var(--border-strong, #888)" stroke-width="1" />
        </g>
        <g v-for="n in store.current.nodes" :key="n.id">
          <circle :cx="nodeXY(n.id).x" :cy="nodeXY(n.id).y" r="6" fill="var(--accent, #3b82f6)" />
          <text :x="nodeXY(n.id).x + 8" :y="nodeXY(n.id).y + 4" font-size="10">{{ n.id }}</text>
        </g>
      </svg>
    </div>

    <div v-if="store.current" class="data-panel">
      <div class="panel-head">
        <h3>{{ t('admin.maps.import') }} / {{ t('admin.maps.export') }}</h3>
      </div>
      <a-form layout="vertical" class="io-form">
        <a-form-item :label="t('admin.maps.import') + ' (JSON)'">
          <a-textarea
            v-model:value="jsonText"
            :rows="8"
            :placeholder="t('admin.maps.importPlaceholder')"
            class="mono"
          />
        </a-form-item>
        <a-space>
          <a-button type="primary" :disabled="!jsonText" @click="doImport">
            {{ t('admin.maps.import') }}
          </a-button>
          <a-button @click="doExport">{{ t('admin.maps.export') }}</a-button>
        </a-space>
        <a-form-item v-if="exportedText" :label="t('admin.maps.export')">
          <pre class="exported mono">{{ exportedText }}</pre>
        </a-form-item>
      </a-form>
    </div>

    <div v-if="store.current" class="data-panel">
      <div class="panel-head">
        <h3>{{ t('admin.maps.versions') }}</h3>
      </div>
      <a-list size="small" :data-source="store.versions" :locale="{ emptyText: t('common.noData') }">
        <template #renderItem="{ item }">
          <a-list-item>
            <span class="mono">v{{ item.version }}</span>
            <span class="version-note">{{ item.note || '-' }}</span>
            <a-button
              v-if="item.note !== 'initial'"
              size="small"
              type="link"
              @click="store.restore(store.current!.map_id, item.version_id)"
            >
              {{ t('admin.maps.restore') }}
            </a-button>
          </a-list-item>
        </template>
      </a-list>
    </div>

    <a-modal
      v-model:open="createOpen"
      :title="t('admin.maps.create')"
      :confirm-loading="creating"
      @ok="submitCreate"
    >
      <a-form layout="vertical">
        <a-form-item :label="t('admin.maps.name')" required>
          <a-input v-model:value="newName" :placeholder="t('admin.maps.namePlaceholder')" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { useAdminMapStore } from '@/stores/adminMaps'
import type { SiteNode } from '@/types'

const { t } = useI18n()
const store = useAdminMapStore()
onMounted(() => store.load())

type SiteMapRow = {
  map_id: string
  name: string
  current_version: number
  nodes?: unknown[]
  edges?: unknown[]
}

const jsonText = ref('')
const exportedText = ref('')
const createOpen = ref(false)
const creating = ref(false)
const newName = ref('')

const columns = [
  { title: 'ID', dataIndex: 'map_id', width: 240 },
  { title: t('admin.maps.name'), dataIndex: 'name' },
  { title: t('admin.maps.version'), dataIndex: 'current_version', width: 90 },
  { title: t('admin.maps.nodes'), dataIndex: 'nodes', width: 90 },
  { title: t('admin.maps.edges'), dataIndex: 'edges', width: 90 },
  { title: t('common.actions'), dataIndex: 'action', width: 90, fixed: 'right' as const },
]

const vbW = computed(() => Math.max(800, ...(store.current?.nodes.map(n => (n.pos[0] || 0) + 60) || [0])))
const vbH = computed(() => Math.max(400, ...(store.current?.nodes.map(n => (n.pos[1] || 0) + 60) || [0])))

function nodeXY(id: string): { x: number; y: number } {
  const n: SiteNode | undefined = store.current?.nodes.find(x => x.id === id)
  if (!n) return { x: 0, y: 0 }
  return { x: (n.pos[0] || 0) + 20, y: (n.pos[1] || 0) + 20 }
}

function rowClass(record: SiteMapRow): string {
  return store.current?.map_id === record.map_id ? 'row-active' : ''
}

function mapCustomRow(record: SiteMapRow) {
  return { onClick: () => store.select(record.map_id) }
}

async function doImport() {
  if (!store.current) return
  try {
    const payload = JSON.parse(jsonText.value)
    await store.importJson(store.current.map_id, payload)
    jsonText.value = ''
    message.success(t('common.success'))
  } catch (e) {
    message.error(t('common.failed') + ': ' + (e as Error).message)
  }
}

async function doExport() {
  if (!store.current) return
  const data = await store.exportJson(store.current.map_id)
  exportedText.value = JSON.stringify(data, null, 2)
}

function openCreate() {
  newName.value = ''
  createOpen.value = true
}

async function submitCreate() {
  if (!newName.value.trim()) {
    message.warning(t('common.required'))
    return
  }
  creating.value = true
  try {
    await store.create({ name: newName.value.trim() })
    createOpen.value = false
    message.success(t('common.success'))
  } finally {
    creating.value = false
  }
}

async function remove(id: string) {
  await store.remove(id)
}
</script>

<style scoped>
.canvas { background: var(--bg-elevated); border: 1px solid var(--border); border-radius: var(--radius); }
.io-form { max-width: 720px; }
.mono { font-family: var(--font-mono, monospace); }
.exported { background: var(--bg-elevated); padding: 8px; overflow: auto; max-height: 240px; border-radius: var(--radius); margin: 0; }
.version-note { flex: 1; color: var(--fg-secondary); }
:deep(.row-active > td) { background: var(--bg-hover) !important; }
</style>
