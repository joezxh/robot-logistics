/**
 * Warehouse Pinia Store
 * Centralized state management for warehouse 3D visualization
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Slot,
  WarehouseGroup,
  ViewMode,
  Language,
  Theme,
  FloorFull,
  LogisticsTask,
  LogisticsStats,
  AGVGrid,
} from '../types'

export const useWarehouseStore = defineStore('warehouse', () => {
  // UI State
  const curView = ref<ViewMode>('3d')
  const lang = ref<Language>('zh')
  const isDark = ref(true)
  const searchQuery = ref('')
  const loading = ref(true)
  const dragActive = ref(false)
  const threeReady = ref(false)
  const sidebarOpen = ref(true)
  const aisleMode = ref(false)
  const aislePickerOpen = ref(false)
  const aisleGaps = ref<{ index: number; label: string; z_center: number; width: number }[]>([])

  // Edit Mode
  const canEdit = ref(false)
  const canView = ref(true)

  // Warehouse Data
  const slots = ref<Slot[]>([])
  const groups = ref<WarehouseGroup[]>([])
  const selGroup = ref<WarehouseGroup | null>(null)
  const floorFull = ref<FloorFull | null>(null)

  // UI Toggles
  const showWalls = ref(true)
  const showMarkings = ref(true)

  // Tooltip
  const ttVisible = ref(false)
  const ttData = ref<any>(null)
  const ttX = ref(0)
  const ttY = ref(0)

  // Detail Panel
  const dpOpen = ref(false)
  const dpData = ref<any>(null)

  // Logistics
  const docks = ref<any[]>([])
  const logisticsTasks = ref<LogisticsTask[]>([])
  const logisticsStats = ref<LogisticsStats>({
    total_inbound: 0,
    total_outbound: 0,
    avg_processing_time: 0,
    dock_utilization: 0,
  })
  const selectedTask = ref<LogisticsTask | null>(null)
  const logisticsOpen = ref(false)
  const logisticsStatsOpen = ref(false)
  const logisticsDateFrom = ref('')
  const logisticsDateTo = ref('')

  // AGV
  const agvOverlay = ref(false)
  const agvOpen = ref(false)
  const agvGrid = ref<AGVGrid | null>(null)
  const agvTool = ref<'walk' | 'block' | 'main' | 'restricted'>('walk')
  const agvCellSize = ref(1.0)

  // Floor Plan Editor
  const fpOpen = ref(false)
  const fpGroup = ref<WarehouseGroup | null>(null)
  const fpAllSlots = ref<Slot[]>([])
  const fpLayer = ref<'paint' | 'zone' | 'wall'>('paint')
  const fpRows = ref<any[]>([])
  const fpShellDraft = ref<any>(null)
  const fpSaveOk = ref(false)
  const fpSaving = ref(false)
  const fpShellErrors = ref<string[]>([])

  // Setup Wizard
  const setupStep = ref(1)
  const setupScan = ref<any>(null)
  const setupMapping = ref<Record<number, string>>({})
  const setupSummary = ref<Record<string, number>>({})
  const setupSaving = ref(false)

  // Warehouse Manage
  const whManageOpen = ref(false)
  const whManageList = ref<any[]>([])
  const whManageLoading = ref(false)
  const whManageSearch = ref('')
  const whFormOpen = ref(false)
  const whFormMode = ref<'create' | 'edit'>('create')
  const whFormLoading = ref(false)
  const whFormSaving = ref(false)
  const whFormError = ref('')
  const whFormLockType = ref(false)
  const whForm = ref<any>({
    name: null,
    warehouse_name: '',
    company: '',
    wt_warehouse_type: 'Slot',
    parent_warehouse: '',
    is_group: true,
    wt_row: 0,
    wt_col: 0,
    wt_row_gap: 0,
    uom_capacities: [],
  })
  const whParentOptions = ref<any[]>([])
  const whCompanies = ref<any[]>([])
  const whUomOptions = ref<string[]>([])
  const whDeleteTarget = ref<any>(null)
  const whDeleting = ref(false)

  // Computed
  const filteredSlots = computed(() => {
    if (!searchQuery.value) return slots.value
    const q = searchQuery.value.toLowerCase()
    return slots.value.filter(sl =>
      sl.levels.some(lv =>
        (lv.items || []).some(it =>
          (it.c || '').toLowerCase().includes(q) ||
          (it.n || '').toLowerCase().includes(q)
        )
      )
    )
  })

  const hudStats = computed(() => {
    const allSlots = slots.value
    const bins = allSlots.flatMap(sl => sl.levels)
    const total = bins.length
    const occ = bins.filter(l => (l.uoms || []).some(u => u.qty > 0)).length
    const qty = allSlots.reduce((s, sl) =>
      s + sl.levels.reduce((ss, l) =>
        ss + (l.uoms || []).reduce((sss, u) => sss + (u.qty || 0), 0), 0), 0)
    return { total, occ, free: total - occ, qty }
  })

  // Actions
  function setView(view: ViewMode) {
    curView.value = view
  }

  function setLang(l: Language) {
    lang.value = l
  }

  function setTheme(dark: boolean) {
    isDark.value = dark
  }

  function setSearch(q: string) {
    searchQuery.value = q
  }

  function setGroup(g: WarehouseGroup | null) {
    selGroup.value = g
  }

  function setFloorFull(ff: FloorFull | null) {
    floorFull.value = ff
  }

  function setSlots(s: Slot[]) {
    slots.value = s
  }

  function setGroups(g: WarehouseGroup[]) {
    groups.value = g
  }

  function setLoading(l: boolean) {
    loading.value = l
  }

  function setThreeReady(ready: boolean) {
    threeReady.value = ready
  }

  function setShowWalls(show: boolean) {
    showWalls.value = show
  }

  function setShowMarkings(show: boolean) {
    showMarkings.value = show
  }

  function openDetailPanel(data: any) {
    dpData.value = data
    dpOpen.value = true
  }

  function closeDetailPanel() {
    dpOpen.value = false
    dpData.value = null
  }

  function enterAisleMode() {
    aisleMode.value = true
  }

  function exitAisleMode() {
    aisleMode.value = false
  }

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  return {
    // State
    curView,
    lang,
    isDark,
    searchQuery,
    loading,
    dragActive,
    threeReady,
    sidebarOpen,
    aisleMode,
    aislePickerOpen,
    aisleGaps,
    canEdit,
    canView,
    slots,
    groups,
    selGroup,
    floorFull,
    showWalls,
    showMarkings,
    ttVisible,
    ttData,
    ttX,
    ttY,
    dpOpen,
    dpData,
    docks,
    logisticsTasks,
    logisticsStats,
    selectedTask,
    logisticsOpen,
    logisticsStatsOpen,
    logisticsDateFrom,
    logisticsDateTo,
    agvOverlay,
    agvOpen,
    agvGrid,
    agvTool,
    agvCellSize,
    fpOpen,
    fpGroup,
    fpAllSlots,
    fpLayer,
    fpRows,
    fpShellDraft,
    fpSaveOk,
    fpSaving,
    fpShellErrors,
    setupStep,
    setupScan,
    setupMapping,
    setupSummary,
    setupSaving,
    whManageOpen,
    whManageList,
    whManageLoading,
    whManageSearch,
    whFormOpen,
    whFormMode,
    whFormLoading,
    whFormSaving,
    whFormError,
    whFormLockType,
    whForm,
    whParentOptions,
    whCompanies,
    whUomOptions,
    whDeleteTarget,
    whDeleting,

    // Computed
    filteredSlots,
    hudStats,

    // Actions
    setView,
    setLang,
    setTheme,
    setSearch,
    setGroup,
    setFloorFull,
    setSlots,
    setGroups,
    setLoading,
    setThreeReady,
    setShowWalls,
    setShowMarkings,
    openDetailPanel,
    closeDetailPanel,
    enterAisleMode,
    exitAisleMode,
    toggleSidebar,
  }
})
