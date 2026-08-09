import { ref } from 'vue'
import axios from 'axios'
import { success, error as toastError } from '../composables/toast'

export interface DrawerTask {
  task_id: string
  type: string
  status: string
  description: string
  device_id: string
  priority: number
  progress?: number
  trace_id: string
  created_at: string
}

export interface DrawerLog {
  timestamp: string
  module: string
  message: string
  trace_id: string
  level: string
}

const open = ref(false)
const task = ref<DrawerTask | null>(null)
const events = ref<DrawerLog[]>([])
const busy = ref(false)

export const taskDrawerState = { open, task, events, busy }

export async function openTaskDrawer(taskId: string): Promise<void> {
  open.value = true
  task.value = null
  events.value = []
  try {
    const [tasksRes, logsRes] = await Promise.all([
      axios.get<DrawerTask[]>('/api/tasks'),
      axios.get<DrawerLog[]>('/api/logs'),
    ])
    const found = tasksRes.data.find((t) => t.task_id === taskId) ?? null
    task.value = found
    if (found) {
      events.value = logsRes.data.filter((l) => l.trace_id === found.trace_id).reverse()
    }
  } catch (e) {
    toastError('failed to load task', (e as Error).message)
  }
}

export function closeTaskDrawer(): void {
  open.value = false
  task.value = null
  events.value = []
}
