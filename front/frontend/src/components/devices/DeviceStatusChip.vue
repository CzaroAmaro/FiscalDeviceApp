<template>
  <v-chip :color="statusColor" size="small" label>
    <v-icon v-if="statusIcon" start size="14">{{ statusIcon }}</v-icon>
    {{ statusText }}
  </v-chip>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  status: string
}>()

interface StatusInfo {
  color: string
  text: string
  icon: string
}

const statusMap: Record<string, StatusInfo> = {
  active: {
    color: 'success',
    text: 'Aktywne',
    icon: 'mdi-check-circle'
  },
  inactive: {
    color: 'grey',
    text: 'Nieaktywne',
    icon: 'mdi-pause-circle'
  },
  serviced: {
    color: 'warning',
    text: 'W serwisie',
    icon: 'mdi-wrench'
  },
  decommissioned: {
    color: 'error',
    text: 'Wycofane',
    icon: 'mdi-cancel'
  },
  default: {
    color: 'grey',
    text: 'Nieznany',
    icon: 'mdi-help-circle'
  }
}

const statusInfo = computed(() => {
  return statusMap[props.status?.toLowerCase()] || statusMap.default
})

const statusColor = computed(() => statusInfo.value.color)
const statusText = computed(() => statusInfo.value.text)
const statusIcon = computed(() => statusInfo.value.icon)
</script>
