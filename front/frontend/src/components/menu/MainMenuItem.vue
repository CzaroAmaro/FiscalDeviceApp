<template>
  <v-list-item
    :active-class="`bg-blue-grey-darken-3 text-white`"
    class="my-1 mx-2"
    exact
    :prepend-icon="item.icon"
    rounded="lg"
    :title="item.title"
    :to="item.to"
    :disabled="!isActivated"
  >
    <!-- NOWOŚĆ: Slot tytułu do podświetlania tekstu -->
    <template #title>
      <MainMenuSearchColoring :search-text="searchQuery" :title="item.title!" />
    </template>
  </v-list-item>
</template>

<script lang="ts" setup>
import type { RouteLocationRaw } from 'vue-router'
import MainMenuSearchColoring from '@/components/menu/MainMenuSearchColoring.vue'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

// NOWOŚĆ: Ujednolicony typ, jak w przykładzie. Możesz go przenieść do osobnego pliku np. types/menu.ts
export type MenuItem = {
  to?: RouteLocationRaw
  title?: string
  icon?: string
  children?: MenuItem[]
  divider?: boolean // Zachowujemy divider na potrzeby danych wejściowych
}

defineProps<{
  item: MenuItem
  searchQuery: string | null // NOWOŚĆ: Prop do przekazania frazy
}>()

const authStore = useAuthStore()
const isActivated = computed(() => authStore.isActivated)
</script>
