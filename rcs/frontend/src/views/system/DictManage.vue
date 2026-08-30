<script setup lang="ts">
// Dictionary management: dictionaries on the left table, their items in a
// drawer. Dictionaries feed status tags and select options across the console.
import { computed, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import * as api from '@/api/sysDicts'
import type { DictItemPayload, DictItemRow, DictPayload, DictRow } from '@/types'

const { t } = useI18n()

const rows = ref<DictRow[]>([])
const loading = ref(false)
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const res = await api.listDictionaries({ keyword: keyword.value || undefined })
    rows.value = res?.data ?? []
  } finally {
    loading.value = false
  }
}

onMounted(load)

const columns = computed(() => [
  { title: t('sys.dict.dictCode'), dataIndex: 'dictCode', width: 180 },
  { title: t('sys.dict.dictName'), dataIndex: 'dictName', width: 180 },
  { title: t('sys.dict.dictType'), dataIndex: 'dictType', width: 120 },
  { title: t('common.remark'), dataIndex: 'description' },
  { title: t('common.status'), dataIndex: 'isActive', width: 90 },
  { title: t('common.actions'), dataIndex: 'actions', width: 200, fixed: 'right' },
])

// --- dictionary create / edit ---------------------------------------------
const modalOpen = ref(false)
const editing = ref<DictRow | null>(null)
const saving = ref(false)
const form = reactive<DictPayload>({
  dictCode: '', dictName: '', dictType: 'system', description: '', sortOrder: 0, isActive: true,
})

function openCreate() {
  editing.value = null
  Object.assign(form, { dictCode: '', dictName: '', dictType: 'system', description: '', sortOrder: 0, isActive: true })
  modalOpen.value = true
}

function openEdit(row: DictRow) {
  editing.value = row
  Object.assign(form, {
    dictCode: row.dictCode, dictName: row.dictName, dictType: row.dictType,
    description: row.description ?? '', sortOrder: row.sortOrder, isActive: row.isActive,
  })
  modalOpen.value = true
}

