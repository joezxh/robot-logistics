<script setup lang="ts">
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <a-layout class="workspace">
    <AppSidebar />

    <a-layout class="workspace-main">
      <AppHeader />

      <a-layout-content class="workspace-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
.workspace {
  display: flex !important;
  flex-direction: row !important;
  height: 100vh;
  background: transparent;
}

.workspace-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
  background: transparent;
}

.workspace-content {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* keep the frosted page glow from bleeding through the content scroll area */
.workspace-content :deep(.app-page) {
  height: 100%;
}
</style>
