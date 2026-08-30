<script setup lang="ts">
// Console landing page: platform counters plus the caller's recent activity.
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  BookOutlined,
  MenuOutlined,
  SafetyCertificateOutlined,
  TeamOutlined,
} from '@ant-design/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { fetchDashboardSummary } from '@/api/sysAuth'
import { localise } from '@/i18n'
import { resolveIcon } from '@/utils/icons'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const auth = useAuthStore()
const router = useRouter()

const summary = ref<{
  userCount: number
  roleCount: number
  menuCount: number
  dictCount: number
  activeUserCount: number
  recentOperations: Array<Record<string, unknown>>
} | null>(null)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await fetchDashboardSummary()
    summary.value = res?.data ?? null
  } catch {
    summary.value = null
  } finally {
    loading.value = false
  }
}

onMounted(load)

const stats = computed(() => [
  {
    key: 'users',
    label: t('sys.dashboard.users'),
    value: summary.value?.userCount ?? 0,
    icon: TeamOutlined,
    color: 'var(--accent)',
  },
  {
    key: 'roles',
    label: t('sys.dashboard.roles'),
    value: summary.value?.roleCount ?? 0,
    icon: SafetyCertificateOutlined,
    color: 'var(--accent-2)',
  },
  {
    key: 'menus',
    label: t('sys.dashboard.menus'),
    value: summary.value?.menuCount ?? 0,
    icon: MenuOutlined,
    color: 'var(--info)',
  },
  {
    key: 'dicts',
    label: t('sys.dashboard.dictionaries'),
    value: summary.value?.dictCount ?? 0,
    icon: BookOutlined,
    color: 'var(--ok)',
  },
])

/** Leaf pages granted to the user — rendered as quick-launch tiles. */
const quickLinks = computed(() => {
  const leaves: Array<{ id: number; name: string; i18n: Record<string, string>; icon?: string | null; path?: string | null }> = []
  const walk = (nodes: typeof auth.menus) => {
    for (const node of nodes) {
      if (node.type === 2 && node.path) {
        leaves.push({ id: node.id, name: node.name, i18n: node.i18n ?? {}, icon: node.icon, path: node.path })
      }
      if (node.children?.length) walk(node.children)
    }
  }
  walk(auth.menus)
  return leaves
})

const opColumns = [
  { title: t('sys.audit.operationType'), dataIndex: 'operationType', width: 120 },
  { title: t('sys.audit.operationModule'), dataIndex: 'operationModule', width: 130 },
  { title: t('sys.audit.operationDesc'), dataIndex: 'operationDesc' },
  { title: t('sys.audit.responseStatus'), dataIndex: 'responseStatus', width: 100 },
  { title: t('common.createdAt'), dataIndex: 'createdAt', width: 180 },
]

function statusColor(status?: number | null): string {
  if (status === undefined || status === null) return 'var(--fg-muted)'
  if (status < 300) return 'var(--ok)'
  if (status < 400) return 'var(--warn)'
  return 'var(--err)'
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2 class="page-title">
          {{ t('sys.dashboard.welcome') }}, {{ auth.profile?.realName ?? auth.profile?.username }}
        </h2>
        <p class="page-subtitle">{{ t('sys.dashboard.subtitle') }}</p>
      </div>
      <a-tag v-if="auth.isAdmin" color="cyan">ADMIN</a-tag>
    </div>

    <div class="stat-grid">
      <div v-for="s in stats" :key="s.key" class="stat-card">
        <div class="stat-icon" :style="{ color: s.color }">
          <component :is="s.icon" />
        </div>
        <div>
          <div class="stat-value">{{ s.value }}</div>
          <div class="stat-label">{{ s.label }}</div>
        </div>
      </div>
    </div>

    <div class="panel">
      <h3 class="panel-title">{{ t('sys.dashboard.quickActions') }}</h3>
      <div class="quick-grid">
        <button
          v-for="link in quickLinks"
          :key="link.id"
          class="quick-card"
          type="button"
          @click="router.push(link.path!)"
        >
          <component :is="resolveIcon(link.icon)" class="quick-icon" />
          <span class="quick-label">{{ localise(link.i18n, link.name) }}</span>
        </button>
      </div>
    </div>

    <div class="panel">
      <h3 class="panel-title">{{ t('sys.dashboard.recentOps') }}</h3>
      <a-table
        :columns="opColumns"
        :data-source="summary?.recentOperations ?? []"
        :loading="loading"
        :pagination="false"
        row-key="logId"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'responseStatus'">
            <span :style="{ color: statusColor(record.responseStatus as number) }">
              {{ record.responseStatus ?? '-' }}
            </span>
          </template>
          <template v-else-if="column.dataIndex === 'createdAt'">
            <span class="mono">{{ record.createdAt ?? '-' }}</span>
          </template>
        </template>
        <template #emptyText>
          <span class="text-muted">{{ t('common.noData') }}</span>
        </template>
      </a-table>
    </div>
  </div>
</template>

<style scoped>
.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.quick-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 92px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--bg-elevated);
  color: var(--fg-secondary);
  cursor: pointer;
  transition: all var(--transition);
}

.quick-card:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--bg-hover);
  transform: translateY(-2px);
  box-shadow: var(--glow);
}

.quick-icon {
  font-size: 22px;
}

.quick-label {
  font-size: 13px;
  text-align: center;
  line-height: 1.3;
}
</style>