async function submit() {
  if (!form.dictCode || !form.dictName) {
    message.warning(t('common.required'))
    return
  }
  saving.value = true
  try {
    if (editing.value) await api.updateDictionary(editing.value.dictCode, form)
    else await api.createDictionary(form)
    message.success(t('common.success'))
    modalOpen.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function remove(row: DictRow) {
  await api.deleteDictionary(row.dictCode)
  message.success(t('common.success'))
  await load()
}

// --- items drawer ----------------------------------------------------------
const itemsOpen = ref(false)
const itemsTarget = ref<DictRow | null>(null)
const items = ref<DictItemRow[]>([])
const itemsLoading = ref(false)

const itemColumns = computed(() => [
  { title: t('sys.dict.itemCode'), dataIndex: 'itemCode', width: 150 },
  { title: t('sys.dict.itemName'), dataIndex: 'itemName', width: 160 },
  { title: t('sys.dict.itemValue'), dataIndex: 'itemValue', width: 140 },
  { title: t('sys.dict.color'), dataIndex: 'color', width: 100 },
  { title: t('common.sortOrder'), dataIndex: 'sortOrder', width: 80 },
  { title: t('common.status'), dataIndex: 'isActive', width: 90 },
  { title: t('common.actions'), dataIndex: 'actions', width: 130 },
])

async function openItems(row: DictRow) {
  itemsTarget.value = row
  itemsOpen.value = true
  await loadItems()
}

async function loadItems() {
  if (!itemsTarget.value) return
  itemsLoading.value = true
  try {
    const res = await api.listDictItems(itemsTarget.value.dictCode)
    items.value = res?.data ?? []
  } finally {
    itemsLoading.value = false
  }
}

// --- item create / edit ----------------------------------------------------
const itemModalOpen = ref(false)
const itemEditing = ref<DictItemRow | null>(null)
const itemSaving = ref(false)
const itemForm = reactive<DictItemPayload>({
  dictCode: '', itemCode: '', itemName: '', itemValue: '',
  color: '', icon: '', sortOrder: 0, isActive: true, remark: '',
})

const COLOR_OPTIONS = [
  'default', 'blue', 'cyan', 'green', 'gold', 'orange', 'red', 'purple', 'magenta',
]

function openItemCreate() {
  itemEditing.value = null
  Object.assign(itemForm, {
    dictCode: itemsTarget.value?.dictCode ?? '', itemCode: '', itemName: '',
    itemValue: '', color: 'default', icon: '',
    sortOrder: items.value.length, isActive: true, remark: '',
  })
  itemModalOpen.value = true
}

function openItemEdit(row: DictItemRow) {
  itemEditing.value = row
  Object.assign(itemForm, {
    dictCode: row.dictCode, itemCode: row.itemCode, itemName: row.itemName,
    itemValue: row.itemValue ?? '', color: row.color ?? 'default', icon: row.icon ?? '',
    sortOrder: row.sortOrder, isActive: row.isActive, remark: row.remark ?? '',
  })
  itemModalOpen.value = true
}

async function submitItem() {
  if (!itemForm.itemCode || !itemForm.itemName) {
    message.warning(t('common.required'))
    return
  }
  itemSaving.value = true
  try {
    if (itemEditing.value) await api.updateDictItem(itemEditing.value.itemId, itemForm)
    else await api.createDictItem(itemForm.dictCode, itemForm)
    message.success(t('common.success'))
    itemModalOpen.value = false
    await loadItems()
    await load()
  } finally {
    itemSaving.value = false
  }
}

async function removeItem(row: DictItemRow) {
  await api.deleteDictItem(row.itemId)
  message.success(t('common.success'))
  await loadItems()
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">{{ t('sys.dict.title') }}</h2>
        <p class="page-subtitle">{{ t('common.total') }} {{ rows.length }}</p>
      </div>
      <a-space>
        <a-button type="primary" @click="openCreate">{{ t('common.add') }}</a-button>
        <a-button @click="load">{{ t('admin.devices.refresh') }}</a-button>
      </a-space>
    </div>

    <div class="panel">
      <div class="toolbar">
        <a-input
          v-model:value="keyword"
          :placeholder="t('common.search')"
          allow-clear
          style="width: 240px"
          @press-enter="load"
        />
        <a-button type="primary" ghost @click="load">{{ t('common.search') }}</a-button>
        <a-button @click="keyword = ''; load()">{{ t('common.reset') }}</a-button>
      </div>

      <a-table
        class="mt-12"
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        row-key="dictId"
        size="small"
        :scroll="{ x: 900 }"
        :pagination="{ pageSize: 10 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'dictCode'">
            <code class="mono">{{ record.dictCode }}</code>
          </template>
          <template v-else-if="column.dataIndex === 'dictType'">
            <a-tag :color="record.dictType === 'system' ? 'blue' : 'green'">{{ record.dictType }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'isActive'">
            <a-tag :color="record.isActive ? 'green' : 'red'">
              {{ record.isActive ? t('common.enabled') : t('common.disabled') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'actions'">
            <a-space :size="4">
              <a-button type="link" size="small" @click="openItems(record)">
                {{ t('sys.dict.manageItems') }}
              </a-button>
              <a-button type="link" size="small" @click="openEdit(record)">{{ t('common.edit') }}</a-button>
              <a-popconfirm :title="t('common.deleteConfirm')" @confirm="remove(record)">
                <a-button type="link" size="small" danger>{{ t('common.delete') }}</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- Dictionary create / edit -->
    <a-modal
      v-model:open="modalOpen"
      :title="editing ? t('sys.dict.edit') : t('sys.dict.create')"
      :confirm-loading="saving"
      @ok="submit"
    >
      <a-form layout="vertical">
        <a-form-item :label="t('sys.dict.dictCode')" required>
          <a-input v-model:value="form.dictCode" :disabled="!!editing" placeholder="user_status" />
        </a-form-item>
        <a-form-item :label="t('sys.dict.dictName')" required>
          <a-input v-model:value="form.dictName" />
        </a-form-item>
        <a-form-item :label="t('sys.dict.dictType')">
          <a-select v-model:value="form.dictType">
            <a-select-option value="system">system</a-select-option>
            <a-select-option value="business">business</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="t('common.remark')">
          <a-textarea v-model:value="form.description" :rows="2" />
        </a-form-item>
        <a-form-item :label="t('common.status')">
          <a-switch v-model:checked="form.isActive" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Items drawer -->
    <a-drawer
      v-model:open="itemsOpen"
      :title="`${t('sys.dict.items')} — ${itemsTarget?.dictName ?? ''}`"
      width="760"
      placement="right"
    >
      <div class="toolbar">
        <a-button type="primary" size="small" @click="openItemCreate">{{ t('common.add') }}</a-button>
        <a-button size="small" @click="loadItems">{{ t('admin.devices.refresh') }}</a-button>
      </div>

      <a-table
        class="mt-12"
        :columns="itemColumns"
        :data-source="items"
        :loading="itemsLoading"
        row-key="itemId"
        size="small"
        :pagination="false"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'color'">
            <a-tag :color="record.color || 'default'">{{ record.color || '-' }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'isActive'">
            <a-tag :color="record.isActive ? 'green' : 'red'">
              {{ record.isActive ? t('common.yes') : t('common.no') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'actions'">
            <a-space :size="4">
              <a-button type="link" size="small" @click="openItemEdit(record)">{{ t('common.edit') }}</a-button>
              <a-popconfirm :title="t('common.deleteConfirm')" @confirm="removeItem(record)">
                <a-button type="link" size="small" danger>{{ t('common.delete') }}</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-drawer>

    <!-- Item create / edit -->
    <a-modal
      v-model:open="itemModalOpen"
      :title="itemEditing ? t('sys.dict.editItem') : t('sys.dict.addItem')"
      :confirm-loading="itemSaving"
      @ok="submitItem"
    >
      <a-form layout="vertical">
        <div class="row">
          <a-form-item :label="t('sys.dict.itemCode')" required class="flex-1">
            <a-input v-model:value="itemForm.itemCode" :disabled="!!itemEditing" />
          </a-form-item>
          <a-form-item :label="t('sys.dict.itemName')" required class="flex-1">
            <a-input v-model:value="itemForm.itemName" />
          </a-form-item>
        </div>
        <div class="row">
          <a-form-item :label="t('sys.dict.itemValue')" class="flex-1">
            <a-input v-model:value="itemForm.itemValue" />
          </a-form-item>
          <a-form-item :label="t('sys.dict.color')" class="flex-1">
            <a-select v-model:value="itemForm.color"
                      :options="COLOR_OPTIONS.map((c) => ({ label: c, value: c }))" />
          </a-form-item>
        </div>
        <div class="row">
          <a-form-item :label="t('common.sortOrder')" class="flex-1">
            <a-input-number v-model:value="itemForm.sortOrder" :min="0" class="w-full" />
          </a-form-item>
          <a-form-item :label="t('common.status')" class="flex-1">
            <a-switch v-model:checked="itemForm.isActive" />
          </a-form-item>
        </div>
        <a-form-item :label="t('common.remark')">
          <a-input v-model:value="itemForm.remark" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  gap: 12px;
}

.flex-1 {
  flex: 1;
  min-width: 0;
}
</style>
