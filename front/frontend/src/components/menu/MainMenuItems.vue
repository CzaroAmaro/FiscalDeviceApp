<template>
  <template
    v-for="(item, index) in items"
    :key="`${item.title}-${mini ? 'mini' : 'normal'}-${index}`"
  >

    <v-tooltip
      v-if="!item.children || item.children.length === 0"
      :disabled="!mini"
      location="end"
      :text="item.title"
    >
      <template #activator="{ props: tooltipActivatorProps }">
        <MainMenuItem
          :item="item"
          :search-query="searchQuery"
          v-bind="mini ? tooltipActivatorProps : undefined"
        />
      </template>
    </v-tooltip>

    <template v-else>
      <v-list-group v-if="!mini" :value="item.title">
        <template #activator="{ props: activatorProps }">
          <v-list-item
            v-bind="activatorProps"
            class="my-1 mx-2"
            :prepend-icon="item.icon"
            rounded="lg"
          >
            <template #title>
              <MainMenuSearchColoring :search-text="searchQuery" :title="item.title!" />
            </template>
          </v-list-item>
        </template>
        <MainMenuItems
          v-model:opened="openedGroups"
          :items="item.children"
          :mini="mini"
          :search-query="searchQuery"
        />
      </v-list-group>

      <!-- Widok zwinięty (mini) -->
      <div v-else>
        <v-tooltip location="end" :text="item.title">
          <template #activator="{ props: tooltipActivatorProps }">
            <v-list-item
              v-bind="tooltipActivatorProps"
              class="my-1 mx-2"
              :prepend-icon="item.icon"
              rounded="lg"
              @click="toggleGroup(item.title!)"
            />
          </template>
        </v-tooltip>
        <div v-if="isGroupOpen(item.title!)" class="mini-submenu">
          <MainMenuItems
            :items="item.children"
            :mini="false"
            :search-query="searchQuery"
          />
        </div>
      </div>
    </template>
  </template>
</template>

<script lang="ts" setup>
defineProps<{
  items: MenuItem[]
  searchQuery: string | null
  mini: boolean
}>()

console.log(import.meta.env.BASE_URL)

import type { MenuItem } from '@/components/menu/MainMenuItem.vue'
import MainMenuItem from '@/components/menu/MainMenuItem.vue'
import MainMenuSearchColoring from '@/components/menu/MainMenuSearchColoring.vue'

const openedGroups = defineModel<string[]>('opened')

function toggleGroup (groupTitle: string) {
  if (!openedGroups.value) {
    openedGroups.value = [groupTitle];
    return;
  }

  openedGroups.value = openedGroups.value.includes(groupTitle)
    ? openedGroups.value.filter(title => title !== groupTitle)
    : [...openedGroups.value, groupTitle]
}

function isGroupOpen (groupTitle: string) {
  return openedGroups.value?.includes(groupTitle) ?? false
}
</script>

