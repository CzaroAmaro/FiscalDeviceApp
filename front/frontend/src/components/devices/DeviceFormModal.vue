<!-- src/components/devices/DeviceFormModal.vue -->
<template>
  <v-dialog :model-value="modelValue" @update:model-value="closeDialog" max-width="700px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="submitForm">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.model_name" label="Model urządzenia" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.serial_number" label="Numer seryjny" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.production_date" label="Data produkcji" type="date" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select v-model="formData.status" :items="statusOptions" label="Status" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="formData.owner"
                  :items="clientsStore.clients"
                  item-title="name"
                  item-value="id"
                  label="Właściciel"
                  :loading="clientsStore.isLoading"
                  :rules="[rules.required]"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" @click="closeDialog">Anuluj</v-btn>
        <v-btn color="primary" @click="submitForm" :loading="isLoading">Zapisz</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted } from 'vue'
import { useDevicesStore } from '@/stores/devices'
import { useClientsStore } from '@/stores/clients'
import type { FiscalDevice, Client } from '@/types'
import type { VForm } from 'vuetify/components'

const props = defineProps<{
  modelValue: boolean
  editingDevice: FiscalDevice | null
}>()

const emit = defineEmits(['update:modelValue', 'save-success'])

const devicesStore = useDevicesStore()
const clientsStore = useClientsStore()

const form = ref<VForm | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const initialFormData = { model_name: '', serial_number: '', production_date: '', status: 'active', owner: null }
const formData = reactive<any>({ ...initialFormData })

const isEditing = computed(() => !!props.editingDevice)
const formTitle = computed(() => isEditing.value ? 'Edytuj urządzenie' : 'Dodaj nowe urządzenie')

const statusOptions = [
  { title: 'Aktywna', value: 'active' },
  { title: 'Niewykorzystywana', value: 'inactive' },
  { title: 'W serwisie', value: 'serviced' },
  { title: 'Wycofana', value: 'decommissioned' },
]

// Pobierz listę klientów, gdy komponent się załaduje
onMounted(() => {
  clientsStore.fetchClients()
})

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (isEditing.value && props.editingDevice) {
      // Przygotuj dane do edycji
      formData.model_name = props.editingDevice.model_name
      formData.serial_number = props.editingDevice.serial_number
      formData.production_date = props.editingDevice.production_date
      formData.status = props.editingDevice.status
      formData.owner = props.editingDevice.owner // Backend oczekuje ID
    } else {
      Object.assign(formData, initialFormData)
    }
  }
})

const rules = { required: (v: any) => !!v || 'Pole jest wymagane' }
const closeDialog = () => emit('update:modelValue', false)

const submitForm = async () => {
  const { valid } = await form.value!.validate()
  if (!valid) return

  isLoading.value = true
  error.value = null
  try {
    if (isEditing.value) {
      await devicesStore.updateDevice(props.editingDevice!.id, formData)
    } else {
      await devicesStore.addDevice(formData)
    }
    emit('save-success', isEditing.value ? 'Dane urządzenia zaktualizowane.' : 'Nowe urządzenie dodane.')
    closeDialog()
  } catch (err: any) {
    error.value = err.response?.data?.serial_number?.[0] || 'Wystąpił błąd serwera.'
  } finally {
    isLoading.value = false
  }
}
</script>
