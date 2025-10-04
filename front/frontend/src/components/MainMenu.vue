<!-- src/components/layout/MainMenu.vue -->
<template>
  <v-list density="compact">
    <!-- Używamy pętli v-for do dynamicznego generowania linków -->
    <template v-for="item in menuItems" :key="item.value">

      <!-- Opcjonalny separator -->
      <v-divider v-if="item.divider" class="my-2"></v-divider>

      <!-- Element listy -->
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

// Nasze menu jako tablica obiektów - jedyne miejsce, które będziesz edytować w przyszłości!
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
    divider: true
  },
  {
    title: 'Klienci',
    value: 'clients',
    icon: 'mdi-account-group-outline',
    to: { name: 'home' }, // Zmień na właściwą ścieżkę w przyszłości
  }
])
</script>
