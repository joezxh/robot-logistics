<template>
  <Teleport to="body">
    <Transition name="login">
      <div v-if="visible" class="overlay">
        <div class="card" role="dialog" :aria-label="t.title">
          <h2>{{ t.title }}</h2>
          <p class="hint">演示登录 · 任意账号密码均通过，前缀 admin/eng 切换角色。</p>
          <form @submit.prevent="submit">
            <label>
              <span>username</span>
              <input v-model="username" autofocus placeholder="operator / eng.jane / admin.bob" />
            </label>
            <label>
              <span>password</span>
              <input v-model="password" type="password" placeholder="••••••" />
            </label>
            <button type="submit" class="primary">登录</button>
            <p v-if="error" class="error">{{ error }}</p>
            <p class="hint">不需要真后端，纯前端 mock。</p>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from '../i18n'
import { useAuth, login } from '../composables/auth'
import { success } from '../composables/toast'

const { t } = useI18n()
const { isAuthed } = useAuth()
const visible = ref(!isAuthed.value)
const username = ref('operator')
const password = ref('demo')
const error = ref('')

function submit() {
  error.value = ''
  const u = login(username.value.trim(), password.value)
  if (!u) {
    error.value = '请输入账号和密码'
    return
  }
  success(`Welcome, ${u.username}`, `role=${u.role}`)
  visible.value = false
}
</script>

<style scoped>
.overlay {
  position: fixed; inset: 0; z-index: 3000;
  background: radial-gradient(circle at 30% 20%, rgba(94,176,255,0.15), rgba(0,0,0,0.7));
  display: flex; align-items: center; justify-content: center;
}
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px;
  width: min(380px, 92vw);
  box-shadow: 0 30px 80px rgba(0,0,0,0.5);
  color: var(--fg);
}
h2 { margin: 0 0 8px; font-size: 22px; }
.hint { margin: 0 0 18px; font-size: 12px; color: var(--fg-soft); }
form { display: flex; flex-direction: column; gap: 10px; }
label { display: flex; flex-direction: column; gap: 4px; font-size: 11px; color: var(--fg-soft); text-transform: uppercase; letter-spacing: 0.5px; }
input {
  background: var(--bg-sub); color: var(--fg);
  border: 1px solid var(--border); border-radius: 4px;
  padding: 8px 10px; font-size: 14px;
}
input:focus { outline: none; border-color: var(--accent); }
button.primary {
  background: linear-gradient(90deg, var(--accent), var(--accent-soft));
  color: white; border: none; border-radius: 6px; padding: 10px;
  cursor: pointer; font-weight: 600; font-size: 14px; margin-top: 6px;
}
button.primary:hover { filter: brightness(1.1); }
.error { color: var(--bad); font-size: 12px; margin: 0; }
.login-enter-from { opacity: 0; transform: translateY(8px); }
.login-leave-to { opacity: 0; transform: translateY(-8px); }
.login-enter-active, .login-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
</style>
