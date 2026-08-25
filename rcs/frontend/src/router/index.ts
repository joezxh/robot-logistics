import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import SiteMapView from '@/views/SiteMapView.vue'
import ControlView from '@/views/ControlView.vue'
import AdminDevicesView from '@/views/AdminDevicesView.vue'
import AdminMapsView from '@/views/AdminMapsView.vue'
import AdminOrdersView from '@/views/AdminOrdersView.vue'
import AdminSchedulerView from '@/views/AdminSchedulerView.vue'
import AdminLogsView from '@/views/AdminLogsView.vue'

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', redirect: '/devices' },
  { path: '/sitemap', name: 'sitemap', component: SiteMapView },
  { path: '/control', name: 'control', component: ControlView },
  { path: '/devices', name: 'admin-devices', component: AdminDevicesView },
  { path: '/admin/maps', name: 'admin-maps', component: AdminMapsView },
  { path: '/admin/orders', name: 'admin-orders', component: AdminOrdersView },
  { path: '/admin/scheduler', name: 'admin-scheduler', component: AdminSchedulerView },
  { path: '/admin/logs', name: 'admin-logs', component: AdminLogsView },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})