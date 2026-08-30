<script setup lang="ts">
// Route shell for the simulation dashboard (`/simulation`).
import SimulationRoot from './SimulationRoot.vue'
import DashboardPage from './dashboard/DashboardPage.vue'
</script>

<template>
  <SimulationRoot>
    <DashboardPage />
  </SimulationRoot>
</template>
