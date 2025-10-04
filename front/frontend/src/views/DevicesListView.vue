<!-- src/views/DevicesListView.vue (nowa, czysta wersja) -->
<template>
  <v-card>
    <v-card-title class="d-flex align-center">
      Urządzenia Fiskalne
      <v-spacer></v-spacer>
      <!-- W przyszłości ten przycisk otworzy modal -->
      <v-btn color="primary" @click="openAddDeviceModal">Dodaj urządzenie</v-btn>
    </v-card-title>

    <!-- Globalny komunikat o błędzie -->
    <v-alert v-if="devicesStore.error" type="error" class="ma-4">
      {{ devicesStore.error }}
    </v-alert>

    <!-- Przekazujemy dane do naszego nowego komponentu tabeli -->
    <DeviceDataTable
      :devices="devicesStore.devices"
      :loading="devicesStore.isLoading"
      @edit="handleEdit"
      @delete="handleDelete"
    />
  </v-card>

  <!-- W przyszłości: <DeviceFormModal v-model="isModalOpen" /> -->
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import DeviceDataTable from '@/components/devices/DeviceDataTable.vue'

// Pobieramy instancję naszego nowego store'a
const devicesStore = useDevicesStore()

// Wywołujemy akcję pobierania danych, gdy komponent jest montowany
onMounted(() => {
  // Pobieramy dane tylko jeśli jeszcze ich nie mamy, aby uniknąć zbędnych zapytań
  if (devicesStore.devices.length === 0) {
    devicesStore.fetchDevices()
  }
})

const openAddDeviceModal = () => {
  console.log('Otwieranie modala do dodawania urządzenia...')
  // Tutaj będzie logika otwierania modala/dialogu
}

const handleEdit = (id: number) => {
  console.log(`Edytowanie urządzenia o ID: ${id}`)
  // Tutaj logika edycji
}

const handleDelete = (id: number) => {
  console.log(`Usuwanie urządzenia o ID: ${id}`)
  // Tutaj logika usuwania
}
</script>
