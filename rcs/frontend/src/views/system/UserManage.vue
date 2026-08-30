<script setup lang="ts">
// User management: list / create / edit / enable / delete, plus role assignment
// and administrator-driven password reset.
import { computed, onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import * as api from '@/api/sysUsers'
import * as roleApi from '@/api/sysRoles'
import type { RoleRow, UserPayload, UserRow, UserUpdatePayload } from '@/types'

const { t } = useI18n()
const auth = useAuthStore()

// --- table state -----------------------------------------------------------
const rows = ref<UserRow[]>([])
const total = ref(0)
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const filters = reactive({ keyword: '', status: undefined as string | undefined })

async function load() {
  loading.value = true
  try {
    const res = await api.listUsers({
      keyword: filters.keyword || undefined,
      status: filters.status,
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
    })
    rows.value = res?.data ?? []
    total.value = res?.total ?? rows.value.length
  } finally {
    loading.value = false
  }
}

onMounted(load)

const columns = computed(() => [
  { title: t('sys.user.username'), dataIndex: 'username', width: 140 },
  { title: t('sys.user.realName'), dataIndex: 'realName', width: 140 },
  { title: t('sys.user.role'), dataIndex: 'roleNames', width: 180 },
  { title: t('sys.user.phone'), dataIndex: 'phone', width: 140 },
  { title: t('sys.user.email'), dataIndex: 'email' },
  { title: t('sys.user.isAdmin'), dataIndex: 'isAdmin', width: 90 },
  { title: t('common.status'), dataIndex: 'status', width: 90 },
  { title: t('sys.user.lastLogin'), dataIndex: 'lastLoginAt', width: 180 },
  { title: t('common.actions'), dataIndex: 'actions', width: 260, fixed: 'right' },
])

function onTableChange(pager: { current?: number; pageSize?: number }) {
  page.value = pager.current ?? 1
  pageSize.value = pager.pageSize ?? 10
  load()
}

// --- roles (for the assignment drawer) -------------------------------------
const roles = ref<RoleRow[]>([])
async function loadRoles() {
  const res = await roleApi.listRoles()
  roles.value = res?.data ?? []
}
onMounted(loadRoles)

// --- create / edit ---------------------------------------------------------
const editing = ref<UserRow | null>(null)
const modalOpen = ref(false)
const saving = ref(false)
const form = reactive<UserPayload & { userId?: number }>({
  username: '',
  password: '',
  realName: '',
  phone: '',
  email: '',
  status: 'active',
  isAdmin: false,
  roleIds: [],
})

function openCreate() {
  editing.value = null
  Object.assign(form, {
    username: '', password: '', realName: '', phone: '', email: '',
    status: 'active', isAdmin: false, roleIds: [], userId: undefined,
  })
  modalOpen.value = true
}

function openEdit(row: UserRow) {
  editing.value = row
  Object.assign(form, {
    username: row.username,
    password: '',
    realName: row.realName,
    phone: row.phone ?? '',
    email: row.email ?? '',
    status: row.status,
    isAdmin: row.isAdmin,
    roleIds: [...row.roleIds],
    userId: row.userId,
  })
  modalOpen.value = true
}

async function submit() {
  if (!form.realName || (!editing.value && (!form.username || !form.password))) {
    message.warning(t('common.required'))
    return
  }
  saving.value = true
  try {
    if (editing.value) {
      const payload: UserUpdatePayload = {
        realName: form.realName,
        phone: form.phone,
        email: form.email,
        status: form.status,
        isAdmin: form.isAdmin,
      }
      await api.updateUser(editing.value.userId, payload)
      await api.assignUserRoles(editing.value.userId, form.roleIds ?? [])
    } else {
      await api.createUser(form)
    }
    message.success(t('common.success'))
    modalOpen.value = false
    await load()
  } finally {
    saving.value = false
  }
}

// --- row actions -----------------------------------------------------------
async function toggleStatus(row: UserRow) {
  if (row.userId === auth.profile?.userId) {
    message.warning(t('sys.user.cannotEditSelf'))
    return
  }
  await api.setUserStatus(row.userId, row.status === 'active' ? 'disabled' : 'active')
  message.success(t('common.success'))
  await load()
}

async function remove(row: UserRow) {
  if (row.userId === auth.profile?.userId) {
    message.warning(t('sys.user.cannotEditSelf'))
    return
  }
  await api.deleteUser(row.userId)
  message.success(t('common.success'))
  await load()
}

// --- password reset --------------------------------------------------------
const pwdOpen = ref(false)
const pwdTarget = ref<UserRow | null>(null)
const newPassword = ref('')

function openReset(row: UserRow) {
  pwdTarget.value = row
  newPassword.value = ''
  pwdOpen.value = true
}

async function submitReset() {
  if (!pwdTarget.value || newPassword.value.length < 6) {
    message.warning(t('common.required'))
    return
  }
  await api.resetUserPassword(pwdTarget.value.userId, newPassword.value)
  message.success(t('common.success'))
  pwdOpen.value = false
}
</script>

<template>
  <div class="app-page">
    <header class="page-hero">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">{{ t('sys.user.title') }}</h1>
        <p class="hero-sub">{{ t('common.total') }} {{ total }}</p>
      </div>
      <div class="hero-actions">
        <a-button type="primary" @click="openCreate">{{ t('common.add') }}</a-button>
        <a-button @click="load">{{ t('admin.devices.refresh') }}</a-button>
      </div>
    </header>

    <div class="data-panel">
      <div class="panel-head">
        <h3>{{ t('sys.user.title') }}</h3>
        <div class="toolbar">
          <a-input
            v-model:value="filters.keyword"
            :placeholder="t('common.search')"
            allow-clear
            class="toolbar-search"
            @press-enter="load"
          />
          <a-select
            v-model:value="filters.status"
            :placeholder="t('common.status')"
            allow-clear
            style="width: 140px"
            @change="load"
          >
            <a-select-option value="active">{{ t('common.enabled') }}</a-select-option>
            <a-select-option value="disabled">{{ t('common.disabled') }}</a-select-option>
          </a-select>
          <a-button type="primary" ghost @click="load">{{ t('common.search') }}</a-button>
          <a-button @click="filters.keyword = ''; filters.status = undefined; load()">
            {{ t('common.reset') }}
          </a-button>
        </div>
      </div>

      <a-table
        class="mt-12"
        :columns="columns"
        :data-source="rows"
        :loading="loading"
        row-key="userId"
        size="small"
        :scroll="{ x: 1180 }"
        :pagination="{ current: page, pageSize, total, showSizeChanger: true }"
        @change="onTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'roleNames'">
            <a-tag v-for="r in record.roleNames" :key="r" color="blue">{{ r }}</a-tag>
            <span v-if="!record.roleNames?.length" class="text-muted">-</span>
          </template>
          <template v-else-if="column.dataIndex === 'isAdmin'">
            <a-tag :color="record.isAdmin ? 'purple' : 'default'">
              {{ record.isAdmin ? t('common.yes') : t('common.no') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 'active' ? 'green' : 'red'">
              {{ record.status === 'active' ? t('common.enabled') : t('common.disabled') }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'lastLoginAt'">
            <span class="mono text-secondary">{{ record.lastLoginAt ?? '-' }}</span>
          </template>
          <template v-else-if="column.dataIndex === 'actions'">
            <a-space :size="4">
              <a-button type="link" size="small" @click="openEdit(record)">{{ t('common.edit') }}</a-button>
              <a-button type="link" size="small" @click="openReset(record)">
                {{ t('sys.user.resetPassword') }}
              </a-button>
              <a-button type="link" size="small" @click="toggleStatus(record)">
                {{ record.status === 'active' ? t('sys.user.disable') : t('sys.user.enable') }}
              </a-button>
              <a-popconfirm :title="t('common.deleteConfirm')" @confirm="remove(record)">
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
      :title="editing ? t('sys.user.edit') : t('sys.user.create')"
      :confirm-loading="saving"
      @ok="submit"
    >
      <a-form layout="vertical">
        <a-form-item :label="t('sys.user.username')" required>
          <a-input v-model:value="form.username" :disabled="!!editing" autocomplete="off" />
        </a-form-item>
        <a-form-item v-if="!editing" :label="t('sys.user.password')" required>
          <a-input-password v-model:value="form.password" autocomplete="new-password" />
        </a-form-item>
        <a-form-item :label="t('sys.user.realName')" required>
          <a-input v-model:value="form.realName" />
        </a-form-item>
        <div class="row">
          <a-form-item :label="t('sys.user.phone')" class="flex-1">
            <a-input v-model:value="form.phone" />
          </a-form-item>
          <a-form-item :label="t('sys.user.email')" class="flex-1">
            <a-input v-model:value="form.email" />
          </a-form-item>
        </div>
        <a-form-item :label="t('sys.user.role')">
          <a-select
            v-model:value="form.roleIds"
            mode="multiple"
            :placeholder="t('sys.user.assignRoles')"
            :options="roles.map((r) => ({ label: `${r.roleName} (${r.roleCode})`, value: r.roleId }))"
          />
        </a-form-item>
        <a-space :size="20">
          <a-form-item :label="t('common.status')">
            <a-select v-model:value="form.status" style="width: 120px">
              <a-select-option value="active">{{ t('common.enabled') }}</a-select-option>
              <a-select-option value="disabled">{{ t('common.disabled') }}</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item :label="t('sys.user.isAdmin')">
            <a-switch v-model:checked="form.isAdmin" />
          </a-form-item>
        </a-space>
      </a-form>
    </a-modal>

    <!-- Password reset -->
    <a-modal
      v-model:open="pwdOpen"
      :title="`${t('sys.user.resetPassword')} — ${pwdTarget?.username ?? ''}`"
      @ok="submitReset"
    >
      <a-form layout="vertical">
        <a-form-item :label="t('sys.user.newPassword')" required>
          <a-input-password v-model:value="newPassword" autocomplete="new-password" />
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
