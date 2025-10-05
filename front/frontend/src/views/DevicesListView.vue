<!-- src/views/DevicesListView.vue -->
<template>
  <v-container fluid>
    <v-row class="align-center mb-4">
      <v-col>
        <h1 class="text-h4">Urządzenia Fiskalne</h1>
      </v-col>
      <v-col class="text-right">
        <v-btn color="primary" @click="openAddModal">
          <v-icon start>mdi-plus</v-icon>
          Dodaj urządzenie
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-alert v-if="devicesStore.error" type="error" class="ma-4">
        {{ devicesStore.error }}
      </v-alert>
      <DeviceDataTable
        :devices="devicesStore.devices"
        :loading="devicesStore.isLoading"
        @edit="openEditModal"
        @delete="openDeleteConfirm"
      />
    </v-card>

    <DeviceFormModal
      v-model="isFormModalOpen"
      :editing-device="selectedDevice"
      @save-success="showSnackbar"
    />

    <v-dialog v-model="isConfirmOpen" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h5">Potwierdź usunięcie</v-card-title>
        <v-card-text>
          Czy na pewno chcesz usunąć urządzenie
          <strong>{{ selectedDevice?.model_name }} (S/N: {{ selectedDevice?.serial_number }})</strong>?
          Ta operacja jest nieodwracalna.
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="isConfirmOpen = false">Anuluj</v-btn>
          <v-btn color="error" @click="handleDelete">Usuń</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import type { FiscalDevice } from '@/types'
import DeviceDataTable from '@/components/devices/DeviceDataTable.vue'
import DeviceFormModal from '@/components/devices/DeviceFormModal.vue'

const devicesStore = useDevicesStore()

const isFormModalOpen = ref(false)
const isConfirmOpen = ref(false)
const selectedDevice = ref<FiscalDevice | null>(null)
const snackbar = reactive({ show: false, text: '', color: 'success' })

onMounted(() => {
  devicesStore.fetchDevices()
})

const openAddModal = () => {
  selectedDevice.value = null
  isFormModalOpen.value = true
}

const openEditModal = (device: FiscalDevice) => {
  selectedDevice.value = { ...device } // Kopiujemy, aby uniknąć problemów z reaktywnością
  isFormModalOpen.value = true
}

const openDeleteConfirm = (device: FiscalDevice) => {
  selectedDevice.value = device
  isConfirmOpen.value = true
}

const handleDelete = async () => {
  if (selectedDevice.value) {
    await devicesStore.deleteDevice(selectedDevice.value.id)
    showSnackbar(`Urządzenie ${selectedDevice.value.model_name} zostało usunięte.`, 'info')
  }
  isConfirmOpen.value = false
}

const showSnackbar = (text: string, color = 'success') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}
</script>
