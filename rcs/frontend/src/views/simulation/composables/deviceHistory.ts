import { reactive } from 'vue'

export interface DeviceHistoryPoint {
  ts: number
  battery: number
  taskCount: number
}

const MAX_POINTS = 30
const TRACK: Record<string, DeviceHistoryPoint[]> = reactive({})

export const deviceHistory = TRACK

export function recordDeviceSnapshot(deviceId: string, battery: number, taskCount: number): void {
  const arr = TRACK[deviceId] ?? (TRACK[deviceId] = [])
  arr.push({ ts: Date.now(), battery, taskCount })
  if (arr.length > MAX_POINTS) arr.shift()
}

export function deviceSparkline(deviceId: string): number[] {
  return (TRACK[deviceId] ?? []).map((p) => p.battery)
}
