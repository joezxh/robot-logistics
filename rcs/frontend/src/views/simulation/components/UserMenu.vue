<template>
  <div class="user" @click.stop="open = !open" tabindex="0" @blur="open = false">
    <div class="avatar" :class="role">{{ initials }}</div>
    <div class="meta">
      <div class="name">{{ username }}</div>
      <div class="role">{{ role }}</div>
    </div>
    <div v-if="open" class="menu" @click.stop>
      <button class="menu-item" @click="onLogout">退出</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { info } from '../composables/toast'

// Session comes from the RCS auth store. Inside the console the user is always
// authenticated (the router guard enforces it), so there is no "log in" branch
// and no mock role assignment — the old `composables/auth.ts` accepted any
// non-empty credentials and derived the role from a username prefix.
const auth = useAuthStore()
const open = ref(false)

const username = computed(() => auth.profile?.username ?? '—')
const role = computed(() => auth.roles[0] ?? 'operator')
const initials = computed(() => username.value.slice(0, 2).toUpperCase())

async function onLogout() {
  open.value = false
  await auth.logout()
  info('已退出')
}
</script>

<style scoped>
.user {
  position: relative;
  display: flex;
  gap: 8px;
  align-items: center;
  padding: 4px 10px 4px 4px;
  background: var(--bg-card-alt);
  border: 1px solid var(--border);
  border-radius: 24px;
  cursor: pointer;
  outline: none;
}
.user:focus { border-color: var(--accent); }
.avatar {
  width: 28px; height: 28px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700; color: white;
  background: var(--accent);
}
.avatar.engineer { background: #2a72d8; }
.avatar.admin { background: #c0392b; }
.avatar.operator { background: var(--good); }
.meta { display: flex; flex-direction: column; gap: 0; line-height: 1.1; }
.name { font-size: 12px; color: var(--fg); font-weight: 600; }
.role { font-size: 10px; color: var(--fg-soft); text-transform: uppercase; letter-spacing: 0.5px; }
.menu {
  position: absolute; top: calc(100% + 6px); right: 0;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 8px; padding: 6px; min-width: 200px;
  box-shadow: 0 12px 32px rgba(0,0,0,0.4);
  z-index: 100;
}
.menu-item {
  width: 100%; text-align: left; background: transparent;
  border: none; padding: 8px 10px; color: var(--fg);
  cursor: pointer; font-size: 13px; border-radius: 4px;
}
.menu-item:hover { background: var(--bg-hover); }
.menu-hint { padding: 4px 10px; font-size: 10px; color: var(--fg-soft); border-top: 1px solid var(--border); margin-top: 4px; }
</style>
