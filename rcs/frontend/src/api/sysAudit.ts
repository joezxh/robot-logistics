// Audit log endpoints (/api/sys/audit-logs).
import { qs, sysHttp } from './sysHttp'
import type { AuditLogRow, AuditStats, Envelope } from '@/types/sys'

export interface AuditLogQuery {
  userId?: number
  username?: string
  operationType?: string
  operationModule?: string
  keyword?: string
  startAt?: string
  endAt?: string
  skip?: number
  limit?: number
}

export const listAuditLogs = (q: AuditLogQuery = {}) =>
  sysHttp.get<Envelope<AuditLogRow[]>>(`/audit-logs${qs(q)}`)

export const fetchAuditStats = () =>
  sysHttp.get<Envelope<AuditStats>>('/audit-logs/stats')

/** `before` omitted => purge everything. */
export const purgeAuditLogs = (before?: string) =>
  sysHttp.delete<Envelope<{ deleted: number }>>(`/audit-logs${qs({ before })}`)
