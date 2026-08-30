<script setup lang="ts">
// Console shell: sidebar (left) + top bar + main content (right).
//
// The sidebar is driven entirely by the permission-filtered menu tree held in
// the auth store, so the layout itself contains no hard-coded navigation.
import AppSidebar from './components/AppSidebar.vue'
import AppHeader from './components/AppHeader.vue'
</script>

<template>
  <div class="console">
    <AppSidebar />
    <div class="console-body">
      <AppHeader />
      <main class="console-content">
        <router-view v-slot="{ Component, route }">
          <keep-alive :max="8">
            <component :is="Component" v-if="route.meta.keepAlive" :key="route.path" />
          </keep-alive>
          <component :is="Component" v-if="!route.meta.keepAlive" :key="route.path" />
        </router-view>
      </main>
    </div>
  </div>
</template>

<style scoped>
.console {
  display: flex;
  height: 100%;
  background: var(--bg-page);
  overflow: hidden;
}

.console-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.console-content {
  flex: 1;
  min-height: 0;
  overflow: auto;
  position: relative;
}
</style>
