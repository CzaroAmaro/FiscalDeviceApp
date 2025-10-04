<!-- src/components/devices/DeviceDataTable.vue -->
<template>
  <v-data-table
    :headers="headers"
    :items="devices"
    :loading="loading"
    loading-text="Ładowanie danych..."
    no-data-text="Nie znaleziono urządzeń"
    class="elevation-1"
  >
    <!-- Używamy slotu, aby dostosować renderowanie komórki statusu -->
    <template #item.status="{ item }">
      <DeviceStatusChip :status="item.status" />
    </template>

    <!-- Slot na przyszłe akcje (np. przyciski Edytuj/Usuń) -->
    <template #item.actions="{ item }">
      <v-icon size="small" class="me-2" @click="$emit('edit', item.id)">
        mdi-pencil
      </v-icon>
      <v-icon size="small" @click="$emit('delete', item.id)">
        mdi-delete
      </v-icon>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import type { FiscalDevice } from '@/types'
import DeviceStatusChip from './DeviceStatusChip.vue'

defineProps<{
  devices: FiscalDevice[]
  loading: boolean
}>()

defineEmits<{
  (e: 'edit', id: number): void
  (e: 'delete', id: number): void
}>()

const headers = [
  { title: 'Model', key: 'model_name' },
  { title: 'Numer seryjny', key: 'serial_number' },
  { title: 'Właściciel', key: 'owner_name' },
  { title: 'Status', key: 'status' },
  { title: 'Data prod.', key: 'production_date' },
  { title: 'Ostatni serwis', key: 'last_service_date' },
  { title: 'Akcje', key: 'actions', sortable: false }, // Dodajemy kolumnę akcji
]
</script>
