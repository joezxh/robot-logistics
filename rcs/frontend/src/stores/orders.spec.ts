import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { http } from '@/api/http'

function fakeFetch() {
  const calls: { url: string; method: string; body?: unknown }[] = []
  const fn = vi.fn(async (url: string, init?: RequestInit) => {
    const method = (init?.method ?? 'GET').toUpperCase()
    let body: unknown = null
    if (method === 'POST' && url.endsWith('/orders')) {
      const parsed = JSON.parse(init?.body as string)
      body = {
        order_id: 'ORD-test1234',
        status: 'queued',
        dag: [{ node_id: 'pick', depends_on: [] }],
        created_at: 1.23,
      }
      calls.push({ url, method, body: parsed })
      return { ok: true, status: 202, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
    }
    if (method === 'GET' && url.includes('/orders/')) {
      body = { order_id: 'ORD-test1234', status: 'queued', dag: [], created_at: 1.23 }
      return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
    }
    return { ok: true, status: 200, json: async () => ({}), text: async () => '{}' } as unknown as Response
  })
  ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
  return { fn, calls }
}

describe('orders store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('places an order and round-trips via GET', async () => {
    const { calls } = fakeFetch()
    const { useOrderStore } = await import('./orders')
    const store = useOrderStore()

    const res = await store.placeOrder({
      scenario_id: 'ecommerce',
      items: [{ ref: 'SKU:1001', quantity: 3 }],
      priority: 7,
    })

    expect(res.order_id).toBe('ORD-test1234')
    expect(store.orders).toHaveLength(1)
    expect(store.orders[0].scenario_id).toBe('ecommerce')
    expect(store.orders[0].itemCount).toBe(1)
    expect(store.orders[0].priority).toBe(7)
    expect(calls.some((c) => c.url.endsWith('/orders') && c.method === 'POST')).toBe(true)
  })

  it('records error and rethrows on failure', async () => {
    const fn = vi.fn(async () => ({
      ok: false,
      status: 500,
      json: async () => ({ detail: 'boom' }),
      text: async () => 'boom',
    } as unknown as Response))
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
    const { useOrderStore } = await import('./orders')
    const store = useOrderStore()

    await expect(
      store.placeOrder({ scenario_id: 'ecommerce', items: [{ ref: 'SKU:1', quantity: 1 }] }),
    ).rejects.toThrow()
    expect(store.error).not.toBeNull()
    expect(store.orders).toHaveLength(0)
  })

  it('reset clears orders', async () => {
    fakeFetch()
    const { useOrderStore } = await import('./orders')
    const store = useOrderStore()
    await store.placeOrder({ scenario_id: 'ecommerce', items: [{ ref: 'SKU:1', quantity: 1 }] })
    store.reset()
    expect(store.orders).toHaveLength(0)
  })
})
