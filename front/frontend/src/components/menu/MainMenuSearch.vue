<template>
  <div class="pa-2">
    <v-text-field
      v-model="searchQuery"
      clearable
      density="compact"
      flat
      hide-details
      :placeholder="$t('menu.searchPlaceholder')"
      prepend-inner-icon="mdi-magnify"
      variant="solo-filled"
      @focus="emit('focused')"
    />
  </div>
</template>

<script lang="ts" setup>
import { defineModel } from 'vue'
import { useI18n } from 'vue-i18n'

const emit = defineEmits(['focused'])

const searchQuery = defineModel<string | null>()


</script>
