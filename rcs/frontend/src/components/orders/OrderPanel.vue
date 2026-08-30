<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useOrderStore } from '@/stores/orders'

const props = defineProps<{
  /**
   * Forwarded to the backend as `scenario_id`, which is a free-form string with
   * no allow-list, so a database warehouse template can pass its template key.
   */
  scenarioId: string | null
}>()

const { t } = useI18n()
const orders = useOrderStore()

const ITEM_TYPES = ['SKU', 'BIN', 'PALLET', 'MACHINE', 'PART', 'CONTAINER'] as const

const form = reactive({
  itemRef: '',
  itemRefType: 'SKU' as (typeof ITEM_TYPES)[number],
  quantity: 1,
  priority: 5,
})

const itemError = computed(() => (form.itemRef.trim() ? '' : t('order.emptyItemRef')))

async function submit(): Promise<void> {
  if (itemError.value) return
  try {
    await orders.placeOrder({
      scenario_id: props.scenarioId ?? undefined,
      items: [{ ref: `${form.itemRefType}:${form.itemRef.trim()}`, quantity: Number(form.quantity) }],
      priority: Number(form.priority),
    })
    form.itemRef = ''
    form.quantity = 1
    form.priority = 5
  } catch {
    // error surfaced via store.error
  }
}

function reset(): void {
  orders.reset()
}
</script>

<template>
  <div class="order-panel">
    <header class="op-head">
      <h3>{{ t('order.title') }}</h3>
      <button class="op-clear" type="button" @click="reset">{{ t('order.reset') }}</button>
    </header>

    <form class="op-form" @submit.prevent="submit">
      <label class="op-field">
        <span>{{ t('order.itemRef') }}</span>
        <input v-model="form.itemRef" type="text" :placeholder="t('order.itemRefPlaceholder')" />
        <em v-if="itemError" class="op-err">{{ itemError }}</em>
      </label>

      <label class="op-field">
        <span>{{ t('order.itemRefType') }}</span>
        <select v-model="form.itemRefType">
          <option v-for="it in ITEM_TYPES" :key="it" :value="it">{{ it }}</option>
        </select>
      </label>

      <div class="op-row">
        <label class="op-field">
          <span>{{ t('order.quantity') }}</span>
          <input v-model.number="form.quantity" type="number" min="1" max="9999" />
        </label>
        <label class="op-field">
          <span>{{ t('order.priority') }}</span>
          <input v-model.number="form.priority" type="number" min="1" max="10" />
        </label>
      </div>

      <button class="op-submit" type="submit" :disabled="orders.submitting">
        {{ orders.submitting ? t('order.submitting') : t('order.submit') }}
      </button>
      <p v-if="orders.error" class="op-fail">{{ t('order.failed') }}: {{ orders.error }}</p>
    </form>

    <section class="op-recent">
      <h4>{{ t('order.recent') }}</h4>
      <p v-if="orders.orders.length === 0" class="op-empty">{{ t('order.noRecent') }}</p>
      <ul v-else>
        <li v-for="o in orders.orders" :key="o.order_id">
          <span class="op-oid">{{ t('order.orderPrefix') }} {{ o.order_id.slice(0, 12) }}</span>
          <span class="op-meta">{{ o.itemCount }} item(s) · {{ t('order.priority') }} {{ o.priority }}</span>
          <span class="op-status" :class="{ ok: o.status === 'accepted' || o.status === 'queued' }">{{ t('order.status') }}: {{ o.status }}</span>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.order-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; }
.op-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.op-head h3 { margin: 0; font-size: 15px; }
.op-clear { background: transparent; border: 1px solid var(--border); color: var(--fg-soft); border-radius: 6px; padding: 2px 8px; font-size: 12px; cursor: pointer; }
.op-form { display: flex; flex-direction: column; gap: 8px; }
.op-row { display: flex; gap: 8px; }
.op-row .op-field { flex: 1; }
.op-field { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--fg-soft); }
.op-field input, .op-field select { background: var(--bg); border: 1px solid var(--border); color: var(--fg); border-radius: 6px; padding: 6px 8px; font-size: 13px; }
.op-err { color: var(--err); font-style: normal; font-size: 11px; }
.op-submit { margin-top: 4px; background: var(--accent); color: #06283d; border: none; border-radius: 6px; padding: 8px; font-weight: 600; cursor: pointer; }
.op-submit:disabled { opacity: 0.6; cursor: default; }
.op-fail { color: var(--err); font-size: 12px; margin: 6px 0 0; }
.op-recent { margin-top: 14px; }
.op-recent h4 { margin: 0 0 6px; font-size: 13px; color: var(--fg-soft); }
.op-empty { color: var(--fg-soft); font-size: 12px; }
.op-recent ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.op-recent li { display: flex; flex-direction: column; gap: 2px; background: var(--bg-card-alt); border: 1px solid var(--border); border-radius: 6px; padding: 6px 8px; font-size: 12px; }
.op-oid { font-weight: 600; color: var(--accent); }
.op-meta { color: var(--fg); }
.op-status { color: var(--fg-soft); font-size: 11px; }
.op-status.ok { color: var(--ok); }
</style>
