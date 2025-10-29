<template>
  <v-dialog v-model="isDialogOpen" max-width="700px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <!-- Błąd przy pobieraniu danych -->
        <v-alert
          v-if="fetchState.error"
          type="error"
          density="compact"
          class="mb-4"
        >
          {{ fetchState.error }}
        </v-alert>

        <!-- Sekcja NIP -->
        <v-text-field
          v-model="nipToFetch"
          :label="t('clients.forms.nipToFetchLabel')"
          :loading="fetchState.isFetching"
          :disabled="fetchState.isFetching || isEditing"
          append-inner-icon="mdi-cloud-download-outline"
          class="mb-4"
          @click:append-inner="fetchCompanyData"
          @keydown.enter.prevent="fetchCompanyData"
        />

        <v-divider class="mb-6" />

        <!-- Formularz klienta -->
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert
            v-if="form.state.error"
            type="error"
            density="compact"
            class="mb-4"
          >
            {{ form.state.error }}
          </v-alert>

          <v-container class="pa-0">
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="form.formData.name"
                  :label="t('clients.forms.nameLabel')"
                  :rules="[rules.required]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.nip"
                  :label="t('clients.forms.nipLabel')"
                  :rules="[rules.required, rules.nip]"
                  readonly
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.regon"
                  :label="t('clients.forms.regonLabel')"
                  readonly
                />
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="form.formData.address"
                  :label="t('clients.forms.addressLabel')"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.phone_number"
                  :label="t('clients.forms.phoneLabel')"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.email"
                  :label="t('clients.forms.emailLabel')"
                  :rules="[rules.email]"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" text @click="closeDialog">
          {{ t('common.cancel') }}
        </v-btn>
        <v-btn
          color="primary"
          :loading="form.state.isSaving"
          @click="handleFormSubmit"
        >
          {{ t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n';
import { useClientsStore } from '@/stores/clients';
import { useForm } from '@/composables/useForm';
import api from '@/api';
import type { Client, ClientPayload } from '@/types';
import type { AxiosResponse } from 'axios';

/* =======================
   Props & Emits
======================= */
const props = defineProps<{
  modelValue: boolean;
  editingClient: Client | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string, newClient?: Client): void;
}>();

/* =======================
   Setup
======================= */
const { t } = useI18n();
const clientsStore = useClientsStore();

const { editingClient } = toRefs(props);

/**
 * useForm<Payload, Item | null, Result>
 * ✅ Poprawiony typ Ref<Client | null>
 *    pasuje do EditableItem<T> w composable
 */
const form = useForm<ClientPayload, Client | null, Client>(
  {
    name: '',
    address: '',
    nip: '',
    phone_number: '',
    email: '',
    regon: '',
  },
  editingClient,
  (payload) => clientsStore.addClient(payload),
  (id, payload) => clientsStore.updateClient(id, payload)
);

const { formRef, isEditing } = form;

/* =======================
   Fetch danych z NIP
======================= */
const nipToFetch = ref('');
const fetchState = reactive({
  isFetching: false,
  error: null as string | null,
});

async function fetchCompanyData() {
  if (!nipToFetch.value) return;

  fetchState.isFetching = true;
  fetchState.error = null;

  try {
    const cleanNip = nipToFetch.value.replace(/\D/g, '');

    // ✅ Typuj odpowiedź poprawnie
    const resp = await api.get<ClientPayload, AxiosResponse<ClientPayload>>(
      `/company-data/${cleanNip}/`
    );

    if (resp.data) {
      Object.assign(form.formData, resp.data);
    }
    nipToFetch.value = '';
  } catch (err: unknown) {
    const error = err as {
      response?: { data?: { detail?: string } };
      message?: string;
    };
    fetchState.error =
      error.response?.data?.detail ?? error.message ?? t('common.serverError');
  } finally {
    fetchState.isFetching = false;
  }
}

/* =======================
   Dialog logic
======================= */
const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => {
    emit('update:modelValue', val);
    if (val) {
      form.resetForm();
      fetchState.error = null;
      nipToFetch.value = '';
    }
  },
});

const formTitle = computed(() =>
  isEditing.value
    ? t('clients.forms.editTitle')
    : t('clients.forms.addTitle')
);

const rules = computed(() => ({
  required: (v: string) => !!v || t('validation.required'),
  nip: (v: string) => !v || /^\d{10}$/.test(v) || t('validation.nip'),
  email: (v: string) => !v || /.+@.+\..+/.test(v) || t('validation.email'),
}));

/* =======================
   Submit
======================= */
async function handleFormSubmit() {
  try {
    const result = await form.submit();
    const message = isEditing.value
      ? t('clients.forms.editSuccess')
      : t('clients.forms.addSuccess');

    emit('save-success', message, result);
    isDialogOpen.value = false;
  } catch (err) {
    console.error('Zapis nie powiódł się:', err);
  }
}

function closeDialog() {
  isDialogOpen.value = false;
}
</script>
