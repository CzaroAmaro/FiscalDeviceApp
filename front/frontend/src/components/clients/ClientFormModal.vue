<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="700px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="client-form-card" rounded="lg">
      <div class="form-header">
        <div class="d-flex align-center">
          <v-avatar
            :color="isEditing ? 'primary' : 'success'"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">
              {{ isEditing ? 'mdi-domain' : 'mdi-domain-plus' }}
            </v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ formTitle }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ isEditing ? t('clients.forms.editSubtitle') : t('clients.forms.addSubtitle') }}
            </p>
          </div>
        </div>
        <v-btn
          icon
          variant="text"
          size="small"
          @click="closeDialog"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <v-divider />

      <v-card-text class="form-content">
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert
            v-if="fetchState.error"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-6"
            closable
            @click:close="fetchState.error = null"
          >
            <template #prepend>
              <v-icon>mdi-cloud-alert</v-icon>
            </template>
            {{ fetchState.error }}
          </v-alert>

          <v-alert
            v-if="state.error"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-6"
            closable
            @click:close="state.error = ''"
          >
            <template #prepend>
              <v-icon>mdi-alert-circle</v-icon>
            </template>
            {{ state.error }}
          </v-alert>

          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-card-account-details</v-icon>
              {{ t('clients.sections.identification') }}
            </h3>

            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.nip"
                  :label="t('clients.forms.nipLabel')"
                  :placeholder="t('clients.placeholders.nip')"
                  :rules="[rules.required, rules.nip]"
                  :loading="fetchState.isFetching"
                  :disabled="fetchState.isFetching || isEditing"
                  variant="outlined"
                  density="comfortable"
                  maxlength="10"
                  counter
                  @keydown.enter.prevent="fetchCompanyData"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-identifier</v-icon>
                  </template>
                  <template #append-inner>
                    <v-tooltip location="top">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          icon
                          size="small"
                          variant="text"
                          :loading="fetchState.isFetching"
                          :disabled="!formData.nip || formData.nip.length !== 10 || isEditing"
                          @click="fetchCompanyData"
                        >
                          <v-icon size="20">mdi-cloud-download</v-icon>
                        </v-btn>
                      </template>
                      {{ t('clients.actions.fetchFromGus') }}
                    </v-tooltip>
                  </template>
                </v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.regon"
                  :label="t('clients.forms.regonLabel')"
                  :placeholder="t('clients.placeholders.regon')"
                  variant="outlined"
                  density="comfortable"
                  readonly
                  :bg-color="formData.regon ? 'grey-lighten-4' : undefined"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-numeric</v-icon>
                  </template>
                  <template v-if="formData.regon" #append-inner>
                    <v-icon color="success" size="20">mdi-check-circle</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>

            <v-alert
              v-if="!isEditing"
              type="info"
              variant="tonal"
              density="compact"
              class="mt-2"
            >
              <template #prepend>
                <v-icon size="18">mdi-lightbulb</v-icon>
              </template>
              <span class="text-caption">
                {{ t('clients.hints.nipInfo') }}
              </span>
            </v-alert>
          </div>

          <v-divider class="my-6" />

          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-office-building</v-icon>
              {{ t('clients.sections.companyData') }}
            </h3>

            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.name"
                  :label="t('clients.forms.nameLabel')"
                  :placeholder="t('clients.placeholders.name')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-domain</v-icon>
                  </template>
                </v-text-field>
              </v-col>

              <v-col cols="12">
                <v-text-field
                  v-model="formData.address"
                  :label="t('clients.forms.addressLabel')"
                  :placeholder="t('clients.placeholders.address')"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-map-marker</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-card-account-phone</v-icon>
              {{ t('clients.sections.contactData') }}
            </h3>

            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.phone_number"
                  :label="t('clients.forms.phoneLabel')"
                  :placeholder="t('clients.placeholders.phone')"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-phone</v-icon>
                  </template>
                </v-text-field>
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.email"
                  :label="t('clients.forms.emailLabel')"
                  :placeholder="t('clients.placeholders.email')"
                  :rules="[rules.email]"
                  type="email"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-email</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </div>

          <div v-if="formData.name && formData.nip" class="preview-section mt-6">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-eye</v-icon>
              {{ t('common.preview') }}
            </h3>

            <v-card variant="outlined" class="preview-card">
              <div class="d-flex align-center pa-4">
                <v-avatar color="primary" size="56" variant="tonal" class="mr-4">
                  <span class="text-h6 font-weight-bold">
                    {{ getInitials(formData.name) }}
                  </span>
                </v-avatar>
                <div class="flex-grow-1">
                  <div class="d-flex align-center mb-1">
                    <span class="text-body-1 font-weight-bold">
                      {{ formData.name }}
                    </span>
                  </div>
                  <div class="d-flex flex-wrap ga-3">
                    <v-chip size="x-small" variant="tonal" color="primary">
                      <v-icon start size="12">mdi-identifier</v-icon>
                      NIP: {{ formData.nip }}
                    </v-chip>
                    <v-chip v-if="formData.address" size="x-small" variant="tonal">
                      <v-icon start size="12">mdi-map-marker</v-icon>
                      {{ truncateAddress(formData.address) }}
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-card>
          </div>
        </v-form>
      </v-card-text>

      <v-divider />

      <v-card-actions class="form-footer">
        <v-btn
          variant="text"
          @click="closeDialog"
        >
          {{ t('common.cancel') }}
        </v-btn>
        <v-spacer />
        <v-btn
          v-if="!isEditing"
          variant="tonal"
          color="grey"
          @click="handleResetForm"
        >
          <v-icon start>mdi-refresh</v-icon>
          {{ t('common.clear') }}
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :loading="state.isSaving"
          :disabled="!formData.name || !formData.nip"
          @click="handleFormSubmit"
        >
          <v-icon start>{{ isEditing ? 'mdi-content-save' : 'mdi-plus' }}</v-icon>
          {{ isEditing ? t('common.save') : t('clients.actions.add') }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <v-dialog v-model="showOverwriteDialog" max-width="400px">
      <v-card rounded="lg">
        <v-card-title class="d-flex align-center">
          <v-icon color="warning" class="mr-2">mdi-alert</v-icon>
          {{ t('clients.dialogs.overwriteTitle') }}
        </v-card-title>
        <v-card-text>
          {{ t('clients.dialogs.overwriteMessage') }}
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="showOverwriteDialog = false">
            {{ t('common.cancel') }}
          </v-btn>
          <v-btn color="warning" variant="flat" @click="confirmFetchCompanyData">
            {{ t('clients.actions.overwrite') }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useClientsStore } from '@/stores/clients';
import api from '@/api';
import type { Client, ClientPayload } from '@/types';

const props = defineProps<{
  modelValue: boolean;
  editingClient: Client | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string, newClient?: Client): void;
}>();

