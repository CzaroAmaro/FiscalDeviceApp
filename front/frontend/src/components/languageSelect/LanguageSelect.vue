<template>
  <v-select
    :model-value="languageStore.currentLanguage"
    :items="languages"
    item-title="label"
    item-value="value"
    hide-details
    variant="outlined"
    density="compact"
    flat
    @update:model-value="languageStore.setLanguage"
  />
</template>

<script setup lang="ts">
import { useLanguageStore } from '@/stores/language'

const languageStore = useLanguageStore()

const languages = [
  { label: 'Polski', value: 'pl' },
  { label: 'English', value: 'en' },
]
</script>
