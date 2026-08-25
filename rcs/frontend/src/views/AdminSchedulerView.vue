<template>
  <div class="admin-view">
    <h2>调度策略配置</h2>
    <div class="row">
      <button @click="store.load()" :disabled="store.loading">刷新</button>
      <button @click="createConfig">新建</button>
    </div>
    <table class="grid" v-if="store.configs.length">
      <thead><tr><th>ID</th><th>名称</th><th>策略</th><th>w1</th><th>w2</th><th>w3</th><th>w4</th><th>激活</th><th>操作</th></tr></thead>
      <tbody>
        <tr v-for="c in store.configs" :key="c.config_id">
          <td>{{ c.config_id }}</td>
          <td>{{ c.name }}</td>
          <td>{{ c.strategy }}</td>
          <td><input type="number" step="0.1" v-model.number="c.weights.w1" /></td>
          <td><input type="number" step="0.1" v-model.number="c.weights.w2" /></td>
          <td><input type="number" step="0.1" v-model.number="c.weights.w3" /></td>
          <td><input type="number" step="0.1" v-model.number="c.weights.w4" /></td>
          <td>
            <span v-if="c.active" class="badge active">ACTIVE</span>
            <button v-else @click="store.activate(c.config_id)">激活</button>
          </td>
          <td>
            <button @click="save(c)">保存</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="store.active">当前激活: <strong>{{ store.active.name }}</strong> ({{ store.active.strategy }})</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAdminSchedulerStore } from '@/stores/adminScheduler'
import type { SchedulerConfig } from '@/types'

const store = useAdminSchedulerStore()
onMounted(() => store.load())

async function save(c: SchedulerConfig) {
  await store.update(c.config_id, { weights: c.weights })
}

async function createConfig() {
  const name = prompt('配置名称?')
  if (!name) return
  await store.create({ name, strategy: 'util-weighted', weights: { w1: 1, w2: 0.5, w3: 0.2, w4: 0.1 } })
}
</script>

<style scoped>
.admin-view { padding: 16px; }
.row { display: flex; gap: 8px; margin-bottom: 8px; }
.grid { width: 100%; border-collapse: collapse; }
.grid th, .grid td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; }
input[type=number] { width: 80px; }
.badge.active { background: #d1fae5; padding: 2px 8px; border-radius: 6px; }
button { padding: 4px 10px; }
</style>