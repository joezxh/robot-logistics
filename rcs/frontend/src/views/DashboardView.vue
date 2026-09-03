<script setup lang="ts">
// Console landing page: platform counters plus the caller's recent activity.
import { computed, onMounted, ref } from 'vue'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { useRouter } from 'vue-router'
import {
  ApiOutlined,
  FileDoneOutlined,
  GlobalOutlined,
  HomeOutlined,
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
  deviceCount: number
  orderCount: number
  mapCount: number
  warehouseCount: number
  recentOperations: Array<Record<string, unknown>>
} | null>(null)
const loading = ref(false)

// GSAP drives these, so the HUD numbers count up instead of snapping into
// place. Kept as a separate array so the tween never fights with Vue's render.
const displayValues = ref<number[]>([0, 0, 0, 0])
const reduceMotion = ref(false)

async function load() {
  loading.value = true
  try {
    const res = await fetchDashboardSummary()
    summary.value = res?.data ?? null
    animateCounts()
  } catch {
    summary.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  reduceMotion.value =
    window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  load()

  // Scroll-reveal: same motion language as RcsLandingView. Every block marked
  // .reveal fades+slides in as it enters the viewport. Honours reduced-motion.
  gsap.registerPlugin(ScrollTrigger)
  const root = document.querySelector('.app-page')
  if (!root) return
  if (reduceMotion.value) {
    root.querySelectorAll('.reveal').forEach((el) => el.classList.add('is-in'))
    return
  }
  root.querySelectorAll('.reveal').forEach((el) => {
    ScrollTrigger.create({
      trigger: el,
      start: 'top 86%',
      once: true,
      onEnter: () => el.classList.add('is-in'),
    })
  })
})

const stats = computed(() => [
  {
    key: 'devices',
    label: t('sys.dashboard.devices'),
    value: summary.value?.deviceCount ?? 0,
    icon: ApiOutlined,
    color: 'var(--accent)',
  },
  {
    key: 'orders',
    label: t('sys.dashboard.orders'),
    value: summary.value?.orderCount ?? 0,
    icon: FileDoneOutlined,
    color: 'var(--accent-2)',
  },
  {
    key: 'maps',
    label: t('sys.dashboard.maps'),
    value: summary.value?.mapCount ?? 0,
    icon: GlobalOutlined,
    color: 'var(--info)',
  },
  {
    key: 'warehouses',
    label: t('sys.dashboard.warehouses'),
    value: summary.value?.warehouseCount ?? 0,
    icon: HomeOutlined,
    color: 'var(--ok)',
  },
])

/**
 * Count the stat values up from zero. Each tile gets its own tween with a small
 * stagger so the row reads as instruments spinning up rather than one
 * synchronised animation.
 */
function animateCounts() {
  stats.value.forEach((s, i) => {
    const target = Number(s.value) || 0
    if (reduceMotion.value) {
      displayValues.value[i] = target
      return
    }
    // Tween a plain proxy object and copy the rounded value across, so Vue only
    // sees whole numbers and never re-renders mid-tween with a fraction.
    const proxy = { v: displayValues.value[i] ?? 0 }
    gsap.to(proxy, {
      v: target,
      duration: 1.1,
      ease: 'power2.out',
      delay: i * 0.08,
      onUpdate: () => {
        displayValues.value[i] = Math.round(proxy.v)
      },
    })
  })
}

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
  <div class="app-page">
    <header class="page-hero reveal">
      <div class="hero-text">
        <span class="hero-kicker">{{ t('common.kicker') }}</span>
        <h1 class="hero-title">
          {{ t('sys.dashboard.welcome') }}, {{ auth.profile?.realName ?? auth.profile?.username }}
        </h1>
        <p class="hero-sub">{{ t('sys.dashboard.subtitle') }}</p>
      </div>
      <div class="hero-actions">
        <a-tag v-if="auth.isAdmin" color="cyan">ADMIN</a-tag>
      </div>
    </header>

    <div class="stat-grid reveal">
      <div v-for="(s, i) in stats" :key="s.key" class="stat-tile clip-notch">
        <span class="stat-label">{{ s.label }}</span>
        <span class="stat-value">{{ displayValues[i] ?? 0 }}</span>
        <span class="stat-ico" :style="{ color: s.color }"><component :is="s.icon" /></span>
      </div>
    </div>

    <div class="data-panel reveal">
      <div class="panel-head">
        <h3>{{ t('sys.dashboard.quickActions') }}</h3>
      </div>
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

    <div class="data-panel reveal">
      <div class="panel-head">
        <h3>{{ t('sys.dashboard.recentOps') }}</h3>
      </div>
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
