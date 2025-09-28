<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      Urządzenia Fiskalne
      <v-spacer></v-spacer>
      <v-btn color="primary">Dodaj urządzenie</v-btn>
    </v-card-title>

    <v-alert v-if="error" type="error" class="ma-4">{{ error }}</v-alert>

    <v-data-table
      :headers="headers"
      :items="devices"
      :loading="isLoading"
      loading-text="Ładowanie danych..."
      no-data-text="Nie znaleziono urządzeń"
      class="elevation-1"
    >
    </v-data-table>
  </v-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api' // Nasza instancja Axios

// Definiujemy typ dla pojedynczego urządzenia, aby TypeScript nam pomagał
interface FiscalDevice {
  id: number;
  model_name: string;
  serial_number: string;
  production_date: string;
  last_service_date: string | null;
  status: string;
  owner_name: string;
}

const devices = ref<FiscalDevice[]>([]) // Reaktywna lista urządzeń
const isLoading = ref(true) // Stan ładowania danych
const error = ref<string | null>(null) // Przechowywanie ewentualnych błędów

// Definiujemy nagłówki dla naszej tabeli Vuetify
const headers = [
  { title: 'Model', key: 'model_name' },
  { title: 'Numer seryjny', key: 'serial_number' },
  { title: 'Właściciel', key: 'owner_name' },
  { title: 'Status', key: 'status' },
  { title: 'Data prod.', key: 'production_date' },
  { title: 'Ostatni serwis', key: 'last_service_date' },
]

// Funkcja do pobierania danych z API
const fetchDevices = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await api.get('/devices/')
    devices.value = response.data
  } catch (err) {
    console.error('Błąd podczas pobierania urządzeń:', err)
    error.value = 'Nie udało się załadować danych. Spróbuj ponownie później.'
  } finally {
    isLoading.value = false
  }
}

// `onMounted` to "hak cyklu życia" komponentu.
// Kod wewnątrz zostanie wykonany, gdy komponent zostanie zamontowany w DOM.
onMounted(() => {
  fetchDevices()
})
</script>
