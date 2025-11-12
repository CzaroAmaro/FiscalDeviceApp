<template>
  <span v-if="searchText && startIndex > -1">
    <span>{{ title.substring(0, startIndex) }}</span>
    <span class="text-red font-weight-bold">
      {{ title.substring(startIndex, endIndex) }}
    </span>
    <span>{{ title.substring(endIndex) }}</span>
  </span>
  <span v-else>
    {{ title }}
  </span>
</template>

<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps<{
  title: string
  searchText: string | null
}>()

const startIndex = computed<number>(() => {
  if (!props.searchText || !props.title) {
    return -1
  }
  return props.title.toLowerCase().indexOf(props.searchText.toLowerCase())
})

const endIndex = computed<number>(() => {
  if (startIndex.value === -1 || !props.searchText) {
    return -1
  }
  return startIndex.value + props.searchText.length
})
</script>
