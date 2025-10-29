<template>
  <v-list-item
    :to="item.to"
    :title="item.title"
    :prepend-icon="item.icon"
    :value="item.to || item.title"
    link
    rounded="lg"
    class="mx-2 my-1"
  />
</template>

<script lang="ts" setup>
import type { MenuItem } from '@/config/menuItems';

defineProps<{
  item: MenuItem;
}>();
</script>
