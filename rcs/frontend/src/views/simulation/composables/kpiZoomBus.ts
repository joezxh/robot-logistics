import { ref } from 'vue'

const open = ref(false)
const label = ref('')
const metricKey = ref<string>('')
const range = ref<'30m' | '2h' | 'all'>('30m')

export function openKpiZoom(key: string, lbl: string): void {
  metricKey.value = key
  label.value = lbl
  open.value = true
}

export function closeKpiZoom(): void {
  open.value = false
}

export const kpiZoomState = {
  open,
  label,
  metricKey,
  range,
}