const { t } = useI18n();
const clientsStore = useClientsStore();
const display = useDisplay();

const isMobile = computed(() => display.smAndDown.value);

const formRef = ref<{ validate: () => Promise<{ valid: boolean }>; reset: () => void } | null>(null);

const state = ref({
  isSaving: false,
  error: '',
});

const fetchState = reactive({
  isFetching: false,
  error: null as string | null,
});

const showOverwriteDialog = ref(false);

const getInitialFormData = (): ClientPayload => ({
  name: '',
  address: '',
  nip: '',
  phone_number: '',
  email: '',
  regon: '',
  latitude: null,
  longitude: null,
});

const formData = ref<ClientPayload>(getInitialFormData());

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isEditing = computed(() => props.editingClient !== null);

const formTitle = computed(() =>
  isEditing.value
    ? t('clients.forms.editTitle')
    : t('clients.forms.addTitle')
);

const rules = {
  required: (v: string | null | undefined) => !!v?.trim() || t('validation.required'),
  nip: (v: string) => {
    if (!v) return true;
    const cleanNip = v.replace(/\D/g, '');
    return cleanNip.length === 10 || t('validation.nip');
  },
  email: (v: string) => {
    if (!v) return true;
    return /.+@.+\..+/.test(v) || t('validation.email');
  },
};

function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .filter(part => part.length > 0)
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function truncateAddress(address: string, maxLength: number = 30): string {
  if (!address) return '';
  return address.length > maxLength ? address.substring(0, maxLength) + '...' : address;
}

function isFormPartiallyFilled(): boolean {
  return !!(formData.value.name || formData.value.address || formData.value.regon);
}

function populateFormFromClient(client: Client) {
  formData.value = {
    name: client.name,
    address: client.address,
    nip: client.nip,
    phone_number: client.phone_number || '',
    email: client.email || '',
    regon: client.regon || '',
    latitude: client.latitude,
    longitude: client.longitude,
  };
}

