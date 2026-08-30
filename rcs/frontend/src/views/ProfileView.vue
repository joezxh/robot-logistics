<script setup lang="ts">
// Personal information: editable profile fields + password change.
import { computed, reactive, ref } from 'vue'
import { LockOutlined, UserOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { changePassword, updateProfile } from '@/api/sysAuth'
import { useI18n } from 'vue-i18n'
import type { ChangePasswordPayload, UpdateProfilePayload } from '@/types'

const { t } = useI18n()
const auth = useAuthStore()

const profileForm = reactive({
  realName: '',
  phone: '',
  email: '',
  avatar: '',
})

function hydrate() {
  const p = auth.profile
  if (!p) return
  profileForm.realName = p.realName ?? ''
  profileForm.phone = p.phone ?? ''
  profileForm.email = p.email ?? ''
  profileForm.avatar = p.avatar ?? ''
}
hydrate()

const savingProfile = ref(false)

async function onSaveProfile() {
  savingProfile.value = true
  try {
    const payload: UpdateProfilePayload = {
      realName: profileForm.realName,
      phone: profileForm.phone,
      email: profileForm.email,
      avatar: profileForm.avatar,
    }
    const updated = await updateProfile(payload)
    // Refresh the store copy so the header avatar/name updates immediately.
    await auth.loadProfile()
    hydrate()
    void updated
    message.success(t('sys.profile.updated'))
  } finally {
    savingProfile.value = false
  }
}

const pwdForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const savingPwd = ref(false)

const pwdMismatch = computed(
  () => pwdForm.confirmPassword.length > 0 && pwdForm.confirmPassword !== pwdForm.newPassword,
)

async function onChangePassword() {
  if (pwdMismatch.value) {
    message.error(t('sys.profile.passwordMismatch'))
    return
  }
  savingPwd.value = true
  try {
    const payload: ChangePasswordPayload = {
      oldPassword: pwdForm.oldPassword,
      newPassword: pwdForm.newPassword,
    }
    await changePassword(payload)
    pwdForm.oldPassword = ''
    pwdForm.newPassword = ''
    pwdForm.confirmPassword = ''
    message.success(t('sys.profile.passwordUpdated'))
  } finally {
    savingPwd.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">{{ t('sys.profile.title') }}</h2>
        <p class="page-subtitle">{{ auth.profile?.username }}</p>
      </div>
    </div>

    <div class="profile-grid">
      <div class="panel">
        <h3 class="panel-title">
          <UserOutlined />
          {{ t('sys.profile.basic') }}
        </h3>
        <a-form layout="vertical">
          <a-form-item :label="t('sys.profile.username')">
            <a-input :value="auth.profile?.username" disabled />
          </a-form-item>
          <a-form-item :label="t('sys.profile.realName')">
            <a-input v-model:value="profileForm.realName" />
          </a-form-item>
          <div class="row">
            <a-form-item :label="t('sys.profile.phone')" class="flex-1">
              <a-input v-model:value="profileForm.phone" />
            </a-form-item>
            <a-form-item :label="t('sys.profile.email')" class="flex-1">
              <a-input v-model:value="profileForm.email" />
            </a-form-item>
          </div>
          <a-form-item :label="t('sys.profile.avatar')">
            <a-input v-model:value="profileForm.avatar" placeholder="https://…" />
          </a-form-item>
          <a-form-item :label="t('sys.profile.roles')">
            <div class="role-tags">
              <a-tag v-for="r in auth.roles" :key="r" color="cyan">{{ r }}</a-tag>
              <span v-if="!auth.roles.length" class="text-muted">-</span>
            </div>
          </a-form-item>
          <a-button type="primary" :loading="savingProfile" @click="onSaveProfile">
            {{ t('sys.profile.saveProfile') }}
          </a-button>
        </a-form>
      </div>

      <div class="panel">
        <h3 class="panel-title">
          <LockOutlined />
          {{ t('sys.profile.security') }}
        </h3>
        <a-form layout="vertical" @submit.prevent="onChangePassword">
          <a-form-item :label="t('sys.profile.oldPassword')">
            <a-input-password v-model:value="pwdForm.oldPassword" autocomplete="current-password" />
          </a-form-item>
          <a-form-item :label="t('sys.profile.newPassword')">
            <a-input-password v-model:value="pwdForm.newPassword" autocomplete="new-password" />
          </a-form-item>
          <a-form-item
            :label="t('sys.profile.confirmPassword')"
            :validate-status="pwdMismatch ? 'error' : ''"
            :help="pwdMismatch ? t('sys.profile.passwordMismatch') : ''"
          >
            <a-input-password v-model:value="pwdForm.confirmPassword" autocomplete="new-password" />
          </a-form-item>
          <a-button type="primary" :loading="savingPwd" @click="onChangePassword">
            {{ t('sys.profile.changePassword') }}
          </a-button>
        </a-form>

        <a-descriptions :column="1" size="small" bordered class="mt-16">
          <a-descriptions-item :label="t('sys.profile.lastLogin')">
            <span class="mono">{{ auth.profile?.lastLoginAt ?? '-' }}</span>
          </a-descriptions-item>
          <a-descriptions-item :label="t('common.createdAt')">
            <span class="mono">{{ auth.profile?.createdAt ?? '-' }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 16px;
  align-items: start;
}

.row {
  display: flex;
  gap: 12px;
}

.flex-1 {
  flex: 1;
  min-width: 0;
}

.role-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  min-height: 24px;
  align-items: center;
}
</style>
