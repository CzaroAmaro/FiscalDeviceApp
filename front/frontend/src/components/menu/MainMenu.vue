<template>
  <v-navigation-drawer
    :rail="mini"
    permanent
    rail-width="72"
    width="280"
    class="main-menu-drawer"
  >
    <!-- Nagłówek - zawsze na górze -->
    <template #prepend>
      <MainMenuHeader v-model:mini="mini" />

      <!-- Wyszukiwarka TUTAJ - zaraz pod headerem -->
      <MainMenuSearch
        v-if="!mini"
        v-model="searchQuery"
        class="mx-3 mb-2"
      />
      <v-divider v-if="!mini" />
    </template>

    <!-- Scrollowalna lista menu -->
    <v-list
      v-model:opened="openedGroups"
      class="pt-2"
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

      <div v-else class="text-body-2 text-grey text-center pa-4">
        {{ t('menu.nothingFoundInMenu') }}
      </div>
    </v-list>
  </v-navigation-drawer>
</template>

<script lang="ts" setup>
import MainMenuHeader from '@/components/menu/MainMenuHeader.vue'
import MainMenuItems from '@/components/menu/MainMenuItems.vue'
import MainMenuSearch from '@/components/menu/MainMenuSearch.vue'
import type { MenuItem } from '@/config/menuItems'
import { useMenu } from '@/components/menu/useMainMenu'
import { ref, toRefs } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{
  items: MenuItem[]
}>()

const mini = defineModel<boolean>('mini', { default: false })

const { items } = toRefs(props)
const { t } = useI18n()
const searchQuery = ref<string | null>(null)

const { filteredItems, openedGroups, isSearching } = useMenu(items, searchQuery)
</script>

<style scoped>
.main-menu-drawer :deep(.v-navigation-drawer__content) {
  display: flex;
  flex-direction: column;
}

.main-menu-drawer :deep(.v-list) {
  flex: 1;
  overflow-y: auto;
}
</style>
