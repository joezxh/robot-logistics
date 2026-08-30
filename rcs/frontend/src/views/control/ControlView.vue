<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDeviceStore } from '@/stores/devices'
import OrderPanel from '@/components/orders/OrderPanel.vue'
import type { CommandType } from '@/types'

const { t } = useI18n()
const devices = useDeviceStore()
const selectedId = ref<string | null>(null)

const selected = computed(() =>
  selectedId.value ? devices.devices.find((d) => d.device_id === selectedId.value) ?? null : null,
)
const selectedState = computed(() =>
  selectedId.value ? devices.states[selectedId.value] ?? null : null,
)

const commandButtons: { type: CommandType; labelKey: string; danger?: boolean }[] = [
  { type: 'stop', labelKey: 'control.cmdStop' },
  { type: 'home', labelKey: 'control.cmdHome' },
  { type: 'recover', labelKey: 'control.cmdRecover' },
  { type: 'move_j', labelKey: 'control.cmdMoveJ' },
  { type: 'move_l', labelKey: 'control.cmdMoveL' },
]

onMounted(() => {
  devices.loadRegistry().then(() => {
    if (devices.devices.length > 0) selectedId.value = devices.devices[0].device_id
  })
})

async function selectDevice(id: string): Promise<void> {
  selectedId.value = id
  await devices.refreshState(id)
}

async function send(type: CommandType): Promise<void> {
  if (!selectedId.value) return
  await devices.runCommand(selectedId.value, { type })
}
</script>

<template>
  <div class="control-page">
    <header class="cp-head">
      <h2>{{ t('control.title') }}</h2>
      <span class="cp-health" :class="{ on: devices.health.running }">
        {{ t('control.health') }}: {{ devices.health.running ? t('control.running') : t('control.stopped') }}
      </span>
      <a-button type="default" @click="devices.loadRegistry()">{{ t('control.refresh') }}</a-button>
    </header>

    <div class="cp-body">
      <aside class="cp-list">
        <h4>{{ t('control.deviceList') }}</h4>
        <p v-if="devices.error" class="cp-err">{{ t('control.loadError') }}: {{ devices.error }}</p>
        <p v-else-if="devices.devices.length === 0" class="cp-soft">{{ t('control.noDevices') }}</p>
        <ul v-else>
          <li
            v-for="d in devices.devices"
            :key="d.device_id"
            :class="{ active: d.device_id === selectedId }"
            @click="selectDevice(d.device_id)"
          >
            <span class="dl-id">{{ d.device_id }}</span>
            <span class="dl-morph">{{ d.morphology }}</span>
          </li>
        </ul>
      </aside>

      <section class="cp-detail">
        <div v-if="!selected" class="cp-soft">{{ t('control.noDevices') }}</div>
        <div v-else class="cp-card">
          <h3>{{ t('control.selected') }}: {{ selected.device_id }}</h3>
          <dl class="cp-meta">
            <div><dt>{{ t('control.morphology') }}</dt><dd>{{ selected.morphology }}</dd></div>
            <div><dt>{{ t('control.robotType') }}</dt><dd>{{ selected.robot_type ?? t('control.none') }}</dd></div>
            <div><dt>{{ t('control.joints') }}</dt><dd>{{ selected.num_joints }}</dd></div>
            <div><dt>{{ t('control.controlHz') }}</dt><dd>{{ selected.control_hz }}</dd></div>
            <div v-if="selectedState">
              <dt>{{ t('control.mode') }}</dt><dd>{{ selectedState.mode }}</dd>
            </div>
            <div v-if="selectedState">
              <dt>{{ t('control.activeCommand') }}</dt><dd>{{ selectedState.active_command_id ?? t('control.none') }}</dd>
            </div>
            <div v-if="selectedState && selectedState.last_error">
              <dt>{{ t('control.lastError') }}</dt><dd class="err">{{ selectedState.last_error }}</dd>
            </div>
          </dl>

          <h4>{{ t('control.commands') }}</h4>
          <div class="cp-cmds">
            <a-button
              v-for="b in commandButtons"
              :key="b.type"
              :danger="b.danger"
              @click="send(b.type)"
            >
              {{ t(b.labelKey) }}
            </a-button>
            <a-button danger @click="selectedId && devices.estop(selectedId)">
              {{ t('control.estop') }}
            </a-button>
            <a-button @click="selectedId && devices.clearEstop(selectedId)">
              {{ t('control.clearEstop') }}
            </a-button>
          </div>
          <p v-if="devices.lastCommand" class="cp-last">{{ t('control.lastCommand') }}: {{ devices.lastCommand }}</p>
        </div>

        <OrderPanel v-if="selectedId" :scenario-id="null" />
      </section>
    </div>
  </div>
</template>

<style scoped>
.control-page { padding: 16px 20px; height: 100%; display: flex; flex-direction: column; gap: 12px; }
.cp-head { display: flex; align-items: center; gap: 12px; }
.cp-head h2 { margin: 0; font-size: 18px; }
.cp-health { font-size: 12px; color: var(--fg-soft); padding: 2px 8px; border: 1px solid var(--border); border-radius: 12px; }
.cp-health.on { color: var(--ok); border-color: var(--ok); }
.cp-body { flex: 1; display: grid; grid-template-columns: 220px 1fr; gap: 14px; min-height: 0; }
.cp-list { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 12px; overflow: auto; }
.cp-list h4 { margin: 0 0 8px; font-size: 13px; color: var(--fg-soft); }
.cp-list ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.cp-list li { display: flex; flex-direction: column; gap: 2px; padding: 8px; border: 1px solid var(--border); border-radius: 6px; cursor: pointer; }
.cp-list li.active { border-color: var(--accent); background: var(--bg-card-alt); }
.dl-id { font-weight: 600; }
.dl-morph { font-size: 11px; color: var(--fg-soft); }
.cp-detail { overflow: auto; display: flex; flex-direction: column; gap: 14px; }
.cp-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 14px; }
.cp-card h3 { margin: 0 0 10px; font-size: 15px; }
.cp-meta { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 0; }
.cp-meta dt { font-size: 11px; color: var(--fg-soft); }
.cp-meta dd { margin: 0 0 4px; font-size: 13px; }
.cp-meta dd.err { color: var(--err); }
.cp-cmds { display: flex; flex-wrap: wrap; gap: 8px; }
.cp-last { font-size: 12px; color: var(--accent); }
.cp-soft { color: var(--fg-soft); font-size: 13px; }
.cp-err { color: var(--err); font-size: 12px; }
</style>
