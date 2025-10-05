<template>
  <v-list density="compact">

    <template v-for="item in menuItems" :key="item.value">

      <v-divider v-if="item.divider" class="my-2"></v-divider>

      <v-list-item
        :prepend-icon="item.icon"
        :title="item.title"
        :value="item.value"
        :to="item.to"
        link
      ></v-list-item>

    </template>
  </v-list>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { MenuItem } from '@/types/index.ts'

const menuItems = ref<MenuItem[]>([
  {
    title: 'Pulpit',
    value: 'dashboard',
    icon: 'mdi-view-dashboard',
    to: { name: 'home' },
  },
  {
    title: 'Urządzenia',
    value: 'devices',
    icon: 'mdi-printer-pos',
    to: { name: 'devices' },
  },
  {
    title: 'Klienci',
    value: 'clients',
    icon: 'mdi-account-group-outline',
    to: { name: 'clients' },
  }
])
</script>
