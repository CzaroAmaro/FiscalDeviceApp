<template>
  <v-dialog
    :model-value="modelValue"
    max-width="700px"
    persistent
    @update:model-value="closeDialog"
  >
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="form" @submit.prevent="submitForm">
          <v-alert
            v-if="fetchError"
            type="error"
            density="compact"
            class="mb-4"
          >
            {{ fetchError }}
          </v-alert>

          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.name"
                  :label="t('clients.forms.nameLabel')"
                  :rules="[rules.required]"
                />
              </v-col>

              <!-- --- ZMIANA: Modyfikujemy pole NIP, aby było interaktywne --- -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.nip"
                  :label="t('clients.forms.nipLabel')"
                  :rules="[rules.required, rules.nip]"
                  :loading="isFetching"
                  :disabled="isFetching"
                  append-inner-icon="mdi-cloud-download-outline"
                  @click:append-inner="fetchCompanyData"
                  @keydown.enter.prevent="fetchCompanyData"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.regon"
                  :label="t('clients.forms.regonLabel')"
                  readonly
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.phone_number"
                  :label="t('clients.forms.phoneLabel')"
                />
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="formData.email"
                  :label="t('clients.forms.emailLabel')"
                  :rules="[rules.email]"
                />
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="formData.address"
                  :label="t('clients.forms.addressLabel')"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" @click="closeDialog">
          {{ t('common.cancel') }}
        </v-btn>
        <v-btn color="primary" :loading="isLoading" @click="submitForm">
          {{ t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useClientsStore } from '@/stores/clients'
import type { Client } from '@/types'
import type { VForm } from 'vuetify/components'
import api from '@/api'

const props = defineProps<{
  modelValue: boolean
  editingClient: Client | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'save-success', message: string, newClient?: Client): void
}>()

const { t } = useI18n()

const clientsStore = useClientsStore()
const form = ref<VForm | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

const isFetching = ref(false);
const fetchError = ref<string | null>(null);

const initialFormData: Omit<Client, 'id' | 'created_at'> = {
  name: '',
  address: '',
  nip: '',
  phone_number: '',
  email: '',
  regon: '',
}

const formData = reactive({ ...initialFormData })

const isEditing = computed(() => Boolean(props.editingClient))
const formTitle = computed(() =>
  isEditing.value ? t('clients.forms.editTitle') : t('clients.forms.addTitle')
)

watchEffect(() => {
  fetchError.value = null;
  if (!props.modelValue) return
  Object.assign(
    formData,
    props.editingClient ?? initialFormData
  )
})

interface ApiError {
  response?: { data?: { detail?: string } }
}

const rules = computed(() => ({
  required: (v: string) => !!v || t('validation.required'),
  nip: (v: string) => /^\d{10}$/.test(v) || t('validation.nip'),
  email: (v: string) => !v || /.+@.+\..+/.test(v) || t('validation.email'),
}))

async function fetchCompanyData() {
  if (!formData.nip) return;

  isFetching.value = true;
  fetchError.value = null;
  try {
    const cleanNip = formData.nip.replace(/\D/g, '');
    const response = await api.get(`/company-data/${cleanNip}/`);
    const data = response.data;

    formData.name = data.name;
    formData.regon = data.regon;
    formData.address = data.address;

    // Opcjonalnie: możemy też zaktualizować NIP, jeśli API go sformatowało
    formData.nip = data.nip;

  } catch (err: any) {
    fetchError.value = err.response?.data?.detail || t('common.serverError');
  } finally {
    isFetching.value = false;
  }
}

const closeDialog = () => emit('update:modelValue', false)

async function submitForm() {
  const { valid } = await form.value?.validate() ?? { valid: false }
  if (!valid) return

  isLoading.value = true
  error.value = null

  try {
    const messageKey = isEditing.value
      ? 'clients.forms.editSuccess'
      : 'clients.forms.addSuccess'

    const payload = { ...formData };

    const newClient = isEditing.value
      ? (await clientsStore.updateClient(props.editingClient!.id, payload), undefined)
      : await clientsStore.addClient(payload)

    emit('save-success', t(messageKey), newClient)
    closeDialog()
  } catch (err) {
    const e = err as ApiError
    error.value = e.response?.data?.detail ?? t('common.serverError')
  } finally {
    isLoading.value = false
  }
}
</script>
