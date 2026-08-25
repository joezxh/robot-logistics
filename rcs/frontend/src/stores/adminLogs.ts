import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/logs'
import type { CommandLogRow, EventLogRow } from '@/types'

export const useAdminLogStore = defineStore('admin-logs', () => {
  const commands = ref<CommandLogRow[]>([])
  const events = ref<EventLogRow[]>([])
  const loading = ref(false)
  const deviceFilter = ref('')
  const levelFilter = ref('')

  async function loadCommands() {
    loading.value = true
    try {
      commands.value = await api.listCommands(deviceFilter.value || undefined)
    } finally { loading.value = false }
  }
  async function loadEvents() {
    loading.value = true
    try {
      events.value = await api.listEvents(levelFilter.value || undefined)
    } finally { loading.value = false }
  }

  return {
    commands, events, loading, deviceFilter, levelFilter,
    loadCommands, loadEvents,
  }
})