import { reactive } from 'vue'

export interface KpiSnapshot {
  ts: number
  throughput_per_hour: number
  success_rate: number
  active_tasks: number
  energy_kwh: number
}

interface KpiBus {
  history: KpiSnapshot[]
  maxPoints: number
  push(snapshot: KpiSnapshot): void
}

export const kpiBus: KpiBus = reactive({
  history: [] as KpiSnapshot[],
  maxPoints: 240, // up to ~12 minutes at 3s sampling
  push(snapshot: KpiSnapshot) {
    this.history.push(snapshot)
    if (this.history.length > this.maxPoints) this.history.shift()
  },
}) as KpiBus
