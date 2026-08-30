import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import App from './App.vue'
import { resetDynamicRoutes, router } from './router'
import { i18n } from './i18n'
import { sysHttp } from './api/sysHttp'
import { useAuthStore } from './stores/auth'
// Order matters: tokens define the variables, global.css consumes them.
import './styles/tokens.css'
import './styles/global.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(Antd)

// Reflect the initial language on <html lang> for a11y / browser translation.
document.documentElement.setAttribute('lang', i18n.global.locale.value)

// A rejected token means the session expired mid-flight (or the account was
// disabled). Clear the local session so the router guard sends the user back to
// the login page instead of leaving them on a dead screen.
sysHttp.onUnauthorized = () => {
  const auth = useAuthStore()
  if (!auth.isAuthenticated) return
  auth.reset()
  resetDynamicRoutes()
  void router.push({ name: 'login' })
}

app.mount('#app')
