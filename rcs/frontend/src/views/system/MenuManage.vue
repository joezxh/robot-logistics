<script setup lang="ts">
// Menu management.
//
// Menus carry a JSONB `i18n` map holding one title per supported locale. The
// editor exposes four inputs (简 / 繁 / EN / 日); `name` is kept as the
// fallback rendered whenever a locale key is missing.
import { computed, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import * as api from '@/api/sysMenus'
import { useAppStore } from '@/stores/app'
import { LOCALE_LABELS, SUPPORTED_LOCALES, localise } from '@/i18n'
import { COMMON_ICONS, resolveIcon } from '@/utils/icons'
import type { AppLocale, I18nMap, MenuNode, MenuPayload, MenuType } from '@/types'

const { t } = useI18n()
const app = useAppStore()

// --- table -----------------------------------------------------------------
const rows = ref<MenuNode[]>([])
const flat = ref<MenuNode[]>([])
const parents = ref<Array<{ id: number; parentId: number | null; name: string }>>([])
const loading = ref(false)
const keyword = ref('')
const typeFilter = ref<MenuType | undefined>(undefined)

async function load() {
  loading.value = true
  try {
    const [tree, simple] = await Promise.all([
      api.listMenuTree({ name: keyword.value || undefined, type: typeFilter.value }),
      api.listMenuSimple(),
    ])
    rows.value = tree?.data ?? []
    flat.value = flatten(rows.value)
    parents.value = (simple?.data ?? []).map((m) => ({ id: m.id, parentId: m.parentId ?? null, name: m.name }))
  } finally {
    loading.value = false
  }
}

function flatten(nodes: MenuNode[], out: MenuNode[] = []): MenuNode[] {
  for (const n of nodes) {
    out.push(n)
    if (n.children?.length) flatten(n.children, out)
  }
  return out
}

onMounted(load)

const columns = computed(() => [
  { title: t('sys.menu.menuName'), dataIndex: 'name', width: 220 },
  { title: t('sys.menu.menuType'), dataIndex: 'type', width: 90 },
  { title: t('sys.menu.permission'), dataIndex: 'permission', width: 200 },
  { title: t('sys.menu.routePath'), dataIndex: 'path', width: 170 },
  { title: t('sys.menu.component'), dataIndex: 'component', width: 220 },
  { title: t('sys.menu.icon'), dataIndex: 'icon', width: 70 },
  { title: t('common.sortOrder'), dataIndex: 'sort', width: 70 },
  { title: t('common.status'), dataIndex: 'status', width: 90 },
  { title: t('common.actions'), dataIndex: 'actions', width: 210, fixed: 'right' },
])

function typeLabel(type: MenuType): string {
  if (type === 1) return t('sys.menu.typeDirectory')
  if (type === 3) return t('sys.menu.typeButton')
  return t('sys.menu.typePage')
}

function typeColor(type: MenuType): string {
  return type === 1 ? 'blue' : type === 3 ? 'purple' : 'cyan'
}

// --- create / edit ---------------------------------------------------------
const modalOpen = ref(false)
const editing = ref<MenuNode | null>(null)
const saving = ref(false)

const form = reactive<MenuPayload & { id?: number }>({
  name: '',
  type: 2,
  parentId: 0,
  permission: '',
  path: '',
  component: '',
  componentName: '',
  icon: '',
  sort: 0,
  status: 0,
  visible: 1,
  keepAlive: 0,
  alwaysShow: 0,
})

/** Per-locale titles edited as a flat record. */
const i18nForm = reactive<Record<AppLocale, string>>({
  'zh-CN': '', 'zh-TW': '', 'en-US': '', 'ja-JP': '',
})

function resetForm() {
  Object.assign(form, {
    name: '', type: 2, parentId: 0, permission: '', path: '', component: '',
    componentName: '', icon: '', sort: 0, status: 0, visible: 1,
    keepAlive: 0, alwaysShow: 0, id: undefined,
  })
  for (const loc of SUPPORTED_LOCALES) i18nForm[loc] = ''
}

function openCreate(parent?: MenuNode) {
  editing.value = null
  resetForm()
  form.parentId = parent?.id ?? 0
  form.type = parent ? 2 : 1
  modalOpen.value = true
}

function openEdit(row: MenuNode) {
  editing.value = row
  resetForm()
  Object.assign(form, {
    id: row.id,
    name: row.name,
    type: row.type,
    parentId: row.parentId ?? 0,
    permission: row.permission ?? '',
    path: row.path ?? '',
    component: row.component ?? '',
    componentName: row.componentName ?? '',
    icon: row.icon ?? '',
    sort: row.sort,
    status: row.status,
    visible: row.visible,
    keepAlive: row.keepAlive,
    alwaysShow: row.alwaysShow,
  })
  const map = (row.i18n ?? {}) as I18nMap
  for (const loc of SUPPORTED_LOCALES) i18nForm[loc] = map[loc] ?? ''
  modalOpen.value = true
}

async function submit() {
  if (!form.name) {
    message.warning(t('common.required'))
    return
  }
  // Drop empty translations so the stored JSONB stays minimal.
  const i18n: I18nMap = {}
  for (const loc of SUPPORTED_LOCALES) {
    const value = i18nForm[loc]?.trim()
    if (value) i18n[loc] = value
  }

  const payload: MenuPayload = {
    name: form.name,
    i18n,
    type: form.type,
    parentId: form.parentId ?? 0,
    permission: form.permission || null,
    path: form.path || null,
    component: form.component || null,
    componentName: form.componentName || null,
    icon: form.icon || null,
    sort: form.sort,
    status: form.status,
    visible: form.visible,
    keepAlive: form.keepAlive,
    alwaysShow: form.alwaysShow,
  }

  saving.value = true
  try {
    if (editing.value) await api.updateMenu(editing.value.id, payload)
    else await api.createMenu(payload)
    message.success(t('common.success'))
    modalOpen.value = false
    // The sidebar is derived from this data — force the shell to re-read it.
    app.bumpPermissions()
    await load()
  } finally {
    saving.value = false
  }
}

async function remove(row: MenuNode) {
  await api.deleteMenu(row.id)
  message.success(t('common.success'))
  app.bumpPermissions()
  await load()
}

/** Case-insensitive search over the parent-menu labels. */
function filterParent(input: string, option: { label?: unknown; value?: unknown }): boolean {
  return String(option?.label ?? '').toLowerCase().includes(input.trim().toLowerCase())
}

/** Parent options exclude the node being edited and its descendants. */
const parentOptions = computed(() => {
  const excluded = new Set<number>()
  if (editing.value) {
    const stack = [editing.value]
    while (stack.length) {
      const node = stack.pop()!
      excluded.add(node.id)
      node.children?.forEach((c) => stack.push(c))
    }
  }
  return [
    { label: t('sys.menu.topLevel'), value: 0 },
    ...parents.value
      .filter((p) => !excluded.has(p.id))
      .map((p) => ({ label: p.name, value: p.id })),
  ]
})
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">{{ t('sys.menu.title') }}</h2>
        <p class="page-subtitle">{{ t('common.total') }} {{ flat.length }}</p>
      </div>
      <a-space>
        <a-button type="primary" @click="openCreate()">{{ t('common.add') }}</a-button>
        <a-button @click="load">{{ t('admin.devices.refresh') }}</a-button>
      </a-space>
    </div>

    <div class="panel">
      <div class="toolbar">
        <a-input
          v-model:value="keyword"
          :placeholder="t('sys.menu.menuName')"
          allow-clear
          style="width: 200px"
          @press-enter="load"
        />
        <a-select
          v-model:value="typeFilter"
          :placeholder="t('sys.menu.menuType')"
          allow-clear
          style="width: 130px"
          @change="load"
        >
          <a-select-option :value="1">{{ t('sys.menu.typeDirectory') }}</a-select-option>
          <a-select-option :value="2">{{ t('sys.menu.typePage') }}</a-select-option>
          <a-select-option :value="3">{{ t('sys.menu.typeButton') }}</a-select-option>
        </a-select>
        <a-button type="primary" ghost @click="load">{{ t('common.search') }}</a-button>
        <a-button @click="keyword = ''; typeFilter = undefined; load()">{{ t('common.reset') }}</a-button>
      </div>

      <a-table
        class="mt-12"
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        row-key="id"
        size="small"
        :scroll="{ x: 1300 }"
        :pagination="false"
        default-expand-all-rows
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'name'">
            <span>{{ localise(record.i18n, record.name) }}</span>
            <span v-if="record.name !== localise(record.i18n, record.name)" class="fallback text-muted">
              · {{ record.name }}
            </span>
          </template>
          <template v-else-if="column.dataIndex === 'type'">
            <a-tag :color="typeColor(record.type)">{{ typeLabel(record.type) }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'permission'">
            <code class="mono text-secondary">{{ record.permission ?? '-' }}</code>
          </template>
          <template v-else-if="column.dataIndex === 'component'">
            <code class="mono text-secondary">{{ record.component ?? '-' }}</code>
          </template>
          <template v-else-if="column.dataIndex === 'icon'">
            <component :is="resolveIcon(record.icon)" v-if="record.icon" />
            <span v-else class="text-muted">-</span>
          </template>
          <template v-else-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 0 ? 'green' : 'red'">
              {{ record.status === 0 ? t('common.enabled') : t('common.disabled') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'actions'">
            <a-space :size="4">
              <a-button type="link" size="small" @click="openEdit(record)">{{ t('common.edit') }}</a-button>
              <a-button
                v-if="record.type !== 3"
                type="link"
                size="small"
                @click="openCreate(record)"
              >
                {{ t('sys.menu.createChild') }}
              </a-button>
              <a-popconfirm :title="t('common.deleteConfirm')" @confirm="remove(record)">
                <a-button type="link" size="small" danger>{{ t('common.delete') }}</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <a-modal
      v-model:open="modalOpen"
      :title="editing ? t('sys.menu.edit') : t('sys.menu.create')"
      width="720px"
      :confirm-loading="saving"
      @ok="submit"
    >
      <a-tabs>
        <a-tab-pane key="basic" :tab="t('sys.profile.basic')">
          <a-form layout="vertical">
            <div class="row">
              <a-form-item :label="t('sys.menu.menuName')" required class="flex-1">
                <a-input v-model:value="form.name" />
              </a-form-item>
              <a-form-item :label="t('sys.menu.menuType')" class="flex-1">
                <a-select v-model:value="form.type">
                  <a-select-option :value="1">{{ t('sys.menu.typeDirectory') }}</a-select-option>
                  <a-select-option :value="2">{{ t('sys.menu.typePage') }}</a-select-option>
                  <a-select-option :value="3">{{ t('sys.menu.typeButton') }}</a-select-option>
                </a-select>
              </a-form-item>
            </div>

            <div class="row">
              <a-form-item :label="t('sys.menu.parent')" class="flex-1">
                <a-select
                  v-model:value="form.parentId"
                  :options="parentOptions"
                  :filter-option="filterParent"
                  show-search
                />
              </a-form-item>
              <a-form-item :label="t('common.sortOrder')" class="flex-1">
                <a-input-number v-model:value="form.sort" :min="0" class="w-full" />
              </a-form-item>
            </div>

            <a-form-item :label="t('sys.menu.permission')">
              <a-input v-model:value="form.permission" placeholder="sys:user:create" />
            </a-form-item>

            <template v-if="form.type !== 3">
              <div class="row">
                <a-form-item :label="t('sys.menu.routePath')" class="flex-1">
                  <a-input v-model:value="form.path" placeholder="/system/users" />
                </a-form-item>
                <a-form-item :label="t('sys.menu.component')" class="flex-1">
                  <a-input v-model:value="form.component" placeholder="views/system/UserManage.vue" />
                </a-form-item>
              </div>
              <div class="row">
                <a-form-item label="Component Name" class="flex-1">
                  <a-input v-model:value="form.componentName" placeholder="UserManage" />
                </a-form-item>
                <a-form-item :label="t('sys.menu.icon')" class="flex-1">
                  <a-select v-model:value="form.icon" show-search allow-clear
                            :options="COMMON_ICONS.map((i) => ({ label: i, value: i }))">
                    <template #option="{ label }">
                      <component :is="resolveIcon(String(label))" /> {{ label }}
                    </template>
                  </a-select>
                </a-form-item>
              </div>
            </template>

            <a-space :size="20" wrap>
              <a-form-item :label="t('common.status')">
                <a-select v-model:value="form.status" style="width: 110px">
                  <a-select-option :value="0">{{ t('common.enabled') }}</a-select-option>
                  <a-select-option :value="1">{{ t('common.disabled') }}</a-select-option>
                </a-select>
              </a-form-item>
              <a-form-item :label="t('sys.menu.visible')">
                <a-switch :checked="form.visible === 1" @update:checked="form.visible = $event ? 1 : 0" />
              </a-form-item>
              <a-form-item :label="t('sys.menu.keepAlive')">
                <a-switch :checked="form.keepAlive === 1" @update:checked="form.keepAlive = $event ? 1 : 0" />
              </a-form-item>
              <a-form-item :label="t('sys.menu.alwaysShow')">
                <a-switch :checked="form.alwaysShow === 1" @update:checked="form.alwaysShow = $event ? 1 : 0" />
              </a-form-item>
            </a-space>
          </a-form>
        </a-tab-pane>

        <a-tab-pane key="i18n" :tab="t('sys.menu.translations')">
          <a-alert type="info" :message="t('sys.menu.i18nHint')" show-icon class="mb-16" />
          <a-form layout="vertical">
            <a-form-item v-for="loc in SUPPORTED_LOCALES" :key="loc" :label="LOCALE_LABELS[loc]">
              <a-input v-model:value="i18nForm[loc]" :placeholder="form.name" />
            </a-form-item>
          </a-form>
        </a-tab-pane>
      </a-tabs>
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

.fallback {
  font-size: 12px;
  margin-left: 6px;
}

.mb-16 {
  margin-bottom: 16px;
}
</style>
