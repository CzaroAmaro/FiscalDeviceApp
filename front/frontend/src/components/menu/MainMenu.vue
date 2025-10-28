<template>
  <v-list density="compact">
    <template v-for="item in translatedMenuItems" :key="item.value">
      <v-divider v-if="item.divider" class="my-2"></v-divider>

      <v-list-item
        v-else
        :prepend-icon="item.icon"
        :title="item.title"
        :value="item.value"
        :to="item.to"
        link>
      </v-list-item>
    </template>
  </v-list>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { getMenuItems } from '@/config/menuItems.ts';

const { t } = useI18n();

const translatedMenuItems = computed(() => getMenuItems(t));
</script>
