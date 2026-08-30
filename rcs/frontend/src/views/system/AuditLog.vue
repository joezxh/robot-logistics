<script setup lang="ts">
// Audit log viewer: filters, statistics and a maintenance purge.
import { computed, onMounted, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { message, Modal } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import * as api from '@/api/sysAudit'
import type { AuditLogRow, AuditStats } from '@/types'

const { t } = useI18n()

const rows = ref<AuditLogRow[]>([])
const total = ref(0)
const loading = ref(false)
const stats = ref<AuditStats | null>(null)
const page = ref(1)
const pageSize = ref(20)

const filters = reactive({
  username: '',
  operationType: undefined as string | undefined,
  keyword: '',
  range: undefined as [dayjs.Dayjs, dayjs.Dayjs] | undefined,
})

const OPERATION_TYPES = ['create', 'update', 'delete', 'query', 'login', 'logout'] as const

async function load() {
  loading.value = true
  try {
    const [res, statsRes] = await Promise.all([
      api.listAuditLogs({
        username: filters.username || undefined,
        operationType: filters.operationType,
        keyword: filters.keyword || undefined,
        startAt: filters.range?.[0]?.startOf('day').toISOString(),
        endAt: filters.range?.[1]?.endOf('day').toISOString(),
        skip: (page.value - 1) * pageSize.value,
        limit: pageSize.value,
      }),
      api.fetchAuditStats(),
    ])
    rows.value = res?.data ?? []
    total.value = res?.total ?? rows.value.length
    stats.value = statsRes?.data ?? null
  } finally {
    loading.value = false
  }
}

onMounted(load)

const columns = computed(() => [
  { title: t('sys.audit.user'), dataIndex: 'username', width: 120 },
  { title: t('sys.audit.operationType'), dataIndex: 'operationType', width: 110 },
  { title: t('sys.audit.operationModule'), dataIndex: 'operationModule', width: 120 },
  { title: t('sys.audit.operationDesc'), dataIndex: 'operationDesc' },
  { title: t('sys.audit.requestIp'), dataIndex: 'requestIp', width: 130 },
  { title: t('sys.audit.responseStatus'), dataIndex: 'responseStatus', width: 90 },
  { title: t('sys.audit.duration'), dataIndex: 'responseTimeMs', width: 90 },
  { title: t('common.createdAt'), dataIndex: 'createdAt', width: 180 },
  { title: t('common.actions'), dataIndex: 'actions', width: 80, fixed: 'right' },
])

function typeColor(type: string): string {
  return {
    create: 'green', update: 'blue', delete: 'red',
    query: 'default', login: 'cyan', logout: 'default',
  }[type] ?? 'default'
}

function statusColor(status?: number | null): string {
  if (status === undefined || status === null) return 'default'
  if (status < 300) return 'green'
  if (status < 400) return 'orange'
  return 'red'
}

function onTableChange(pager: { current?: number; pageSize?: number }) {
  page.value = pager.current ?? 1
  pageSize.value = pager.pageSize ?? 20
  load()
}

// --- detail drawer ---------------------------------------------------------
const detailOpen = ref(false)
const detail = ref<AuditLogRow | null>(null)

function openDetail(row: AuditLogRow) {
  detail.value = row
  detailOpen.value = true
}

// --- purge -----------------------------------------------------------------
function purge(before?: string) {
  Modal.confirm({
    title: before ? `${t('sys.audit.purgeOlder')} ${before}` : t('sys.audit.purgeAll'),
    content: t('common.deleteConfirm'),
    okType: 'danger',
    async onOk() {
      const res = await api.purgeAuditLogs(before)
      message.success(`${t('common.success')} (${res?.data?.deleted ?? 0})`)
      await load()
    },
  })
}
</script>

<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">{{ t('sys.audit.title') }}</h1>
        <p class="hero-sub">{{ t('common.total') }} {{ total }}</p>
      </div>
      <div class="hero-actions">
        <a-button danger @click="purge(dayjs().subtract(90, 'day').format('YYYY-MM-DD'))">
          {{ t('sys.audit.purge') }} (90d)
        </a-button>
        <a-button danger type="primary" @click="purge()">{{ t('sys.audit.purgeAll') }}</a-button>
        <a-button @click="load">{{ t('admin.devices.refresh') }}</a-button>
      </div>
    </header>

    <div class="stat-grid">
      <div class="stat-tile">
        <span class="stat-label">{{ t('sys.audit.totalRecords') }}</span>
        <span class="stat-value">{{ stats?.total ?? 0 }}</span>
      </div>
      <div class="stat-tile stat-by-type">
        <span class="stat-label">{{ t('sys.audit.operationType') }}</span>
        <div class="type-tags">
          <a-tag v-for="(count, type) in (stats?.byType ?? {})" :key="type" :color="typeColor(type)">
            {{ type }}: {{ count }}
          </a-tag>
          <span v-if="!stats?.byType" class="text-muted">-</span>
        </div>
      </div>
    </div>

    <div class="data-panel">
      <div class="panel-head">
        <h3>{{ t('sys.audit.title') }}</h3>
        <div class="toolbar">
          <a-input
            v-model:value="filters.username"
            :placeholder="t('sys.audit.user')"
            allow-clear
            class="toolbar-search"
            @press-enter="load"
          />
          <a-select
            v-model:value="filters.operationType"
            :placeholder="t('sys.audit.operationType')"
            allow-clear
            style="width: 150px"
            @change="load"
          >
            <a-select-option v-for="op in OPERATION_TYPES" :key="op" :value="op">{{ op }}</a-select-option>
          </a-select>
          <a-input
            v-model:value="filters.keyword"
            :placeholder="t('common.search')"
            allow-clear
            class="toolbar-search"
            @press-enter="load"
          />
          <a-range-picker v-model:value="filters.range" style="width: 240px" @change="load" />
          <a-button type="primary" ghost @click="load">{{ t('common.search') }}</a-button>
          <a-button @click="filters.username = ''; filters.operationType = undefined;
                            filters.keyword = ''; filters.range = undefined; load()">
            {{ t('common.reset') }}
          </a-button>
        </div>
      </div>

      <a-table
        class="mt-12"
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        row-key="logId"
        size="small"
        :scroll="{ x: 1300 }"
        :pagination="{ current: page, pageSize, total, showSizeChanger: true }"
        @change="onTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'operationType'">
            <a-tag :color="typeColor(record.operationType)">{{ record.operationType }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'responseStatus'">
            <a-tag :color="statusColor(record.responseStatus)">
              {{ record.responseStatus ?? '-' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'responseTimeMs'">
            <span class="mono">{{ record.responseTimeMs ?? '-' }} ms</span>
          </template>
          <template v-else-if="column.dataIndex === 'createdAt'">
            <span class="mono text-secondary">{{ record.createdAt ?? '-' }}</span>
          </template>
          <template v-else-if="column.dataIndex === 'actions'">
            <a-button type="link" size="small" @click="openDetail(record)">{{ t('common.detail') }}</a-button>
          </template>
        </template>
      </a-table>
    </div>

    <a-drawer v-model:open="detailOpen" :title="t('sys.audit.operationDesc')" width="560">
      <a-descriptions :column="1" bordered size="small">
        <a-descriptions-item :label="t('sys.audit.user')">
          {{ detail?.username ?? '-' }} ({{ detail?.userId ?? '-' }})
        </a-descriptions-item>
        <a-descriptions-item :label="t('sys.audit.operationType')">
          {{ detail?.operationType }}
        </a-descriptions-item>
        <a-descriptions-item :label="t('sys.audit.requestUrl')">
          <span class="mono wrap">{{ detail?.requestUrl ?? '-' }}</span>
        </a-descriptions-item>
        <a-descriptions-item :label="t('sys.audit.requestIp')">
          {{ detail?.requestIp ?? '-' }}
        </a-descriptions-item>
        <a-descriptions-item :label="t('sys.audit.responseStatus')">
          {{ detail?.responseStatus ?? '-' }}
        </a-descriptions-item>
        <a-descriptions-item :label="t('common.createdAt')">
          <span class="mono">{{ detail?.createdAt ?? '-' }}</span>
        </a-descriptions-item>
      </a-descriptions>

      <h3 class="section-title">{{ t('sys.audit.params') }}</h3>
      <pre class="json-block">{{ JSON.stringify(detail?.requestParams ?? {}, null, 2) }}</pre>
    </a-drawer>
  </div>
</template>

<style scoped>
.stat-by-type {
  align-items: flex-start;
  flex-direction: column;
  gap: 8px;
  justify-content: center;
}

.type-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  margin: 18px 0 8px;
  color: var(--fg-secondary);
}

.json-block {
  margin: 0;
  padding: 12px;
  border-radius: var(--radius);
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--fg-secondary);
  font-size: 12px;
  max-height: 320px;
  overflow: auto;
}

.wrap {
  word-break: break-all;
}
</style>
