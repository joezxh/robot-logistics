import { createRouter, createWebHistory } from 'vue-router'

const ScenesPage = () => import('../scenes/ScenesPage.vue')
const Dashboard = () => import('../dashboard/DashboardPage.vue')

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/scenes', name: 'scenes', component: ScenesPage },
  ],
})
