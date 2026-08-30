<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">{{ t('admin.scheduler.title') }}</h1>
        <p class="hero-sub">{{ t('admin.scheduler.subtitle') }}</p>
      </div>
      <div class="hero-actions">
        <a-button :loading="store.loading" @click="store.load()">
          <template #icon><ReloadOutlined /></template>
          {{ t('common.refresh') }}
        </a-button>
        <a-button type="primary" @click="openCreate">
          <template #icon><PlusOutlined /></template>
          {{ t('admin.scheduler.create') }}
        </a-button>
      </div>
    </header>

    <div class="data-panel">
      <div class="panel-head">
        <h3>
          {{ t('admin.scheduler.title') }}
          <a-tag v-if="store.active" color="green" class="active-tag">
            {{ t('admin.scheduler.active') }}: {{ store.active.name }} ({{ store.active.strategy }})
          </a-tag>
        </h3>
      </div>
      <a-table
        :columns="columns"
        :data-source="store.configs"
        :loading="store.loading"
        :pagination="false"
        row-key="config_id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="weightKeys.includes(column.dataIndex as WeightKey)">
            <a-input-number
              :value="(record as SchedulerConfig).weights[column.dataIndex as WeightKey]"
              :step="0.1"
              size="small"
              style="width: 90px"
              @update:value="(v: number | null) => setWeight(record as SchedulerConfig, column.dataIndex as WeightKey, v)"
            />
          </template>
          <template v-else-if="column.dataIndex === 'active'">
            <a-tag v-if="(record as SchedulerConfig).active" color="green">ACTIVE</a-tag>
            <a-button v-else size="small" type="link" @click="store.activate((record as SchedulerConfig).config_id)">
              {{ t('admin.scheduler.activate') }}
            </a-button>
          </template>
          <template v-else-if="column.dataIndex === 'action'">
            <a-button size="small" type="link" @click="save(record as SchedulerConfig)">
              {{ t('admin.scheduler.save') }}
            </a-button>
          </template>
        </template>
        <template #emptyText>
          <span class="text-muted">{{ t('common.noData') }}</span>
        </template>
      </a-table>
    </div>

    <a-modal
      v-model:open="createOpen"
      :title="t('admin.scheduler.create')"
      :confirm-loading="creating"
      @ok="submitCreate"
    >
      <a-form :model="draft" layout="vertical">
        <a-form-item :label="t('admin.scheduler.name')" required>
          <a-input v-model:value="draft.name" :placeholder="t('admin.scheduler.namePlaceholder')" />
        </a-form-item>
        <a-form-item :label="t('admin.scheduler.strategy')">
          <a-select v-model:value="draft.strategy">
            <a-select-option v-for="s in strategies" :key="s" :value="s">{{ s }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { message } from 'ant-design-vue'
import { PlusOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { useAdminSchedulerStore } from '@/stores/adminScheduler'
import type { SchedulerConfig, SchedulerWeights } from '@/types'

const { t } = useI18n()
const store = useAdminSchedulerStore()
onMounted(() => store.load())

type WeightKey = keyof SchedulerWeights
const weightKeys: WeightKey[] = ['w1', 'w2', 'w3', 'w4']
const strategies = ['util-weighted', 'fifo', 'edf', 'priority']

const columns = [
  { title: 'ID', dataIndex: 'config_id', width: 140 },
  { title: t('admin.scheduler.name'), dataIndex: 'name', width: 160 },
  { title: t('admin.scheduler.strategy'), dataIndex: 'strategy', width: 140 },
  { title: 'w1', dataIndex: 'w1', width: 110 },
  { title: 'w2', dataIndex: 'w2', width: 110 },
  { title: 'w3', dataIndex: 'w3', width: 110 },
  { title: 'w4', dataIndex: 'w4', width: 110 },
  { title: t('admin.scheduler.active'), dataIndex: 'active', width: 110 },
  { title: t('common.actions'), dataIndex: 'action', width: 90, fixed: 'right' as const },
]

const createOpen = ref(false)
const creating = ref(false)
const draft = reactive<{ name: string; strategy: string }>({ name: '', strategy: 'util-weighted' })

function setWeight(row: SchedulerConfig, key: WeightKey, value: number | null): void {
  row.weights[key] = value ?? 0
}

async function save(c: SchedulerConfig) {
  await store.update(c.config_id, { weights: c.weights })
  message.success(t('common.saved'))
}

function openCreate() {
  draft.name = ''
  draft.strategy = 'util-weighted'
  createOpen.value = true
}

async function submitCreate() {
  if (!draft.name.trim()) {
    message.warning(t('common.required'))
    return
  }
  creating.value = true
  try {
    await store.create({
      name: draft.name.trim(),
      strategy: draft.strategy,
      weights: { w1: 1, w2: 0.5, w3: 0.2, w4: 0.1 },
    })
    createOpen.value = false
    message.success(t('common.success'))
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.active-tag { margin-left: 8px; }
</style>
