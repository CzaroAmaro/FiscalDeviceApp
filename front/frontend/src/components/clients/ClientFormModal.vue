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
              <v-col cols="12">
                <v-text-field v-model="formData.name" label="Nazwa firmy/Imię i nazwisko" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.nip" label="NIP" :rules="[rules.required, rules.nip]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.phone_number" label="Numer telefonu" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formData.email" label="Adres e-mail" :rules="[rules.email]" />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formData.address" label="Adres" />
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
import { ref, reactive, watch, computed } from 'vue'
import { useClientsStore } from '@/stores/clients'
import type { Client } from '@/types'
import type { VForm } from 'vuetify/components'

const props = defineProps<{
  modelValue: boolean // v-model
  editingClient: Client | null
}>()

const emit = defineEmits(['update:modelValue', 'save-success'])

const clientsStore = useClientsStore()
const form = ref<VForm | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const initialFormData = { name: '', address: '', nip: '', phone_number: '', email: '' }
const formData = reactive({ ...initialFormData })

const isEditing = computed(() => !!props.editingClient)
const formTitle = computed(() => isEditing.value ? 'Edytuj dane klienta' : 'Dodaj nowego klienta')

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (isEditing.value) {
      Object.assign(formData, props.editingClient)
    } else {
      Object.assign(formData, initialFormData)
    }
  }
})

const rules = {
  required: (v: string) => !!v || 'Pole jest wymagane',
  nip: (v: string) => /^\d{10}$/.test(v) || 'NIP musi składać się z 10 cyfr',
  email: (v: string) => !v || /.+@.+\..+/.test(v) || 'Nieprawidłowy format e-mail',
}

const closeDialog = () => emit('update:modelValue', false)

const submitForm = async () => {
  const { valid } = await form.value!.validate()
  if (!valid) return

  isLoading.value = true
  error.value = null
  try {
    if (isEditing.value) {
      await clientsStore.updateClient(props.editingClient!.id, formData)
    } else {
      await clientsStore.addClient(formData)
    }
    emit('save-success', isEditing.value ? 'Dane klienta zaktualizowane.' : 'Nowy klient dodany.')
    closeDialog()
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Wystąpił błąd serwera.'
  } finally {
    isLoading.value = false
  }
}
</script>
