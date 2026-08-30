import { ref, readonly, type Ref } from 'vue'

export type ToastKind = 'info' | 'success' | 'warning' | 'error'
export interface Toast {
  id: number
  kind: ToastKind
  title: string
  message?: string
  ttlMs: number
  createdAt: number
}

const items: Ref<Toast[]> = ref([])
let seq = 0

export const toasts = readonly(items)

export function pushToast(input: Omit<Toast, 'id' | 'createdAt' | 'ttlMs'> & { ttlMs?: number }): number {
  seq += 1
  const t: Toast = {
    id: seq,
    kind: input.kind,
    title: input.title,
    message: input.message,
    ttlMs: input.ttlMs ?? 3500,
    createdAt: Date.now(),
  }
  items.value = [...items.value, t]
  if (t.ttlMs > 0) {
    setTimeout(() => dismissToast(t.id), t.ttlMs)
  }
  return t.id
}

export function dismissToast(id: number): void {
  items.value = items.value.filter((x) => x.id !== id)
}

export function success(title: string, message?: string): number {
  return pushToast({ kind: 'success', title, message })
}
export function info(title: string, message?: string): number {
  return pushToast({ kind: 'info', title, message })
}
export function warn(title: string, message?: string): number {
  return pushToast({ kind: 'warning', title, message })
}
export function error(title: string, message?: string): number {
  return pushToast({ kind: 'error', title, message })
}
