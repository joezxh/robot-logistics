<template>
  <div class="card">
    <header class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab"
        :class="{ active: active === tab.id }"
        @click="active = tab.id"
      >
        <span class="icon">{{ tab.icon }}</span>
        <span class="lbl">{{ tab.label }}</span>
      </button>
    </header>
    <div class="body" :class="{ overview: active === 'overview' }">
      <Transition name="fade" mode="out-in">
        <div v-if="active === 'overview'" key="overview" class="overview-stack">
          <DeviceStatus />
          <SiteManager />
          <TaskQueue />
          <KpiPanel />
        </div>
        <TaskCreateForm v-else-if="active === 'create'" key="create" />
        <RollbackPanel v-else-if="active === 'rollback'" key="rollback" />
        <LogViewer v-else key="logs" />
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DeviceStatus from '../dashboard/DeviceStatus.vue'
import SiteManager from '../dashboard/SiteManager.vue'
import TaskQueue from '../dashboard/TaskQueue.vue'
import KpiPanel from '../dashboard/Kpi.vue'
import TaskCreateForm from './TaskCreate.vue'
import RollbackPanel from './Rollback.vue'
import LogViewer from './LogViewer.vue'

const tabs = [
  { id: 'overview', icon: '📊', label: '概览' },
  { id: 'create', icon: '➕', label: '创建' },
  { id: 'rollback', icon: '↶', label: '回滚' },
  { id: 'logs', icon: '📜', label: '日志' },
] as const

const active = ref<typeof tabs[number]['id']>('overview')
</script>

<style scoped>
.card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0;
  display: flex;
  flex-direction: column;
  min-height: 0;
  flex: 1;
}
.tabs {
  display: flex;
  gap: 0;
  padding: 6px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-card-alt);
  border-radius: 8px 8px 0 0;
}
.tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 6px;
  background: transparent;
  border: none;
  border-radius: 6px;
  color: var(--fg-soft);
  font-size: 12px;
  cursor: pointer;
  transition: background 0.18s ease, color 0.18s ease;
}
.tab:hover { background: var(--bg-hover); color: var(--fg); }
.tab.active { background: var(--bg-card); color: var(--fg); font-weight: 600; box-shadow: 0 1px 0 var(--border); }
.tab .icon { font-size: 14px; }
.body {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  min-height: 0;
}
.body.overview { padding: 12px; }
.overview-stack {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.overview-stack > * { min-height: 0; }
.body > * { background: transparent !important; border: none !important; padding: 0 !important; }
.body.overview > .overview-stack { background: transparent !important; border: none !important; padding: 0 !important; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(4px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s ease, transform 0.18s ease; }
</style>
