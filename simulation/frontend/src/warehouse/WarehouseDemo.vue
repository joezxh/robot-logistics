<template>
  <div class="warehouse-demo">
    <div class="demo-header">
      <h1>{{ t.title }}</h1>
      <p>{{ t.description }}</p>
      <div class="demo-actions">
        <button class="btn-primary" @click="generateData" :disabled="loading">
          {{ loading ? t.generating : t.generate }}
        </button>
        <button class="btn-secondary" @click="navigateToWarehouse">
          {{ t.open_3d }}
        </button>
      </div>
    </div>

    <div class="demo-status" v-if="status">
      <div class="status-item">
        <span class="status-label">{{ t.groups }}:</span>
        <span class="status-value">{{ status.groups }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">{{ t.slots }}:</span>
        <span class="status-value">{{ status.slots }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { generateDemoData } from '../api/warehouse'

const router = useRouter()
const loading = ref(false)
const status = ref<{ groups: number; slots: number } | null>(null)

const t = {
  get title() { return 'Warehouse 3D Demo' },
  get description() { return '3D warehouse visualization with rack zones, AGV navigation, and logistics tracking.' },
  get generate() { return 'Generate Demo Data' },
  get generating() { return 'Generating...' },
  get open_3d() { return 'Open 3D View' },
  get groups() { return 'Groups' },
  get slots() { return 'Slots' },
}

async function generateData() {
  loading.value = true
  try {
    const result = await generateDemoData()
    status.value = { groups: result.groups, slots: result.slots }
  } catch (e) {
    console.error('Failed to generate demo data:', e)
  } finally {
    loading.value = false
  }
}

function navigateToWarehouse() {
  router.push('/warehouse')
}
</script>

<style scoped>
.warehouse-demo {
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
}

.demo-header {
  text-align: center;
  margin-bottom: 32px;
}

.demo-header h1 {
  font-size: 28px;
  margin: 0 0 12px;
}

.demo-header p {
  color: var(--fg-soft);
  margin: 0 0 24px;
}

.demo-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-primary {
  height: 40px;
  padding: 0 24px;
  border-radius: 8px;
  border: none;
  background: var(--accent);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  height: 40px;
  padding: 0 24px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--fg);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.demo-status {
  display: flex;
  gap: 24px;
  justify-content: center;
  padding: 16px;
  background: var(--bg-card);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.status-item {
  display: flex;
  gap: 8px;
}

.status-label {
  color: var(--fg-soft);
}

.status-value {
  font-weight: 600;
}
</style>
