import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as api from '@/api/planning'
import type { PlanningProfile } from '@/types'

export const useAdminPlanningStore = defineStore('admin-planning', () => {
  const profiles = ref<PlanningProfile[]>([])
  const loading = ref(false)

  async function load() {
    loading.value = true
    try { profiles.value = await api.listProfiles() } finally { loading.value = false }
  }
  async function create(body: { name: string; algo: string; axes: number; vel_max: number[]; acc_max: number[]; created_by?: string }) {
    await api.createProfile(body)
    await load()
  }
  async function remove(id: string) {
    await api.deleteProfile(id)
    await load()
  }

  return { profiles, loading, load, create, remove }
})