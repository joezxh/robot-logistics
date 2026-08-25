import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/orders'
import type { OrderRow, OrderTask, OrderItem } from '@/types'

export const useAdminOrderStore = defineStore('admin-orders', () => {
  const orders = ref<OrderRow[]>([])
  const tasks = ref<OrderTask[]>([])
  const current = ref<api.OrderResponse | null>(null)
  const loading = ref(false)

  async function load(status?: string) {
    loading.value = true
    try { orders.value = await api.listOrders(status) } finally { loading.value = false }
  }
  async function select(id: string) {
    const o = await api.getOrder(id)
    current.value = o
    tasks.value = (o && (o.dag as OrderTask[])) || (await api.getOrderTasks(id))
  }
  async function create(body: { scenario_id?: string; priority: number; deadline?: number | null; items: OrderItem[] }) {
    await api.createOrder(body)
    await load()
  }
  async function advance(id: string, status: string) {
    await api.advanceStatus(id, status)
    await load()
  }
  async function setTaskStatus(orderId: string, nodeId: string, status: string) {
    await api.setTaskStatus(orderId, nodeId, status)
    if (current.value?.order_id === orderId) {
      await select(orderId)
    }
  }

  return { orders, tasks, current, loading, load, select, create, advance, setTaskStatus }
})