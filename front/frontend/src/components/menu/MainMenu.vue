<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="mini"
    permanent
    width="280"
    rail-width="72"
    color="grey-darken-3"
  >
    <template #prepend>
      <!-- Używamy v-model do dwukierunkowej komunikacji stanu mini -->
      <MainMenuHeader v-model:mini="mini" />
    </template>

    <v-list v-model:opened="openedGroups" nav density="compact">
      <MainMenuItems :items="items" :rail="mini" />
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import MainMenuHeader from '@/components/menu/MainMenuHeader.vue';
import MainMenuItems from '@/components/menu/MainMenuItems.vue';
import type { MenuItem } from '@/config/menuItems'

// Przechowuje otwarte grupy menu

defineProps<{
  items: MenuItem[];
}>();

// Definiuje v-model:mini, który może być użyty w komponencie nadrzędnym
const mini = defineModel<boolean>('mini');

const drawer = ref(true); // Stan widoczności szuflady (głównie dla mobile)
const openedGroups = ref([]);</script>
