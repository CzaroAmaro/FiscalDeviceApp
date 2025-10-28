<template>
  <v-list density="compact" nav>
    <MainMenuItem
      v-for="item in items"
      :key="item.value || 'divider'"
      :item="item"
      :rail="rail"
    />
  </v-list>
</template>

<script setup lang="ts">
import type { MenuItem } from '@/config/menuItems';
import MainMenuItem from './MainMenuItem.vue';

defineProps<{
  /**
   * Tablica elementów menu do wyrenderowania.
   */
  items: MenuItem[];
  /**
   * Przekazuje stan zwinięcia do dzieci.
   */
  rail: boolean;
}>();
</script>
