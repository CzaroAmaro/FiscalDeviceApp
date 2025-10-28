<template>
  <!-- Case 1: Renderuj separator, jeśli zdefiniowano -->
  <v-divider v-if="item.divider" class="my-2" />

  <!-- Case 2: Renderuj standardowy element listy -->
  <v-tooltip v-else :disabled="!rail" location="right">
    <template #activator="{ props }">
      <v-list-item
        v-bind="props"
        :prepend-icon="item.icon"
        :title="item.title"
        :value="item.value"
        :to="item.to"
        link
      />
    </template>
    <span>{{ item.title }}</span>
  </v-tooltip>
</template>

<script setup lang="ts">
import type { MenuItem } from '@/config/menuItems'; // Użyjemy typu z pliku konfiguracyjnego

defineProps<{
  /**
   * Obiekt definiujący element menu.
   */
  item: MenuItem;
  /**
   * Określa, czy menu jest zwinięte (do pokazania tooltipa).
   */
  rail: boolean;
}>();
</script>
