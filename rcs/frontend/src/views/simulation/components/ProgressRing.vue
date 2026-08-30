<template>
  <div class="ring" :style="{ '--size': size + 'px', '--stroke': stroke + 'px' }">
    <svg :width="size" :height="size">
      <circle :cx="size / 2" :cy="size / 2" :r="radius" class="bg" />
      <circle
        :cx="size / 2"
        :cy="size / 2"
        :r="radius"
        class="fg"
        :class="stateClass"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        :transform="`rotate(-90 ${size / 2} ${size / 2})`"
      />
    </svg>
    <div class="label">
      <span class="pct">{{ Math.round(value) }}</span>
      <span class="unit">%</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  value: number
  size?: number
  stroke?: number
  state?: 'running' | 'pending' | 'completed' | 'failed' | 'reverted'
}>(), { size: 48, stroke: 5, state: 'running' })

const radius = computed(() => (props.size - props.stroke) / 2 - 1)
const circumference = computed(() => 2 * Math.PI * radius.value)
const dashOffset = computed(() => circumference.value * (1 - Math.max(0, Math.min(100, props.value)) / 100))
const stateClass = computed(() => props.state)
</script>

<style scoped>
.ring { position: relative; display: inline-flex; align-items: center; justify-content: center; }
.ring svg { display: block; }
.bg { fill: none; stroke: #1d2740; stroke-width: var(--stroke); }
.fg { fill: none; stroke-width: var(--stroke); stroke-linecap: round; transition: stroke-dashoffset 0.4s ease, stroke 0.4s ease; }
.fg.running { stroke: #5eb0ff; }
.fg.pending { stroke: #8a98ad; }
.fg.completed { stroke: #1f8a4c; }
.fg.failed { stroke: #c0392b; }
.fg.reverted { stroke: #d68910; }
.label { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; gap: 2px; font-size: 12px; font-weight: 700; color: #e6e9ef; }
.pct { font-size: 12px; }
.unit { font-size: 9px; opacity: 0.7; }
</style>