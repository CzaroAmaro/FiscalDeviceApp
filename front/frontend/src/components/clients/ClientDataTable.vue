<template>
  <v-data-table
    :headers="headers"
    :items="clients"
    :loading="loading"
    item-value="id"
    loading-text="Ładowanie danych klientów..."
    no-data-text="Nie znaleziono klientów"
  >
    <template #item.actions="{ item }">
      <v-icon class="me-2" size="small" @click="$emit('edit', item)">
        mdi-pencil
      </v-icon>
      <v-icon size="small" @click="$emit('delete', item)">
        mdi-delete
      </v-icon>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import type { Client } from '@/types'

defineProps<{
  clients: Client[]
  loading: boolean
}>()

const emit = defineEmits<{
  (e: 'edit', client: Client): void
  (e: 'delete', client: Client): void
}>()

const headers = [
  { title: 'Nazwa firmy/Imię i nazwisko', key: 'name' },
  { title: 'NIP', key: 'nip' },
  { title: 'Telefon', key: 'phone_number' },
  { title: 'Email', key: 'email' },
  { title: 'Akcje', key: 'actions', sortable: false, align: 'end' },
]
</script>
