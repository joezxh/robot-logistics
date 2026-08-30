<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAdminLogStore } from '@/stores/adminLogs'

const { t } = useI18n()
const store = useAdminLogStore()
const tab = ref<'commands' | 'events'>('commands')

function switchTab(t2: 'commands' | 'events') {
  tab.value = t2
  if (t2 === 'commands') store.loadCommands()
  else store.loadEvents()
}

const commandColumns = [
  { title: t('admin.logs.cmdId'), dataIndex: 'cmd_id', width: 140 },
  { title: t('admin.logs.device'), dataIndex: 'device_id', width: 120 },
  { title: t('admin.logs.type'), dataIndex: 'cmd_type', width: 110 },
  { title: t('admin.logs.result'), dataIndex: 'result', width: 90 },
  { title: t('admin.logs.issuedBy'), dataIndex: 'issued_by', width: 120 },
  { title: t('admin.logs.payload'), dataIndex: 'payload' },
  { title: t('common.createdAt'), dataIndex: 'created_at', width: 180 },
]

const eventColumns = [
  { title: t('admin.logs.eventId'), dataIndex: 'event_id', width: 140 },
  { title: t('admin.logs.level'), dataIndex: 'level', width: 90 },
  { title: t('admin.logs.source'), dataIndex: 'source', width: 120 },
  { title: t('admin.logs.message'), dataIndex: 'message' },
  { title: t('admin.logs.meta'), dataIndex: 'meta' },
  { title: t('common.createdAt'), dataIndex: 'created_at', width: 180 },
]

function levelColor(level?: string): string {
  if (level === 'error') return 'red'
  if (level === 'warn') return 'orange'
  return 'blue'
}

onMounted(() => store.loadCommands())
</script>

<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">Logs</span>
        <h1 class="hero-title">{{ t('admin.logs.title') }}</h1>
        <p class="hero-sub">{{ t('admin.logs.subtitle') }}</p>
      </div>
      <div class="hero-actions">
        <a-button
          v-if="tab === 'commands'"
          :loading="store.loading"
          @click="store.loadCommands()"
        >{{ t('common.refresh') }}</a-button>
        <a-button v-else :loading="store.loading" @click="store.loadEvents()">{{ t('common.refresh') }}</a-button>
      </div>
    </header>

    <a-tabs v-model:activeKey="tab" @change="switchTab">
      <a-tab-pane key="commands" :tab="t('admin.logs.commands')">
        <div class="data-panel">
          <div class="panel-head">
            <h3>{{ t('admin.logs.commands') }}</h3>
            <div class="toolbar">
              <a-input
                v-model:value="store.deviceFilter"
                :placeholder="t('admin.logs.devicePlaceholder')"
                allow-clear
                class="toolbar-search"
                @press-enter="store.loadCommands()"
              />
              <a-button type="primary" ghost :loading="store.loading" @click="store.loadCommands()">
                {{ t('common.search') }}
              </a-button>
            </div>
          </div>
          <a-table
            class="mt-12"
            :columns="commandColumns"
            :data-source="store.commands"
            :loading="store.loading"
            row-key="cmd_id"
            size="small"
            :scroll="{ x: 1100 }"
            :pagination="{ pageSize: 15 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'payload'">
                <code class="mono">{{ JSON.stringify(record.payload) }}</code>
              </template>
              <template v-else-if="column.dataIndex === 'issued_by'">
                {{ record.issued_by || '-' }}
              </template>
            </template>
            <template #emptyText>
              <span class="text-muted">{{ t('common.noData') }}</span>
            </template>
          </a-table>
        </div>
      </a-tab-pane>

      <a-tab-pane key="events" :tab="t('admin.logs.events')">
        <div class="data-panel">
          <div class="panel-head">
            <h3>{{ t('admin.logs.events') }}</h3>
            <div class="toolbar">
              <a-select
                v-model:value="store.levelFilter"
                :placeholder="t('admin.logs.level')"
                allow-clear
                style="width: 140px"
                @change="store.loadEvents()"
              >
                <a-select-option value="">{{ t('common.all') }}</a-select-option>
                <a-select-option value="info">info</a-select-option>
                <a-select-option value="warn">warn</a-select-option>
                <a-select-option value="error">error</a-select-option>
              </a-select>
              <a-button type="primary" ghost :loading="store.loading" @click="store.loadEvents()">
                {{ t('common.search') }}
              </a-button>
            </div>
          </div>
          <a-table
            class="mt-12"
            :columns="eventColumns"
            :data-source="store.events"
            :loading="store.loading"
            row-key="event_id"
            size="small"
            :scroll="{ x: 1100 }"
            :pagination="{ pageSize: 15 }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'level'">
                <a-tag :color="levelColor(record.level)">{{ record.level }}</a-tag>
              </template>
              <template v-else-if="column.dataIndex === 'meta'">
                <code class="mono">{{ JSON.stringify(record.meta) }}</code>
              </template>
              <template v-else-if="column.dataIndex === 'source'">
                {{ record.source || '-' }}
              </template>
            </template>
            <template #emptyText>
              <span class="text-muted">{{ t('common.noData') }}</span>
            </template>
          </a-table>
        </div>
      </a-tab-pane>
    </a-tabs>
  </div>
</template>

<style scoped>
.mono {
  font-size: 11px;
  color: var(--fg-secondary);
}
</style>
