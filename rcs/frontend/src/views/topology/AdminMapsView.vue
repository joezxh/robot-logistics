<script setup lang="ts">
// Legacy "场景地图" (sys:map:list) top menu previously pointed at a removed
// topology admin view. The topology area was folded into the unified scene-maps
// console, so we re-mount the existing MapsListView here to keep the menu working
// without touching the database seed row (which already references this path).
import MapsListView from '@/views/maps/MapsListView.vue'
</script>

<template>
  <MapsListView />
</template>
