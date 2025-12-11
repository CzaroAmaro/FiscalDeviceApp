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

export type MenuItem = {
  to?: RouteLocationRaw
  title?: string
  icon?: string
  children?: MenuItem[]
  divider?: boolean
}

defineProps<{
  item: MenuItem
  searchQuery: string | null
}>()

const authStore = useAuthStore()
const isActivated = computed(() => authStore.isActivated)
</script>
