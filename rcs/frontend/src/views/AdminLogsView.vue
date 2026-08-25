<template>
  <div class="admin-view">
    <h2>系统日志</h2>
    <div class="tabs">
      <button :class="{ active: tab === 'commands' }" @click="switchTab('commands')">指令</button>
      <button :class="{ active: tab === 'events' }" @click="switchTab('events')">事件</button>
    </div>

    <div v-if="tab === 'commands'" class="panel">
      <div class="row">
        <label>设备 ID: <input v-model="store.deviceFilter" placeholder="agv-01" /></label>
        <button @click="store.loadCommands()" :disabled="store.loading">查询</button>
      </div>
      <table class="grid">
        <thead><tr><th>指令ID</th><th>设备</th><th>类型</th><th>结果</th><th>操作人</th><th>载荷</th><th>时间</th></tr></thead>
        <tbody>
          <tr v-for="c in store.commands" :key="c.cmd_id">
            <td>{{ c.cmd_id }}</td>
            <td>{{ c.device_id }}</td>
            <td>{{ c.cmd_type }}</td>
            <td>{{ c.result }}</td>
            <td>{{ c.issued_by || '-' }}</td>
            <td><code>{{ JSON.stringify(c.payload) }}</code></td>
            <td>{{ c.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="tab === 'events'" class="panel">
      <div class="row">
        <label>级别:
          <select v-model="store.levelFilter">
            <option value="">全部</option>
            <option value="info">info</option>
            <option value="warn">warn</option>
            <option value="error">error</option>
          </select>
        </label>
        <button @click="store.loadEvents()" :disabled="store.loading">查询</button>
      </div>
      <table class="grid">
        <thead><tr><th>事件ID</th><th>级别</th><th>来源</th><th>消息</th><th>元数据</th><th>时间</th></tr></thead>
        <tbody>
          <tr v-for="e in store.events" :key="e.event_id">
            <td>{{ e.event_id }}</td>
            <td><span :class="`lvl ${e.level}`">{{ e.level }}</span></td>
            <td>{{ e.source || '-' }}</td>
            <td>{{ e.message }}</td>
            <td><code>{{ JSON.stringify(e.meta) }}</code></td>
            <td>{{ e.created_at }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAdminLogStore } from '@/stores/adminLogs'

const store = useAdminLogStore()
const tab = ref<'commands' | 'events'>('commands')

function switchTab(t: 'commands' | 'events') {
  tab.value = t
  if (t === 'commands') store.loadCommands()
  else store.loadEvents()
}

onMounted(() => store.loadCommands())
</script>

<style scoped>
.admin-view { padding: 16px; }
.tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.tabs button { padding: 6px 14px; }
.tabs button.active { background: #1f2937; color: #fff; }
.row { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; }
.grid { width: 100%; border-collapse: collapse; }
.grid th, .grid td { border: 1px solid #ddd; padding: 6px 8px; vertical-align: top; }
code { font-size: 11px; }
.lvl { padding: 2px 8px; border-radius: 6px; }
.lvl.info { background: #dbeafe; }
.lvl.warn { background: #fef3c7; }
.lvl.error { background: #fee2e2; }
</style>