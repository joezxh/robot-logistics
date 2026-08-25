<template>
  <div class="admin-view">
    <h2>设备列表</h2>
    <button @click="store.load()" :disabled="store.loading">刷新</button>
    <table class="grid" v-if="store.devices.length">
      <thead>
        <tr>
          <th>ID</th><th>形态</th><th>关节</th><th>Hz</th><th>状态</th><th>更新</th><th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="d in store.devices" :key="d.device_id"
            :class="{ active: store.selectedId === d.device_id }"
            @click="store.selectedId = d.device_id">
          <td>{{ d.device_id }}</td>
          <td>{{ d.morphology }}</td>
          <td>{{ d.num_joints }}</td>
          <td>{{ d.control_hz }}</td>
          <td>{{ d.status }}</td>
          <td>{{ d.updated_at || '-' }}</td>
          <td>
            <button @click.stop="remove(d.device_id)">删</button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-else>暂无设备。启动后端会从 registry 种子化默认设备。</p>

    <div v-if="selected" class="detail">
      <h3>参数编辑 — {{ selected.device_id }}</h3>
      <label>状态</label>
      <select v-model="draft.status">
        <option v-for="s in ['registered', 'online', 'offline', 'error']" :key="s" :value="s">{{ s }}</option>
      </select>
      <label>控制模式 (mode)</label>
      <input v-model="draft.mode" placeholder="idle / auto / manual" />
      <label>Limits JSON</label>
      <textarea v-model="limitsText" rows="6"></textarea>
      <label>Home joints (JSON)</label>
      <textarea v-model="homeText" rows="2"></textarea>
      <button @click="save" :disabled="saving">保存</button>
      <span v-if="msg" class="msg">{{ msg }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useAdminDeviceStore } from '@/stores/adminDevices'
import type { DeviceRow } from '@/types'

const store = useAdminDeviceStore()
onMounted(() => store.load())

const selected = computed<DeviceRow | undefined>(() =>
  store.devices.find(d => d.device_id === store.selectedId) || undefined,
)
const draft = ref<{ status: string; mode: string }>({ status: 'registered', mode: '' })
const limitsText = ref('[]')
const homeText = ref('[]')
const saving = ref(false)
const msg = ref('')

watch(selected, (d) => {
  if (d) {
    draft.value = { status: d.status, mode: d.mode || '' }
    limitsText.value = JSON.stringify(d.limits ?? {}, null, 2)
    homeText.value = JSON.stringify(d.home_joints ?? [], null, 2)
    msg.value = ''
  }
}, { immediate: true })

async function save() {
  if (!selected.value) return
  saving.value = true
  try {
    let limits: Record<string, number[]> = {}
    let home: number[] = []
    try { limits = JSON.parse(limitsText.value) } catch { msg.value = 'limits JSON 格式错误'; return }
    try { home = JSON.parse(homeText.value) } catch { msg.value = 'home_joints JSON 格式错误'; return }
    await store.save(selected.value.device_id, {
      status: draft.value.status,
      mode: draft.value.mode || null,
      limits,
      home_joints: home,
    })
    msg.value = '已保存'
  } catch (e) {
    msg.value = '失败: ' + (e as Error).message
  } finally {
    saving.value = false
  }
}

async function remove(id: string) {
  if (!confirm(`删除 ${id}?`)) return
  await store.remove(id)
  if (store.selectedId === id) store.selectedId = null
}
</script>

<style scoped>
.admin-view { padding: 16px; }
.grid { width: 100%; border-collapse: collapse; margin-top: 8px; }
.grid th, .grid td { border: 1px solid #ddd; padding: 6px 8px; text-align: left; }
.grid tr.active { background: #f0f7ff; }
.detail { margin-top: 24px; display: flex; flex-direction: column; gap: 6px; max-width: 720px; }
textarea { font-family: monospace; }
.msg { margin-left: 12px; color: #2d8f4e; }
button { padding: 4px 10px; }
</style>