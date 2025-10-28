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
        <!-- Sekcja do pobierania danych -->
        <v-alert v-if="fetchError" type="error" density="compact" class="mb-4">{{ fetchError }}</v-alert>
        <v-text-field
          v-model="nipToFetch"
          :label="t('clients.forms.nipToFetchLabel')"
          :loading="isFetching"
          :disabled="isFetching || isEditing"
          :placeholder="t('clients.forms.nipPlaceholder')"
          append-inner-icon="mdi-cloud-download-outline"
          class="mb-4"
          @click:append-inner="fetchCompanyData"
          @keydown.enter.prevent="fetchCompanyData"
        >
          <template #details><div class="text-caption">{{ t('clients.forms.nipFetchHint') }}</div></template>
        </v-text-field>

        <v-divider class="mb-6"></v-divider>

        <!-- Główny formularz -->
        <v-form ref="form" @submit.prevent="submitForm">
          <v-alert v-if="formError" type="error" density="compact" class="mb-4">{{ formError }}</v-alert>
          <v-container class="pa-0">
            <v-row>
              <v-col cols="12">
                <v-text-field v-model="formData.name" :label="t('clients.forms.nameLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.nip" :label="t('clients.forms.nipLabel')" :rules="[rules.required, rules.nip]" readonly />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.regon" :label="t('clients.forms.regonLabel')" readonly />
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="formData.address" :label="t('clients.forms.addressLabel')" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.phone_number" :label="t('clients.forms.phoneLabel')" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.email" :label="t('clients.forms.emailLabel')" :rules="[rules.email]" />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" @click="closeDialog">{{ t('common.cancel') }}</v-btn>
        <v-btn color="primary" :loading="isSaving" @click="submitForm">{{ t('common.save') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useClientsStore, type ClientPayload } from '@/stores/clients';
import api from '@/api';
import type { Client } from '@/types';
import type { VForm } from 'vuetify/components';

const props = defineProps<{ modelValue: boolean; editingClient: Client | null; }>();
const emit = defineEmits<{(e: 'update:modelValue', value: boolean): void; (e: 'save-success', message: string, newClient?: Client): void;}>();

const { t } = useI18n();
const clientsStore = useClientsStore();
const form = ref<VForm | null>(null);

const isSaving = ref(false);
const formError = ref<string | null>(null);

const nipToFetch = ref('');
const isFetching = ref(false);
const fetchError = ref<string | null>(null);

const initialFormData: ClientPayload = { name: '', address: '', nip: '', phone_number: '', email: '', regon: '' };
const formData = reactive<ClientPayload>({ ...initialFormData });

const isEditing = computed(() => !!props.editingClient);
const formTitle = computed(() => isEditing.value ? t('clients.forms.editTitle') : t('clients.forms.addTitle'));

watch(() => props.modelValue, (isOpen) => {
  formError.value = null;
  fetchError.value = null;
  nipToFetch.value = '';
  if (isOpen) {
    if (props.editingClient) {
      Object.assign(formData, props.editingClient);
    } else {
      Object.assign(formData, initialFormData);
    }
  }
});

const rules = computed(() => ({
  required: (v: string) => !!v || t('validation.required'),
  nip: (v: string) => !v || /^\d{10}$/.test(v) || t('validation.nip'),
  email: (v: string) => !v || /.+@.+\..+/.test(v) || t('validation.email'),
}));

async function fetchCompanyData() {
  if (!nipToFetch.value) return;
  isFetching.value = true;
  fetchError.value = null;
  try {
    const cleanNip = nipToFetch.value.replace(/\D/g, '');
    const response = await api.get(`/company-data/${cleanNip}/`);
    const data = response.data;
    formData.name = data.name;
    formData.nip = data.nip;
    formData.regon = data.regon;
    formData.address = data.address;
    nipToFetch.value = '';
  } catch (err: any) {
    fetchError.value = err.response?.data?.detail || t('common.serverError');
  } finally {
    isFetching.value = false;
  }
}

const closeDialog = () => emit('update:modelValue', false);

async function submitForm() {
  const { valid } = await form.value!.validate();
  if (!valid) return;

  isSaving.value = true;
  formError.value = null;
  try {
    const payload = { ...formData };
    if (isEditing.value) {
      await clientsStore.updateClient(props.editingClient!.id, payload);
      emit('save-success', t('clients.forms.editSuccess'));
    } else {
      const newClient = await clientsStore.addClient(payload);
      emit('save-success', t('clients.forms.addSuccess'), newClient);
    }
    closeDialog();
  } catch (err: any) {
    const errorData = err.response?.data;
    if (errorData?.nip) {
      formError.value = `NIP: ${errorData.nip[0]}`;
    } else {
      formError.value = errorData?.detail || t('common.serverError');
    }
  } finally {
    isSaving.value = false;
  }
}
</script>
