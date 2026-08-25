import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { http } from '@/api/http'

describe('OrderPanel', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const fn = vi.fn(async (url: string, init?: RequestInit) => {
      const method = (init?.method ?? 'GET').toUpperCase()
      if (method === 'POST' && url.endsWith('/orders')) {
        const body = { order_id: 'ORD-abc12345', status: 'queued', dag: [], created_at: 1.2 }
        return { ok: true, status: 202, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
      }
      if (url.includes('/orders/')) {
        const body = { order_id: 'ORD-abc12345', status: 'queued', dag: [], created_at: 1.2 }
        return { ok: true, status: 200, json: async () => body, text: async () => JSON.stringify(body) } as unknown as Response
      }
      return { ok: true, status: 200, json: async () => ({}), text: async () => '{}' } as unknown as Response
    })
    ;(http as unknown as { fetchFn: typeof fetch }).fetchFn = fn as unknown as typeof fetch
  })

  async function mountPanel() {
    const { mount } = await import('@vue/test-utils')
    const { i18n } = await import('@/i18n')
    const { default: OrderPanel } = await import('./OrderPanel.vue')
    return mount(OrderPanel, { props: { scenarioId: 'ecommerce' }, global: { plugins: [i18n] } })
  }

  it('renders the title and a submit button', async () => {
    const wrapper = await mountPanel()
    expect(wrapper.find('.order-panel').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
  })

  it('blocks submit when item ref is empty', async () => {
    const wrapper = await mountPanel()
    const submit = wrapper.find('button[type="submit"]')
    await submit.trigger('submit')
    await new Promise((r) => setTimeout(r, 10))
    // no order should be created
    expect(wrapper.find('.op-err').exists()).toBe(true)
    expect(wrapper.findAll('.op-recent li')).toHaveLength(0)
  })

  it('places an order end-to-end on submit', async () => {
    const wrapper = await mountPanel()
    await wrapper.find('input[type="text"]').setValue('1001')
    await wrapper.find('button[type="submit"]').trigger('submit')
    await new Promise((r) => setTimeout(r, 30))
    expect(wrapper.findAll('.op-recent li')).toHaveLength(1)
    expect(wrapper.text()).toContain('ORD-abc12345')
  })
})
