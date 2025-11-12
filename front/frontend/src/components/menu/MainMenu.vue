<template>
  <v-navigation-drawer
    :rail="mini"
    permanent
    rail-width="72"
    width="280"
  >
    <template #prepend>
      <MainMenuHeader v-model:mini="mini" />
    </template>

    <v-list
      v-model:opened="openedGroups"
      class="pt-0"
      density="comfortable"
      nav
      open-strategy="multiple"
    >
      <MainMenuItems
        v-if="!isSearching || filteredItems.length > 0"
        v-model:opened="openedGroups"
        :items="filteredItems"
        :mini="mini"
        :search-query="searchQuery"
      />
      <!-- NOWOŚĆ: Komunikat, gdy nic nie znaleziono -->
      <div v-else class="text-body-2 text-grey text-center pa-4">
        {{ t('menu.nothingFoundInMenu') }}
      </div>
    </v-list>

    <template #append>
      <MainMenuSearch
        v-model="searchQuery"
        @focused="mini = false"
      />
    </template>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import MainMenuHeader from '@/components/menu/MainMenuHeader.vue'
import MainMenuItems from '@/components/menu/MainMenuItems.vue'
import MainMenuSearch from '@/components/menu/MainMenuSearch.vue'
import type { MenuItem } from '@/config/menuItems'
import { useMenu } from '@/components/menu/useMainMenu.ts'
import { ref, toRefs } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  items: MenuItem[]
}>()

const mini = defineModel<boolean>('mini', { default: false })

const { items } = toRefs(props)
const {t} = useI18n()
const searchQuery = ref<string | null>(null)

// NOWOŚĆ: Użycie composable do zarządzania logiką menu
const { filteredItems, openedGroups, isSearching } = useMenu(items, searchQuery)
</script>
