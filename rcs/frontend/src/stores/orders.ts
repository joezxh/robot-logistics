import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  createOrder,
  getOrder,
  type OrderCreateRequest,
  type OrderResponse,
} from '@/api/orders'
import type { ScenarioId } from '@/types'

// The backend's OrderResponse does not echo scenario_id/items/priority, so we
// tag each confirmed order locally to power per-scenario filtering in the UI.
export type TaggedOrder = OrderResponse & {
  scenario_id?: ScenarioId | null
  itemCount?: number
  priority?: number
}

export const useOrderStore = defineStore('orders', () => {
  const orders = ref<TaggedOrder[]>([])
  const submitting = ref(false)
  const error = ref<string | null>(null)

  async function placeOrder(req: OrderCreateRequest): Promise<TaggedOrder> {
    submitting.value = true
    error.value = null
    try {
      const created = await createOrder(req)
      // Round-trip through GET to prove the device/order API persisted it.
      const confirmed = await getOrder(created.order_id)
      const tagged: TaggedOrder = {
        ...confirmed,
        scenario_id: (req.scenario_id ?? null) as TaggedOrder['scenario_id'],
        itemCount: req.items?.length ?? 0,
        priority: req.priority,
      }
      orders.value = [tagged, ...orders.value]
      return tagged
    } catch (e) {
      error.value = (e as Error).message
      throw e
    } finally {
      submitting.value = false
    }
  }

  function recentForScenario(scenarioId: ScenarioId): TaggedOrder[] {
    return orders.value.filter((o) => o.scenario_id === scenarioId)
  }

  function reset(): void {
    orders.value = []
    error.value = null
  }

  return { orders, submitting, error, placeOrder, recentForScenario, reset }
})
