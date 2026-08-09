const dict = {
  zh: {
    title: '机器人智能仓储物流系统',
    subtitle: 'Mixed-fleet control plane · 集装箱 · AGV · 堆垛机',
    badge: '原型 v1.0',
    api: 'API ↗',
    metrics: 'Metrics ↗',
    devices: '设备状态',
    fleet: {
      running: '运行',
      idle: '空闲',
      charging: '充电',
      fault: '故障',
    },
    tasks: '任务队列',
    kpi: '关键指标',
    kpi_throughput: '吞吐量 / 小时',
    kpi_success: '成功率',
    kpi_active: '活跃任务',
    kpi_energy: '能耗 kWh',
    alerts: '告警',
    scene_caption: '实时场景',
    create_task: '创建任务',
    task_type: '任务类型',
    priority: '优先级',
    description: '任务描述',
    device: '目标设备',
    submit: '🚀 创建任务',
    rollback: '回滚',
    rollback_hint: '将最近已完成的任务回滚到执行前的设备状态。',
    rollback_busy: '回滚中…',
    logs: '实时日志',
    logs_filter_placeholder: '按 trace / module / message 过滤',
    logs_loading: '加载中…',
    logs_empty: '暂无日志',
    logs_no_match: '没有匹配的日志',
    connected: 'SSE 已连接',
    connecting: '重新连接中…',
    follow: '▶ 跟随',
    pause: '⏸ 暂停',
    ack: '确认',
    create_success: '✓ 已创建',
    create_fail: '✗ 创建失败：后端不可用',
    rollback_done: '已回滚',
    type_loading: '月台装卸',
    type_dock_loading: '月台装卸',
    type_agv_transport: 'AGV 转运',
    type_warehouse_storage: '立体仓储',
    select_device_hint: '选择',
    open_drawer: '详情',
    close_drawer: '关闭',
    confirm: '确认',
    cancel: '取消',
    task_timeline: '任务时间线',
    help: '键盘快捷键',
    hotkey_help: 'Ctrl+K 命令面板 · Ctrl+R 刷新 · Esc 关闭',
    no_devices_match: '未找到匹配的设备或任务',
    queue_empty: '队列为空',
    severity: { info: '提示', warning: '警告', critical: '严重' },
    state: { firing: '触发', acknowledged: '已确认', resolved: '已恢复' },
    ack_done: '已确认',
    toast: {
      task_created: '任务已创建',
      task_completed: '任务已完成',
      task_failed: '任务失败',
      ack_done: '告警已确认',
      rollback_done: '已回滚 {n} 条任务',
      backend_offline: '后端不可达，请检查 /api/status',
    },
    scene: {
      pause: '暂停',
      resume: '继续',
      reset: '重置',
      speed: '速度',
      auto_rotate: '自旋',
    },
    onboard: {
      title: '欢迎',
      hint: 'Ctrl+K 命令面板 · Ctrl+R 刷新 · Esc 关闭',
      skip: '跳过',
      next: '下一步',
      done: '完成',
    },
    kpi_zoom: {
      title: '历史趋势',
      range: '窗口',
      range_30m: '30 分钟',
      range_2h: '2 小时',
      range_all: '全部',
    },
    multi_select: {
      hint: '按住 Shift 多选设备',
      count: '已选 {n} 台',
      bulk_rollback: '批量回滚',
      confirm: '对 {n} 台设备执行批量回滚？',
    },
    history_empty: '暂无历史',
    battery: '电量',
    speed: '速度',
    position: '位置',
    task_history: '任务历史',
    current_task: '当前任务',
    no_task: '无',
    severity_filter_all: '全部级别',
    state_filter_all: '全部状态',
  },
  en: {
    title: 'Robot Logic — Warehouse Fleet Control',
    subtitle: 'Mixed-fleet control plane · container · AGV · stacker',
    badge: 'proto v1.0',
    api: 'API ↗',
    metrics: 'Metrics ↗',
    devices: 'Devices',
    fleet: { running: 'running', idle: 'idle', charging: 'charging', fault: 'fault' },
    tasks: 'Task queue',
    kpi: 'Key metrics',
    kpi_throughput: 'throughput / hour',
    kpi_success: 'success rate',
    kpi_active: 'active tasks',
    kpi_energy: 'energy kWh',
    alerts: 'Alerts',
    scene_caption: 'live scene',
    create_task: 'Create task',
    task_type: 'type',
    priority: 'priority',
    description: 'description',
    device: 'target device',
    submit: '🚀 create',
    rollback: 'Rollback',
    rollback_hint: 'Revert the most recent completed tasks to their pre-execution device state.',
    rollback_busy: 'rolling back…',
    logs: 'Live logs',
    logs_filter_placeholder: 'filter by trace / module / message',
    logs_loading: 'loading…',
    logs_empty: 'no logs yet',
    logs_no_match: 'no logs match',
    connected: 'SSE connected',
    connecting: 'reconnecting…',
    follow: '▶ follow',
    pause: '⏸ paused',
    ack: 'ack',
    create_success: '✓ created',
    create_fail: '✗ create failed: backend offline',
    rollback_done: 'rolled back',
    type_loading: 'dock loading',
    type_dock_loading: 'dock loading',
    type_agv_transport: 'AGV transport',
    type_warehouse_storage: 'warehouse storage',
    select_device_hint: 'pick',
    open_drawer: 'details',
    close_drawer: 'close',
    confirm: 'confirm',
    cancel: 'cancel',
    task_timeline: 'Task timeline',
    help: 'Keyboard shortcuts',
    hotkey_help: 'Ctrl+K command palette · Ctrl+R refresh · Esc close',
    no_devices_match: 'no matching devices or tasks',
    queue_empty: 'queue is empty',
    severity: { info: 'info', warning: 'warning', critical: 'critical' },
    state: { firing: 'firing', acknowledged: 'ack', resolved: 'resolved' },
    ack_done: 'acknowledged',
    toast: {
      task_created: 'Task created',
      task_completed: 'Task completed',
      task_failed: 'Task failed',
      ack_done: 'Alert acknowledged',
      rollback_done: 'Rolled back {n} tasks',
      backend_offline: 'Backend unreachable — check /api/status',
    },
    scene: {
      pause: 'Pause',
      resume: 'Resume',
      reset: 'Reset',
      speed: 'Speed',
      auto_rotate: 'Auto rotate',
    },
    onboard: {
      title: 'Welcome',
      hint: 'Ctrl+K palette · Ctrl+R refresh · Esc close',
      skip: 'Skip',
      next: 'Next',
      done: 'Done',
    },
    kpi_zoom: {
      title: 'Historical trend',
      range: 'window',
      range_30m: '30 min',
      range_2h: '2 h',
      range_all: 'all',
    },
    multi_select: {
      hint: 'Hold Shift to multi-select',
      count: '{n} selected',
      bulk_rollback: 'Bulk rollback',
      confirm: 'Bulk-rollback {n} devices?',
    },
    history_empty: 'no history',
    battery: 'battery',
    speed: 'speed',
    position: 'position',
    task_history: 'task history',
    current_task: 'current task',
    no_task: 'none',
    severity_filter_all: 'all levels',
    state_filter_all: 'all states',
  },
} as const

