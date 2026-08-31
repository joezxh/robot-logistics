import { describe, it, expect, vi } from 'vitest'
import { HttpClient } from '@/api/http'
import { listShells, getShell } from '@/api/topologyShell'
import { createOrder, getOrder } from '@/api/orders'
import { http } from '@/api/http'

function makeFetch(impl: (url: string, init?: RequestInit) => Response) {
  return vi.fn(impl)
}

const okRes = (body: unknown, status = 200): Response =>
  ({ ok: true, status, json: async () => body, text: async () => JSON.stringify(body) }) as unknown as Response

describe('HttpClient', () => {
  it('uses default base /api/rcs and GETs the path', async () => {
    const fetchFn = makeFetch((url) => {
      expect(url).toBe('/api/rcs/topology/shell')
      return okRes([{ site_id: 's1', bounds: { w: 1, d: 1 }, zone_count: 0 }])
    })
    const client = new HttpClient({ fetchFn: fetchFn as unknown as typeof fetch })
    const out = await client.get<unknown>('/topology/shell')
    expect(out).toHaveLength(1)
  })

  it('throws a readable error on non-2xx with JSON detail', async () => {
    const fetchFn = makeFetch(() => ({ ok: false, status: 404, statusText: 'Not Found', json: async () => ({ detail: "x" }) }) as unknown as Response)
    const client = new HttpClient({ fetchFn: fetchFn as unknown as typeof fetch })
    await expect(client.get('/topology/shell/missing')).rejects.toThrow(/HTTP 404/)
  })

  it('honors an injected baseUrl', async () => {
    const fetchFn = makeFetch((url) => {
      expect(url).toBe('http://x/topology/shell')
      return okRes([])
    })
    const client = new HttpClient({ baseUrl: 'http://x', fetchFn: fetchFn as unknown as typeof fetch })
    await client.get('/topology/shell')
  })
})

describe('topologyShell API', () => {
  it('listShells maps GET /topology/shell', async () => {
    const fetchFn = makeFetch((url, init) => {
      expect(url).toBe('/api/rcs/topology/shell')
      expect(init?.method).toBe('GET')
      return okRes([{ site_id: 'a', bounds: { w: 10, d: 20 }, zone_count: 3 }])
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fetchFn as unknown as typeof fetch
    const out = await listShells()
    expect(out[0].site_id).toBe('a')
    expect(out[0].bounds.w).toBe(10)
  })

  it('getShell encodes the site id into the path', async () => {
    const fetchFn = makeFetch((url) => {
      expect(url).toBe('/api/rcs/topology/shell/my%2Fsite')
      return okRes({ bounds: { w: 5, d: 5 }, zones: [] })
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fetchFn as unknown as typeof fetch
    const shell = await getShell('my/site')
    expect(shell.bounds.w).toBe(5)
  })
})

describe('orders API', () => {
  it('createOrder POSTs scenario_id + items and reads 202 body', async () => {
    const fetchFn = makeFetch((url, init) => {
      expect(url).toBe('/api/rcs/orders')
      expect(init?.method).toBe('POST')
      const body = JSON.parse(init!.body as string)
      expect(body.scenario_id).toBe('ecommerce')
      expect(body.items).toHaveLength(1)
      return okRes(
        { order_id: 'ORD-1', status: 'queued', dag: [{ node_id: 'pick', depends_on: [] }], created_at: 1 },
        202,
      )
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fetchFn as unknown as typeof fetch
    const out = await createOrder({ scenario_id: 'ecommerce', items: [{ ref: 'A', quantity: 2 }] })
    expect(out.order_id).toBe('ORD-1')
    expect(out.status).toBe('queued')
  })

  it('getOrder GETs /orders/:id', async () => {
    const fetchFn = makeFetch((url) => {
      expect(url).toBe('/api/rcs/orders/ORD-1')
      return okRes({ order_id: 'ORD-1', status: 'queued', dag: [], created_at: 1 })
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fetchFn as unknown as typeof fetch
    const out = await getOrder('ORD-1')
    expect(out.order_id).toBe('ORD-1')
  })
})
