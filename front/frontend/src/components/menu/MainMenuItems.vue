<template>
  <template v-for="(item, index) in items" :key="index">
    <!-- Case 1: Renderuj separator -->
    <v-divider v-if="item.divider" class="my-2 mx-2" />

    <!-- Case 2: Renderuj grupę zagnieżdżoną -->
    <v-list-group v-else-if="item.children" :value="item.title">
      <template #activator="{ props }">
        <v-tooltip :disabled="!rail" location="end">
          <template #activator="{ props: tooltipProps }">
            <v-list-item
              v-bind="{ ...props, ...tooltipProps }"
              :prepend-icon="item.icon"
              :title="item.title"
              rounded="lg"
              class="mx-2 my-1"
            />
          </template>
          <span>{{ item.title }}</span>
        </v-tooltip>
      </template>

      <!-- REKURENCJA: Komponent wywołuje sam siebie dla dzieci grupy -->
      <MainMenuItems :items="item.children" :rail="rail" />
    </v-list-group>

    <!-- Case 3: Renderuj standardowy element listy -->
    <v-tooltip v-else :disabled="!rail" location="end">
      <template #activator="{ props }">
        <div v-bind="props">
          <MainMenuItem :item="item" />
        </div>
      </template>
      <span>{{ item.title }}</span>
    </v-tooltip>
  </template>
</template>

<script lang="ts" setup>
import type { MenuItem } from '@/config/menuItems';
import MainMenuItem from '@/components/menu/MainMenuItem.vue'

defineProps<{
  items: MenuItem[];
  rail: boolean;
}>();
</script>
