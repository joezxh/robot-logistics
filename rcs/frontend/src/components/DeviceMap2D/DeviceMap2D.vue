<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, shallowRef } from 'vue'
import * as echarts from 'echarts'
import type { FloorShell } from '@/types'
import { buildMapOption } from './option'

const props = defineProps<{
  shell: FloorShell | null
  floorIndex?: number
}>()

const el = ref<HTMLDivElement | null>(null)
const chart = shallowRef<echarts.ECharts | null>(null)

function render() {
  if (!chart.value || !props.shell) return
  chart.value.setOption(buildMapOption({ shell: props.shell, floorIndex: props.floorIndex }), true)
}

onMounted(() => {
  if (!el.value) return
  chart.value = echarts.init(el.value, undefined, { renderer: 'canvas' })
  render()
  window.addEventListener('resize', onResize)
})

function onResize() {
  chart.value?.resize()
}

watch(() => [props.shell, props.floorIndex], render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  chart.value?.dispose()
  chart.value = null
})
</script>

<template>
  <div class="device-map-2d">
    <div v-if="!shell" class="empty">—</div>
    <div v-show="shell" ref="el" class="canvas" data-testid="map2d"></div>
  </div>
</template>

<style scoped>
.device-map-2d { width: 100%; height: 100%; }
.canvas { width: 100%; height: 100%; min-height: 320px; }
.empty { color: var(--fg-soft); display: grid; place-items: center; height: 100%; }
</style>
