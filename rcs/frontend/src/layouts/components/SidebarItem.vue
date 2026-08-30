<script setup lang="ts">
// Recursive sidebar entry.
//
// A menu node with children renders as a sub-menu; a leaf renders as a menu
// item. The component recurses into itself to support arbitrary depth, which
// matches how `sys_menu.parent_id` is modelled.
import type { MenuNode } from '@/types'
import { resolveIcon } from '@/utils/icons'
import { localise } from '@/i18n'

defineProps<{ node: MenuNode }>()
</script>

<template>
  <a-sub-menu v-if="node.children?.length" :key="`dir-${node.id}`">
    <template #icon>
      <component :is="resolveIcon(node.icon)" />
    </template>
    <template #title>{{ localise(node.i18n, node.name) }}</template>
    <SidebarItem v-for="child in node.children" :key="child.id" :node="child" />
  </a-sub-menu>

  <a-menu-item v-else :key="node.path ?? `menu-${node.id}`">
    <template #icon>
      <component :is="resolveIcon(node.icon)" />
    </template>
    <span>{{ localise(node.i18n, node.name) }}</span>
  </a-menu-item>
</template>
