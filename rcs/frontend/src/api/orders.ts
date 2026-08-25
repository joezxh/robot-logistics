import { http } from './http'
import type { OrderRow, OrderTask, OrderItem } from '@/types'

// Backwards-compat types (legacy stores/tests import these names).
export interface OrderCreateRequest {
  scenario_id?: string
  items: OrderItem[]
  priority?: number
  deadline?: number | null
}
export interface OrderResponse {
  order_id: string
  status: string
  scenario_id?: string | null
  priority?: number
  items?: OrderItem[]
  dag?: OrderTask[]
  created_at: number
}

export const listOrders = (status?: string) =>
  http.get<OrderRow[]>(`/orders${status ? `?status=${encodeURIComponent(status)}` : ''}`)
export const getOrder = (id: string): Promise<OrderResponse> =>
  http.get<OrderResponse>(`/orders/${encodeURIComponent(id)}`)
export const createOrder = (body: OrderCreateRequest) => http.post<OrderResponse>('/orders', body)
export const advanceStatus = (id: string, status: string) =>
  http.put<{ order_id: string; status: string }>(`/orders/${encodeURIComponent(id)}/status`, { status })
export const getOrderTasks = (id: string) =>
  http.get<OrderTask[]>(`/orders/${encodeURIComponent(id)}/tasks`)
export const setTaskStatus = (id: string, nodeId: string, status: string) =>
  http.put<{ order_id: string; node_id: string; status: string }>(
    `/orders/${encodeURIComponent(id)}/tasks/${encodeURIComponent(nodeId)}/status`,
    { status },
  )