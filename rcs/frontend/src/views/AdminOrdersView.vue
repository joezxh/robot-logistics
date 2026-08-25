<template>
  <div class="admin-view">
    <h2>订单管理 / 监控看板</h2>
    <div class="row">
      <button @click="store.load()" :disabled="store.loading">刷新</button>
      <select v-model="filterStatus" @change="store.load(filterStatus || undefined)">
        <option value="">全部</option>
        <option value="queued">queued</option>
        <option value="running">running</option>
        <option value="done">done</option>
        <option value="failed">failed</option>
        <option value="cancelled">cancelled</option>
      </select>
    </div>
    <table class="grid" v-if="store.orders.length">
      <thead><tr><th>订单ID</th><th>场景</th><th>优先级</th><th>状态</th><th>条目</th><th>任务</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="o in store.orders" :key="o.order_id"
            :class="{ active: store.current?.order_id === o.order_id }"
            @click="store.select(o.order_id)">
          <td>{{ o.order_id }}</td>
          <td>{{ o.scenario_id }}</td>
          <td>{{ o.priority }}</td>
          <td><span :class="`badge ${o.status}`">{{ o.status }}</span></td>
          <td>{{ o.items.length }}</td>
          <td>{{ o.tasks.length }}</td>
          <td>
            <button v-if="o.status === 'queued'" @click.stop="advance(o.order_id, 'running')">启动</button>
            <button v-if="o.status === 'running'" @click.stop="advance(o.order_id, 'done')">完成</button>
            <button v-if="o.status !== 'cancelled' && o.status !== 'done'" @click.stop="advance(o.order_id, 'cancelled')">取消</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>暂无订单。POST /api/rcs/orders 创建。</p>

    <div v-if="store.current" class="tasks-panel">
      <h3>DAG 任务 — {{ store.current.order_id }}</h3>
      <table class="grid">
        <thead><tr><th>节点</th><th>类型</th><th>SLO</th><th>依赖</th><th>状态</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="t in store.tasks" :key="t.node_id">
            <td>{{ t.node_id }}</td>
            <td>{{ t.task_type }}</td>
            <td>{{ t.slo_class }}</td>
            <td>{{ t.depends_on.join(', ') || '-' }}</td>
            <td>{{ t.status }}</td>
            <td>
              <button @click="setTaskDone(t.node_id)">完成</button>
              <button @click="setTaskFail(t.node_id)">失败</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAdminOrderStore } from '@/stores/adminOrders'

const store = useAdminOrderStore()
const filterStatus = ref('')
onMounted(() => store.load())

async function advance(id: string, status: string) {
  await store.advance(id, status)
}
async function setTaskDone(nodeId: string) {
  if (!store.current) return
  await store.setTaskStatus(store.current.order_id, nodeId, 'done')
}
async function setTaskFail(nodeId: string) {
  if (!store.current) return
  await store.setTaskStatus(store.current.order_id, nodeId, 'failed')
}
</script>

<style scoped>
.admin-view { padding: 16px; }
.row { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.grid { width: 100%; border-collapse: collapse; margin-top: 8px; }
.grid th, .grid td { border: 1px solid #ddd; padding: 6px 8px; }
.grid tr.active { background: #f0f7ff; }
.badge { padding: 2px 8px; border-radius: 8px; font-size: 12px; }
.badge.queued { background: #fef3c7; }
.badge.running { background: #dbeafe; }
.badge.done { background: #d1fae5; }
.badge.failed { background: #fee2e2; }
.badge.cancelled { background: #e5e7eb; }
.tasks-panel { margin-top: 24px; }
button { padding: 4px 10px; margin-right: 4px; }
</style>