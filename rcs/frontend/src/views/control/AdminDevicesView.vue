<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">{{ t('sys.devices.title') }}</h1>
        <p class="hero-sub">{{ t('sys.devices.subtitle') }}</p>
      </div>
      <div class="hero-actions">
        <a-button type="primary" :loading="store.loading" @click="store.load()">
          <template #icon><ReloadOutlined /></template>
          {{ t('common.refresh') }}
        </a-button>
      </div>
    </header>

    <div class="data-panel">
      <div class="panel-head">
        <h3>{{ t('sys.devices.list') }}</h3>
      </div>
      <a-table
        :columns="columns"
        :data-source="store.devices"
        :loading="store.loading"
        :pagination="{ pageSize: 10, showSizeChanger: true, showTotal: (t:number)=>`${t}` }"
        row-key="device_id"
        :row-class-name="(record: DeviceRow) => store.selectedId === record.device_id ? 'row-active' : ''"
        size="small"
        @row-click="(_: unknown, record: DeviceRow) => (store.selectedId = record.device_id)"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="statusColor((record as DeviceRow).status)">
              {{ (record as DeviceRow).status }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'updated_at'">
            <span class="mono">{{ (record as DeviceRow).updated_at || '-' }}</span>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-popconfirm
              :title="t('common.deleteConfirm')"
              @confirm="remove((record as DeviceRow).device_id)"
            >
              <a-button type="link" danger size="small">{{ t('common.delete') }}</a-button>
            </a-popconfirm>
          </template>
        </template>
        <template #emptyText>
          <span class="text-muted">{{ t('common.noData') }}</span>
        </template>
      </a-table>
    </div>

    <div v-if="selected" class="data-panel">
      <div class="panel-head">
        <h3>{{ t('sys.devices.edit') }} — {{ selected.device_id }}</h3>
      </div>
      <div class="detail">
        <label>{{ t('sys.devices.status') }}</label>
        <a-select v-model:value="draft.status" style="max-width: 240px">
          <a-select-option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</a-select-option>
        </a-select>
        <label>{{ t('sys.devices.mode') }}</label>
        <a-input v-model:value="draft.mode" :placeholder="t('sys.devices.modePlaceholder')" />
        <label>Limits JSON</label>
        <a-textarea v-model:value="limitsText" :rows="6" class="mono" />
        <label>Home joints (JSON)</label>
        <a-textarea v-model:value="homeText" :rows="2" class="mono" />
        <div class="detail-actions">
          <a-button type="primary" :loading="saving" @click="save">{{ t('common.save') }}</a-button>
          <span v-if="msg" class="msg">{{ msg }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useAdminDeviceStore } from '@/stores/adminDevices'
import type { DeviceRow } from '@/types/admin'

const { t } = useI18n()
const store = useAdminDeviceStore()
onMounted(() => store.load())

const statusOptions = ['registered', 'online', 'offline', 'error']

const columns = [
  { title: 'ID', dataIndex: 'device_id', width: 160 },
  { title: t('sys.devices.morphology'), dataIndex: 'morphology', width: 120 },
  { title: t('sys.devices.joints'), dataIndex: 'num_joints', width: 80 },
  { title: 'Hz', dataIndex: 'control_hz', width: 80 },
  { title: t('sys.devices.status'), dataIndex: 'status', width: 110 },
  { title: t('sys.devices.updatedAt'), dataIndex: 'updated_at', width: 200 },
  { title: t('common.action'), dataIndex: 'action', width: 90, fixed: 'right' as const },
]

const selected = computed<DeviceRow | undefined>(() =>
  store.devices.find(d => d.device_id === store.selectedId) || undefined,
)
const draft = ref<{ status: string; mode: string }>({ status: 'registered', mode: '' })
const limitsText = ref('[]')
const homeText = ref('[]')
const saving = ref(false)
const msg = ref('')

function statusColor(status?: string): string {
  switch (status) {
    case 'online': return 'green'
    case 'offline': return 'default'
    case 'error': return 'red'
    default: return 'blue'
  }
}

watch(selected, (d) => {
  if (d) {
    draft.value = { status: d.status, mode: d.mode || '' }
    limitsText.value = JSON.stringify(d.limits ?? {}, null, 2)
    homeText.value = JSON.stringify(d.home_joints ?? [], null, 2)
    msg.value = ''
  }
}, { immediate: true })

async function save() {
  if (!selected.value) return
  saving.value = true
  try {
    let limits: Record<string, number[]> = {}
    let home: number[] = []
    try { limits = JSON.parse(limitsText.value) } catch { msg.value = 'limits JSON ' + t('common.formatError'); return }
    try { home = JSON.parse(homeText.value) } catch { msg.value = 'home_joints JSON ' + t('common.formatError'); return }
    await store.save(selected.value.device_id, {
      status: draft.value.status,
      mode: draft.value.mode || null,
      limits,
      home_joints: home,
    })
    msg.value = t('common.saved')
  } catch (e) {
    msg.value = t('common.failed') + ': ' + (e as Error).message
  } finally {
    saving.value = false
  }
}

async function remove(id: string) {
  await store.remove(id)
  if (store.selectedId === id) store.selectedId = null
}
</script>

<style scoped>
.detail {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: 720px;
}
.detail label { color: var(--fg-secondary); font-size: 13px; }
.mono { font-family: var(--font-mono, monospace); }
.detail-actions { display: flex; align-items: center; gap: 12px; margin-top: 6px; }
.msg { color: var(--ok); }
:deep(.row-active > td) { background: var(--bg-hover) !important; }
</style>
