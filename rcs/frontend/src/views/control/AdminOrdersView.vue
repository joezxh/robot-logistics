<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">{{ t('admin.orders.title') }}</h1>
        <p class="hero-sub">{{ t('admin.orders.subtitle') }}</p>
      </div>
      <div class="hero-actions">
        <a-button :loading="store.loading" @click="store.load(filterStatus || undefined)">
          <template #icon><ReloadOutlined /></template>
          {{ t('common.refresh') }}
        </a-button>
      </div>
    </header>

    <div class="data-panel">
      <div class="panel-head">
        <h3>{{ t('admin.orders.title') }}</h3>
        <div class="panel-tools">
          <a-select
            v-model:value="filterStatus"
            :placeholder="t('admin.orders.statusFilter')"
            style="width: 160px"
            allow-clear
            @change="onFilterChange"
          >
            <a-select-option value="">{{ t('admin.orders.all') }}</a-select-option>
            <a-select-option v-for="s in statusOptions" :key="s" :value="s">{{ s }}</a-select-option>
          </a-select>
        </div>
      </div>
      <a-table
        :columns="orderColumns"
        :data-source="store.orders"
        :loading="store.loading"
        :pagination="{ pageSize: 10, showSizeChanger: true }"
        :row-class-name="rowClass"
        :custom-row="orderCustomRow"
        row-key="order_id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="statusColor((record as OrderRow).status)">{{ (record as OrderRow).status }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-space :size="4">
              <a-button
                v-if="(record as OrderRow).status === 'queued'"
                size="small"
                type="link"
                @click.stop="advance((record as OrderRow).order_id, 'running')"
              >
                {{ t('admin.orders.start') }}
              </a-button>
              <a-button
                v-if="(record as OrderRow).status === 'running'"
                size="small"
                type="link"
                @click.stop="advance((record as OrderRow).order_id, 'done')"
              >
                {{ t('admin.orders.done') }}
              </a-button>
              <a-button
                v-if="(record as OrderRow).status !== 'cancelled' && (record as OrderRow).status !== 'done'"
                size="small"
                type="link"
                danger
                @click.stop="advance((record as OrderRow).order_id, 'cancelled')"
              >
                {{ t('admin.orders.cancel') }}
              </a-button>
            </a-space>
          </template>
        </template>
        <template #emptyText>
          <span class="text-muted">{{ t('admin.orders.noOrders') }}</span>
        </template>
      </a-table>
    </div>

    <div v-if="store.current" class="data-panel">
      <div class="panel-head">
        <h3>{{ t('admin.orders.tasks') }} — {{ store.current.order_id }}</h3>
      </div>
      <a-table
        :columns="taskColumns"
        :data-source="store.tasks"
        :pagination="false"
        row-key="node_id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'depends_on'">
            {{ (record as OrderTask).depends_on?.join(', ') || '-' }}
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-space :size="4">
              <a-button size="small" type="link" @click="setTaskDone((record as OrderTask).node_id)">
                {{ t('admin.orders.done') }}
              </a-button>
              <a-button size="small" type="link" danger @click="setTaskFail((record as OrderTask).node_id)">
                {{ t('admin.orders.failed') }}
              </a-button>
            </a-space>
          </template>
        </template>
        <template #emptyText>
          <span class="text-muted">{{ t('common.noData') }}</span>
        </template>
      </a-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useAdminOrderStore } from '@/stores/adminOrders'
import type { OrderRow, OrderTask } from '@/types'

const { t } = useI18n()
const store = useAdminOrderStore()
const filterStatus = ref('')
const statusOptions = ['queued', 'running', 'done', 'failed', 'cancelled']

onMounted(() => store.load())

const orderColumns = [
  { title: t('admin.orders.orderId'), dataIndex: 'order_id', width: 200 },
  { title: t('admin.orders.scenario'), dataIndex: 'scenario_id', width: 130 },
  { title: t('admin.orders.priority'), dataIndex: 'priority', width: 90 },
  { title: t('common.status'), dataIndex: 'status', width: 110 },
  { title: t('admin.orders.items'), dataIndex: 'items', width: 90 },
  { title: t('admin.orders.taskCount'), dataIndex: 'tasks', width: 90 },
  { title: t('common.actions'), dataIndex: 'action', width: 180, fixed: 'right' as const },
]

const taskColumns = [
  { title: t('admin.orders.node'), dataIndex: 'node_id', width: 160 },
  { title: t('admin.orders.taskType'), dataIndex: 'task_type', width: 120 },
  { title: 'SLO', dataIndex: 'slo_class', width: 110 },
  { title: t('admin.orders.depends'), dataIndex: 'depends_on' },
  { title: t('common.status'), dataIndex: 'status', width: 110 },
  { title: t('common.actions'), dataIndex: 'action', width: 140, fixed: 'right' as const },
]

function statusColor(status: string): string {
  switch (status) {
    case 'queued': return 'gold'
    case 'running': return 'blue'
    case 'done': return 'green'
    case 'failed': return 'red'
    default: return 'default'
  }
}

function rowClass(record: OrderRow): string {
  return store.current?.order_id === record.order_id ? 'row-active' : ''
}

function orderCustomRow(record: OrderRow) {
  return { onClick: () => store.select(record.order_id) }
}

function onFilterChange() {
  store.load(filterStatus.value || undefined)
}

async function advance(id: string, status: string) {
  await store.advance(id, status)
}
async function setTaskDone(nodeId: string) {
  if (!store.current) return
  await store.setTaskStatus(store.current.order_id, nodeId, 'done')
}
async function setTaskFail(nodeId: string) {
  if (!store.current) return
  await store.setTaskStatus(store.current.order_id, nodeId, 'failed')
}
</script>

<style scoped>
.panel-tools { display: flex; gap: 8px; }
:deep(.row-active > td) { background: var(--bg-hover) !important; }
</style>
