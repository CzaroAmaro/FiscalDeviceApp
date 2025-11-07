<template>
  <v-list-item
    :to="item.to"
    :title="item.title"
    :prepend-icon="item.icon"
    :value="item.to || item.title"
    :disabled="!isActivated"
    link
    rounded="lg"
    class="mx-2 my-1"
  />
</template>

<script lang="ts" setup>
import type { MenuItem } from '@/config/menuItems';
import { useAuthStore } from '@/stores/auth';

defineProps<{
  item: MenuItem;
}>();

const authStore = useAuthStore();
const isActivated = authStore.isActivated;
</script>
