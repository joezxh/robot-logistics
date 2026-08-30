<script setup lang="ts">
// Role management: CRUD plus menu-permission assignment through a tree of
// checkboxes built from the full menu catalogue.
import { computed, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import * as api from '@/api/sysRoles'
import * as menuApi from '@/api/sysMenus'
import { useAppStore } from '@/stores/app'
import { localise } from '@/i18n'
import type { MenuNode, RolePayload, RoleRow } from '@/types'

const { t } = useI18n()
const app = useAppStore()

// --- table -----------------------------------------------------------------
const rows = ref<RoleRow[]>([])
const loading = ref(false)
const keyword = ref('')

async function load() {
  loading.value = true
  try {
    const res = await api.listRoles(keyword.value || undefined)
    rows.value = res?.data ?? []
  } finally {
    loading.value = false
  }
}

onMounted(load)

const columns = computed(() => [
  { title: t('sys.role.roleName'), dataIndex: 'roleName', width: 160 },
  { title: t('sys.role.roleCode'), dataIndex: 'roleCode', width: 160 },
  { title: t('sys.role.description'), dataIndex: 'description' },
  { title: t('sys.role.menus'), dataIndex: 'menuIds', width: 100 },
  { title: t('common.status'), dataIndex: 'status', width: 90 },
  { title: t('common.actions'), dataIndex: 'actions', width: 240, fixed: 'right' },
])

// --- create / edit ---------------------------------------------------------
const modalOpen = ref(false)
const editing = ref<RoleRow | null>(null)
const saving = ref(false)
const form = reactive<RolePayload>({
  roleName: '',
  roleCode: '',
  description: '',
  sortOrder: 0,
  status: 'active',
})

function openCreate() {
  editing.value = null
  Object.assign(form, { roleName: '', roleCode: '', description: '', sortOrder: 0, status: 'active' })
  modalOpen.value = true
}

function openEdit(row: RoleRow) {
  editing.value = row
  Object.assign(form, {
    roleName: row.roleName,
    roleCode: row.roleCode,
    description: row.description ?? '',
    sortOrder: row.sortOrder,
    status: row.status,
  })
  modalOpen.value = true
}

async function submit() {
  if (!form.roleName || !form.roleCode) {
    message.warning(t('common.required'))
    return
  }
  saving.value = true
  try {
    if (editing.value) await api.updateRole(editing.value.roleId, form)
    else await api.createRole(form)
    message.success(t('common.success'))
    modalOpen.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function remove(row: RoleRow) {
  await api.deleteRole(row.roleId)
  message.success(t('common.success'))
  await load()
}

// --- menu permissions ------------------------------------------------------
const permOpen = ref(false)
const permTarget = ref<RoleRow | null>(null)
const menuTree = ref<MenuNode[]>([])
const checkedIds = ref<number[]>([])
const expandedKeys = ref<number[]>([])
const permSaving = ref(false)

/** AntD tree control needs `{key, title, children}` nodes. */
const treeData = computed(() => toTree(menuTree.value))

function toTree(nodes: MenuNode[]): Array<Record<string, unknown>> {
  return nodes.map((n) => ({
    key: n.id,
    title: localise(n.i18n, n.name),
    children: n.children?.length ? toTree(n.children) : undefined,
  }))
}

function allIds(nodes: MenuNode[]): number[] {
  const ids: number[] = []
  const walk = (list: MenuNode[]) => {
    for (const n of list) {
      ids.push(n.id)
      if (n.children?.length) walk(n.children)
    }
  }
  walk(nodes)
  return ids
}

async function openPermissions(row: RoleRow) {
  permTarget.value = row
  const [tree, granted] = await Promise.all([menuApi.listMenuTree(), api.getRoleMenus(row.roleId)])
  menuTree.value = tree?.data ?? []
  checkedIds.value = granted?.data ?? []
  expandedKeys.value = allIds(menuTree.value)
  permOpen.value = true
}

async function savePermissions() {
  if (!permTarget.value) return
  permSaving.value = true
  try {
    await api.assignRoleMenus(permTarget.value.roleId, checkedIds.value)
    message.success(t('common.success'))
    permOpen.value = false
    // Permission grants changed — views holding cached data should refresh.
    app.bumpPermissions()
    await load()
  } finally {
    permSaving.value = false
  }
}

function toggleAll(checked: boolean) {
  checkedIds.value = checked ? allIds(menuTree.value) : []
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">{{ t('sys.role.title') }}</h2>
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
          style="width: 220px"
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
        row-key="roleId"
        size="small"
        :scroll="{ x: 900 }"
        :pagination="{ pageSize: 10 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'roleCode'">
            <code class="mono">{{ record.roleCode }}</code>
            <a-tag v-if="record.roleCode === 'super_admin'" color="gold" class="ml-8">
              {{ t('sys.role.builtin') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'menuIds'">
            <a-tag color="cyan">{{ record.menuIds?.length ?? 0 }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'red'">
              {{ record.status === 'active' ? t('common.enabled') : t('common.disabled') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'actions'">
            <a-space :size="4">
              <a-button type="link" size="small" @click="openEdit(record)">{{ t('common.edit') }}</a-button>
              <a-button type="link" size="small" @click="openPermissions(record)">
                {{ t('sys.role.assignMenus') }}
              </a-button>
              <a-popconfirm
                v-if="record.roleCode !== 'super_admin'"
                :title="t('common.deleteConfirm')"
                @confirm="remove(record)"
              >
                <a-button type="link" size="small" danger>{{ t('common.delete') }}</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </div>

    <!-- Create / edit -->
    <a-modal
      v-model:open="modalOpen"
      :title="editing ? t('sys.role.edit') : t('sys.role.create')"
      :confirm-loading="saving"
      @ok="submit"
    >
      <a-form layout="vertical">
        <a-form-item :label="t('sys.role.roleName')" required>
          <a-input v-model:value="form.roleName" />
        </a-form-item>
        <a-form-item :label="t('sys.role.roleCode')" required>
          <a-input v-model:value="form.roleCode" :disabled="!!editing" placeholder="e.g. operator" />
        </a-form-item>
        <a-form-item :label="t('sys.role.description')">
          <a-textarea v-model:value="form.description" :rows="3" />
        </a-form-item>
        <a-space :size="20">
          <a-form-item :label="t('common.sortOrder')">
            <a-input-number v-model:value="form.sortOrder" :min="0" />
          </a-form-item>
          <a-form-item :label="t('common.status')">
            <a-select v-model:value="form.status" style="width: 120px">
              <a-select-option value="active">{{ t('common.enabled') }}</a-select-option>
              <a-select-option value="disabled">{{ t('common.disabled') }}</a-select-option>
            </a-select>
          </a-form-item>
        </a-space>
      </a-form>
    </a-modal>

    <!-- Menu permissions -->
    <a-drawer
      v-model:open="permOpen"
      :title="`${t('sys.role.assignMenus')} — ${permTarget?.roleName ?? ''}`"
      width="480"
      placement="right"
    >
      <div class="toolbar">
        <a-button size="small" @click="toggleAll(true)">{{ t('sys.role.selectAll') }}</a-button>
        <a-button size="small" @click="toggleAll(false)">{{ t('sys.role.unselectAll') }}</a-button>
        <span class="spacer" />
        <a-button type="primary" size="small" :loading="permSaving" @click="savePermissions">
          {{ t('common.save') }}
        </a-button>
      </div>

      <a-divider />

      <a-tree
        v-model:checked-keys="checkedIds"
        v-model:expanded-keys="expandedKeys"
        checkable
        :tree-data="treeData"
        :selectable="false"
        default-expand-all
      />
    </a-drawer>
  </div>
</template>

<style scoped>
.spacer {
  flex: 1;
}

.ml-8 {
  margin-left: 8px;
}
</style>
