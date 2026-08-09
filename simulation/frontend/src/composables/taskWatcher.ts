import { reactive } from 'vue'
import { info, success, error as toastError } from './toast'
import axios from 'axios'

interface TaskSummary {
  task_id: string
  status: string
}

const LAST: Record<string, string> = reactive({})
let lastSnapshot: Record<string, string> = {}
let timer: number | undefined

async function snapshot(): Promise<Record<string, string>> {
  try {
    const res = await axios.get<TaskSummary[]>('/api/tasks')
    const next: Record<string, string> = {}
    for (const t of res.data) next[t.task_id] = t.status
    return next
  } catch {
    return lastSnapshot
  }
}

export async function checkAndNotify(): Promise<void> {
  const prev = lastSnapshot
  const next = await snapshot()
  for (const id of Object.keys(next)) {
    const s = next[id]
    const p = prev[id]
    if (p && p !== s) {
      if (s === 'completed') success(`任务完成`, id.slice(0, 12))
      else if (s === 'failed') toastError(`任务失败`, id.slice(0, 12))
      else if (s === 'reverted') info(`任务回滚`, id.slice(0, 12))
      else if (s === 'running' && p === 'pending') info(`任务开始`, id.slice(0, 12))
    }
  }
  for (const id of Object.keys(prev)) {
    if (!(id in next)) info(`任务移除`, id.slice(0, 12))
  }
  lastSnapshot = next
  for (const id of Object.keys(LAST)) delete LAST[id]
  for (const id of Object.keys(next)) LAST[id] = next[id]
}

export function startTaskWatcher(intervalMs = 3000): () => void {
  if (timer) return () => stopTaskWatcher()
  // Prime snapshot before scheduling to avoid spurious first transitions.
  snapshot().then((s) => { lastSnapshot = s })
  timer = window.setInterval(checkAndNotify, intervalMs)
  return stopTaskWatcher
}

export function stopTaskWatcher(): void {
  if (timer) {
    clearInterval(timer)
    timer = undefined
  }
}