function handleResetForm() {
  formData.value = getInitialFormData();
  state.value.error = '';
  fetchState.error = null;
}

function closeDialog() {
  emit('update:modelValue', false);
}

async function fetchCompanyData() {
  const nip = formData.value.nip;
  if (!nip || nip.replace(/\D/g, '').length !== 10) return;

  if (isFormPartiallyFilled()) {
    showOverwriteDialog.value = true;
    return;
  }

  await performFetchCompanyData();
}

async function confirmFetchCompanyData() {
  showOverwriteDialog.value = false;
  await performFetchCompanyData();
}

async function performFetchCompanyData() {
  const nip = formData.value.nip;

  fetchState.isFetching = true;
  fetchState.error = null;

  try {
    const cleanNip = nip.replace(/\D/g, '');

    interface CompanyDataResponse {
      name?: string;
      address?: string;
      nip?: string;
      regon?: string;
    }

    const response = await api.get<CompanyDataResponse>(`/external/company-data/${cleanNip}/`);

    if (response.data) {
      formData.value = {
        ...getInitialFormData(),
        nip: cleanNip,
        name: response.data.name || '',
        address: response.data.address || '',
        regon: response.data.regon || '',
      };
    }
  } catch (err: unknown) {
    const error = err as {
      response?: { data?: { detail?: string } };
      message?: string;
    };
    fetchState.error =
      error.response?.data?.detail ?? error.message ?? t('common.errors.serverError');
  } finally {
    fetchState.isFetching = false;
  }
}

async function handleFormSubmit() {
  const validation = await formRef.value?.validate();
  if (!validation?.valid) {
    return;
  }

  state.value.isSaving = true;
  state.value.error = '';

  try {
    let savedClient: Client | undefined;

    const payload: ClientPayload = {
      name: formData.value.name,
      address: formData.value.address,
      nip: formData.value.nip,
    };

    if (formData.value.phone_number) {
      payload.phone_number = formData.value.phone_number;
    }
    if (formData.value.email) {
      payload.email = formData.value.email;
    }
    if (formData.value.regon) {
      payload.regon = formData.value.regon;
    }

    if (isEditing.value && props.editingClient) {
      await clientsStore.updateClient(props.editingClient.id, payload);
    } else {
      savedClient = await clientsStore.addClient(payload);
    }

    const message = isEditing.value
      ? t('clients.forms.editSuccess')
      : t('clients.forms.addSuccess');

    emit('save-success', message, savedClient);
    closeDialog();
    clientsStore.fetchClients(true);
  } catch (error) {
    console.error('Error saving client:', error);
    state.value.error = error instanceof Error ? error.message : t('common.errors.unknown');
  } finally {
    state.value.isSaving = false;
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.editingClient) {
      populateFormFromClient(props.editingClient);
    } else {
      handleResetForm();
    }
  }
});

watch(() => props.editingClient, (newClient) => {
  if (newClient && props.modelValue) {
    populateFormFromClient(newClient);
  }
}, { immediate: true });
</script>

<style scoped>
.client-form-card {
  overflow: hidden;
}

.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.08) 0%,
    rgba(var(--v-theme-primary), 0.02) 100%
  );
}

.form-content {
  padding: 24px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

.form-section,
.preview-section {
  margin-bottom: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 16px;
}

.form-footer {
  padding: 16px 24px;
  background: rgb(var(--v-theme-surface));
}

.preview-card {
  border-radius: 12px;
  background: rgba(var(--v-theme-primary), 0.02);
  border-color: rgba(var(--v-theme-primary), 0.2);
  transition: all 0.3s ease;
}

.preview-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.4);
}

:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}

:deep(.v-field--disabled) {
  opacity: 0.8;
}

.form-content::-webkit-scrollbar {
  width: 6px;
}

.form-content::-webkit-scrollbar-track {
  background: transparent;
}

.form-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 3px;
}

.form-content::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.3);
}

@media (max-width: 600px) {
  .form-header {
    padding: 16px;
  }

  .form-content {
    padding: 16px;
    max-height: calc(100vh - 200px);
  }

  .form-footer {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .form-footer .v-btn {
    flex: 1;
    min-width: 120px;
  }
}
</style>