export type Lang = keyof typeof dict
export type Dict = typeof dict[Lang]

const STORAGE_KEY = 'robot-logic.lang'

function detectInitial(): Lang {
  if (typeof localStorage === 'undefined') return 'zh'
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'zh' || stored === 'en') return stored
  const nav = (typeof navigator !== 'undefined' ? navigator.language : 'zh')?.toLowerCase() ?? 'zh'
  return nav.startsWith('zh') ? 'zh' : 'en'
}

import { ref, computed, type Ref, type ComputedRef } from 'vue'

const lang: Ref<Lang> = ref(detectInitial())

function applyDocumentLang(l: Lang): void {
  if (typeof document !== 'undefined') {
    document.documentElement.lang = l === 'zh' ? 'zh-CN' : 'en'
  }
}

applyDocumentLang(lang.value)

export function useI18n(): { t: ComputedRef<Dict>; lang: Ref<Lang>; toggle: () => void; set: (l: Lang) => void } {
  const t = computed(() => dict[lang.value])
  function toggle(): void {
    const next: Lang = lang.value === 'zh' ? 'en' : 'zh'
    set(next)
  }
  function set(l: Lang): void {
    lang.value = l
    applyDocumentLang(l)
    try { localStorage.setItem(STORAGE_KEY, l) } catch { /* ignore */ }
  }
  return { t, lang, toggle, set }
}

export function tr(key: keyof Dict): string {
  return dict[lang.value][key] as string
}

export function tf(template: string, params: Record<string, string | number> = {}): string {
  return template.replace(/\{(\w+)\}/g, (_, k) => String(params[k] ?? `{${k}}`))
}
