<template>
  <v-chip :color="statusColor" size="small" label>
    {{ statusText }}
  </v-chip>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

const statusMap: Record<string, { color: string; text: string }> = {
  active: { color: 'green', text: 'Aktywne' },
  inactive: { color: 'red', text: 'Niewaktywne' },
  serviced: { color: 'blue', text: 'W serwisie' },
  // Dodaj inne statusy, jeśli istnieją
  default: { color: 'grey', text: 'Nieznany' }
}

const statusInfo = computed(() => {
  return statusMap[props.status.toLowerCase()] || statusMap.default
})

const statusColor = computed(() => statusInfo.value.color)
const statusText = computed(() => statusInfo.value.text)
</script>
