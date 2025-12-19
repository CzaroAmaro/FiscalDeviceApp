<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="800px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="device-form-card" rounded="lg">
      <!-- Nagłówek -->
      <div class="form-header">
        <div class="d-flex align-center">
          <v-avatar
            :color="isEditing ? 'primary' : 'success'"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">
              {{ isEditing ? 'mdi-printer-settings' : 'mdi-printer-pos-plus' }}
            </v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ formTitle }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ isEditing ? t('devices.forms.editSubtitle') : t('devices.forms.addSubtitle') }}
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

      <!-- Formularz -->
      <v-card-text class="form-content">
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <!-- Alert błędu -->
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

          <!-- Sekcja: Identyfikacja urządzenia -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-card-account-details</v-icon>
              {{ t('devices.sections.identification') }}
            </h3>

            <v-row dense>
              <!-- Marka/Producent -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="formData.brand"
                  :items="manufacturersStore.manufacturers"
                  item-title="name"
                  item-value="id"
                  :label="t('devices.forms.brandLabel')"
                  :placeholder="t('devices.placeholders.brand')"
                  :rules="[rules.required]"
                  :loading="manufacturersStore.isLoading"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-factory</v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar color="secondary" size="32" variant="tonal">
                          <span class="text-caption font-weight-bold">
                            {{ getInitials(item.raw.name) }}
                          </span>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #append-inner>
                    <v-tooltip location="top">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          icon
                          size="x-small"
                          variant="text"
                          color="primary"
                          @click.stop="isManufacturerModalOpen = true"
                        >
                          <v-icon size="18">mdi-plus</v-icon>
                        </v-btn>
                      </template>
                      {{ t('devices.actions.addManufacturer') }}
                    </v-tooltip>
                  </template>
                </v-select>
              </v-col>

              <!-- Model -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.model_name"
                  :label="t('devices.forms.modelLabel')"
                  :placeholder="t('devices.placeholders.model')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-printer-pos</v-icon>
                  </template>
                </v-text-field>
              </v-col>

              <!-- Numer unikatowy -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.unique_number"
                  :label="t('devices.forms.uniqueNumberLabel')"
                  :placeholder="t('devices.placeholders.uniqueNumber')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-identifier</v-icon>
                  </template>
                </v-text-field>
              </v-col>

              <!-- Numer seryjny -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.serial_number"
                  :label="t('devices.forms.serialLabel')"
                  :placeholder="t('devices.placeholders.serial')"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-barcode</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Właściciel -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-domain</v-icon>
              {{ t('devices.sections.owner') }}
            </h3>

            <v-row dense>
              <v-col cols="12">
                <v-autocomplete
                  v-model="formData.owner"
                  :items="clientsStore.clients"
                  item-title="name"
                  item-value="id"
                  :label="t('devices.forms.ownerLabel')"
                  :placeholder="t('devices.placeholders.owner')"
                  :rules="[rules.required]"
                  :loading="clientsStore.isLoading"
                  variant="outlined"
                  density="comfortable"
                  clearable
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-office-building</v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar color="primary" size="32" variant="tonal">
                          <span class="text-caption font-weight-bold">
                            {{ getInitials(item.raw.name) }}
                          </span>
                        </v-avatar>
                      </template>
                      <template #subtitle>
                        <span class="text-caption">NIP: {{ item.raw.nip }}</span>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <div class="d-flex align-center">
                      <v-avatar color="primary" size="24" variant="tonal" class="mr-2">
                        <span style="font-size: 10px;" class="font-weight-bold">
                          {{ getInitials(item.raw.name) }}
                        </span>
                      </v-avatar>
                      <div>
                        <span>{{ item.raw.name }}</span>
                        <span class="text-caption text-medium-emphasis ml-2">
                          ({{ item.raw.nip }})
                        </span>
                      </div>
                    </div>
                  </template>
                  <template #append-inner>
                    <v-tooltip location="top">
                      <template #activator="{ props: tooltipProps }">
                        <v-btn
                          v-bind="tooltipProps"
                          icon
                          size="x-small"
                          variant="text"
                          color="primary"
                          @click.stop="$emit('request-new-client')"
                        >
                          <v-icon size="18">mdi-plus</v-icon>
                        </v-btn>
                      </template>
                      {{ t('devices.actions.addClient') }}
                    </v-tooltip>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>

            <!-- Alert gdy wybrano klienta -->
            <v-expand-transition>
              <v-alert
                v-if="selectedClient"
                type="info"
                variant="tonal"
                density="compact"
                class="mt-4"
              >
                <template #prepend>
                  <v-icon size="18">mdi-information</v-icon>
                </template>
                <div class="d-flex align-center justify-space-between">
                  <span class="text-caption">
                    {{ t('devices.hints.clientSelected', { name: selectedClient.name }) }}
                  </span>
                  <v-chip size="x-small" variant="tonal" color="primary">
                    {{ clientDevicesCount }} {{ t('devices.labels.devicesCount') }}
                  </v-chip>
                </div>
              </v-alert>
            </v-expand-transition>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Status i daty -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-calendar-clock</v-icon>
              {{ t('devices.sections.statusAndDates') }}
            </h3>

            <v-row dense>
              <!-- Status -->
              <v-col cols="12" sm="4">
                <v-select
                  v-model="formData.status"
                  :items="statusOptions"
                  :label="t('devices.forms.statusLabel')"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon :color="getStatusColor(formData.status)" size="20">
                      {{ getStatusIcon(formData.status) }}
                    </v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar
                          :color="getStatusColor(item.raw.value)"
                          size="32"
                          variant="tonal"
                        >
                          <v-icon size="16">{{ getStatusIcon(item.raw.value) }}</v-icon>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <v-chip
                      :color="getStatusColor(item.raw.value)"
                      size="small"
                      variant="tonal"
                    >
                      <v-icon start size="14">{{ getStatusIcon(item.raw.value) }}</v-icon>
                      {{ item.title }}
                    </v-chip>
                  </template>
                </v-select>
              </v-col>

              <!-- Data sprzedaży -->
              <v-col cols="12" sm="4">
                <DatePicker
                  v-model="formData.sale_date"
                  :label="t('devices.forms.saleDateLabel')"
                  :rules="[rules.required]"
                  prepend-inner-icon="mdi-calendar-check"
                />
              </v-col>

              <!-- Data ostatniego serwisu -->
              <v-col cols="12" sm="4">
                <DatePicker
                  v-model="formData.last_service_date"
                  :label="t('devices.forms.lastServiceDateLabel')"
                  prepend-inner-icon="mdi-calendar-clock"
                  clearable
                />
              </v-col>
            </v-row>

            <!-- Alert o statusie -->
            <v-expand-transition>
              <v-alert
                v-if="formData.status === 'decommissioned'"
                type="warning"
                variant="tonal"
                density="compact"
                class="mt-4"
              >
                <template #prepend>
                  <v-icon size="18">mdi-alert</v-icon>
                </template>
                <span class="text-caption">
                  {{ t('devices.warnings.decommissioned') }}
                </span>
              </v-alert>
            </v-expand-transition>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Dodatkowe informacje -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-text-box-multiple</v-icon>
              {{ t('devices.sections.additionalInfo') }}
            </h3>

            <v-row dense>
              <!-- Instrukcja obsługi -->
              <v-col cols="12">
                <v-textarea
                  v-model="formData.operating_instructions"
                  :label="t('devices.forms.instructionsLabel')"
                  :placeholder="t('devices.placeholders.instructions')"
                  variant="outlined"
                  density="comfortable"
                  rows="2"
                  auto-grow
                  counter
                  maxlength="1000"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20" class="mt-1">mdi-file-document</v-icon>
                  </template>
                </v-textarea>
              </v-col>

              <!-- Uwagi -->
              <v-col cols="12">
                <v-textarea
                  v-model="formData.remarks"
                  :label="t('devices.forms.remarksLabel')"
                  :placeholder="t('devices.placeholders.remarks')"
                  variant="outlined"
                  density="comfortable"
                  rows="2"
                  auto-grow
                  counter
                  maxlength="500"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20" class="mt-1">mdi-note-text</v-icon>
                  </template>
                </v-textarea>
              </v-col>
            </v-row>
          </div>

          <!-- Podgląd urządzenia -->
          <div v-if="formData.model_name && formData.unique_number" class="preview-section mt-6">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-eye</v-icon>
              {{ t('common.preview') }}
            </h3>

            <v-card variant="outlined" class="preview-card">
              <div class="d-flex align-center pa-4">
                <v-avatar
                  :color="getStatusColor(formData.status)"
                  size="56"
                  variant="tonal"
                  class="mr-4"
                >
                  <v-icon size="28">mdi-printer-pos</v-icon>
                </v-avatar>
                <div class="flex-grow-1">
                  <div class="d-flex align-center flex-wrap ga-2 mb-2">
                    <span class="text-body-1 font-weight-bold">
                      {{ selectedBrandName }} {{ formData.model_name }}
                    </span>
                    <v-chip
                      :color="getStatusColor(formData.status)"
                      size="x-small"
                      variant="tonal"
                    >
                      {{ getStatusLabel(formData.status) }}
                    </v-chip>
                  </div>
                  <div class="d-flex flex-wrap ga-3">
                    <v-chip size="x-small" variant="tonal" color="primary">
                      <v-icon start size="12">mdi-identifier</v-icon>
                      {{ formData.unique_number }}
                    </v-chip>
                    <v-chip v-if="formData.serial_number" size="x-small" variant="tonal">
                      <v-icon start size="12">mdi-barcode</v-icon>
                      {{ formData.serial_number }}
                    </v-chip>
                    <v-chip v-if="selectedClient" size="x-small" variant="tonal">
                      <v-icon start size="12">mdi-domain</v-icon>
                      {{ selectedClient.name }}
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-card>
          </div>
        </v-form>
      </v-card-text>

      <v-divider />

      <!-- Stopka -->
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
          :disabled="!isFormValid"
          @click="handleFormSubmit"
        >
          <v-icon start>{{ isEditing ? 'mdi-content-save' : 'mdi-plus' }}</v-icon>
          {{ isEditing ? t('common.save') : t('devices.actions.add') }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Modal dodawania producenta -->
    <ManufacturerFormModal
      v-model="isManufacturerModalOpen"
      :editing-manufacturer="null"
      @save-success="onManufacturerSaveSuccess"
    />
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useDevicesStore } from '@/stores/devices';
import { useClientsStore } from '@/stores/clients';
import { useManufacturersStore } from '@/stores/manufacturers';
import { useSnackbarStore } from '@/stores/snackbar';
import type { FiscalDevice, DevicePayload, Manufacturer, Client } from '@/types';
import ManufacturerFormModal from '@/components/manufacturers/ManufacturerFormModal.vue';
import DatePicker from '@/components/common/DatePicker.vue';

// Props & Emits
const props = defineProps<{
  modelValue: boolean;
  editingDevice: FiscalDevice | null;
  newlyAddedClientId: number | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
  (e: 'request-new-client'): void;
}>();

// Composables
const { t } = useI18n();
const devicesStore = useDevicesStore();
const clientsStore = useClientsStore();
const manufacturersStore = useManufacturersStore();
const snackbarStore = useSnackbarStore();
const display = useDisplay();

// Responsive
const isMobile = computed(() => display.smAndDown.value);

// Refs
const formRef = ref<{ validate: () => Promise<{ valid: boolean }>; reset: () => void } | null>(null);
const isManufacturerModalOpen = ref(false);

// State
const state = ref({
  isSaving: false,
  error: '',
});

// Initial form data
const getInitialFormData = (): DevicePayload => ({
  brand: 0,
  model_name: '',
  unique_number: '',
  serial_number: '',
  sale_date: '',
  last_service_date: null,
  status: 'active',
  operating_instructions: '',
  remarks: '',
  owner: 0,
});

// Form data
const formData = ref<DevicePayload>(getInitialFormData());

// Computed
const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isEditing = computed(() => props.editingDevice !== null);

const formTitle = computed(() =>
  isEditing.value
    ? t('devices.forms.editTitle')
    : t('devices.forms.addTitle')
);

const isFormValid = computed(() => {
  return formData.value.brand > 0 &&
    formData.value.model_name.trim() !== '' &&
    formData.value.unique_number.trim() !== '' &&
    formData.value.owner > 0 &&
    formData.value.sale_date !== '';
});

const selectedClient = computed<Client | undefined>(() => {
  if (!formData.value.owner) return undefined;
  return clientsStore.clients.find(c => c.id === formData.value.owner);
});

const selectedBrandName = computed(() => {
  if (!formData.value.brand) return '';
  const brand = manufacturersStore.manufacturers.find(m => m.id === formData.value.brand);
  return brand?.name || '';
});

const clientDevicesCount = computed(() => {
  if (!selectedClient.value) return 0;
  return devicesStore.devices.filter(d => d.owner.id === selectedClient.value?.id).length;
});

const statusOptions = computed(() => [
  { title: t('devices.forms.statusOptions.active'), value: 'active' },
  { title: t('devices.forms.statusOptions.inactive'), value: 'inactive' },
  { title: t('devices.forms.statusOptions.serviced'), value: 'serviced' },
  { title: t('devices.forms.statusOptions.decommissioned'), value: 'decommissioned' },
]);

// Validation rules
const rules = {
  required: (v: unknown) => {
    if (typeof v === 'number') return v > 0 || t('validation.required');
    if (typeof v === 'string') return v.trim() !== '' || t('validation.required');
    return !!v || t('validation.required');
  },
};

// Methods
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

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'success',
    inactive: 'grey',
    serviced: 'warning',
    decommissioned: 'error',
  };
  return colors[status] || 'grey';
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    active: 'mdi-check-circle',
    inactive: 'mdi-pause-circle',
    serviced: 'mdi-wrench',
    decommissioned: 'mdi-cancel',
  };
  return icons[status] || 'mdi-help-circle';
}

function getStatusLabel(status: string): string {
  const option = statusOptions.value.find(o => o.value === status);
  return option?.title || status;
}

function populateFormFromDevice(device: FiscalDevice) {
  formData.value = {
    brand: device.brand.id,
    model_name: device.model_name,
    unique_number: device.unique_number,
    serial_number: device.serial_number,
    sale_date: device.sale_date,
    last_service_date: device.last_service_date || null,
    status: device.status,
    operating_instructions: device.operating_instructions,
    remarks: device.remarks,
    owner: device.owner.id,
  };
}

function handleResetForm() {
  formData.value = getInitialFormData();
  state.value.error = '';
}

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  const validation = await formRef.value?.validate();
  if (!validation?.valid) {
    return;
  }

  state.value.isSaving = true;
  state.value.error = '';

  try {
    const payload: DevicePayload = {
      ...formData.value,
      owner: Number(formData.value.owner),
      brand: Number(formData.value.brand),
    };

    if (isEditing.value && props.editingDevice) {
      await devicesStore.updateDevice(props.editingDevice.id, payload);
    } else {
      await devicesStore.addDevice(payload);
    }

    const message = isEditing.value
      ? t('devices.forms.editSuccess')
      : t('devices.forms.addSuccess');

    emit('save-success', message);
    closeDialog();
    devicesStore.fetchDevices(true);
  } catch (error) {
    console.error('Błąd zapisu urządzenia:', error);
    state.value.error = error instanceof Error ? error.message : t('common.errors.unknown');
  } finally {
    state.value.isSaving = false;
  }
}

function onManufacturerSaveSuccess(message: string, newManufacturer?: Manufacturer) {
  snackbarStore.showSuccess(message);
  manufacturersStore.fetchManufacturers(true);
  if (newManufacturer) {
    formData.value.brand = newManufacturer.id;
  }
}

// Watchers
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.editingDevice) {
      populateFormFromDevice(props.editingDevice);
    } else {
      handleResetForm();
      // Ustaw właściciela, jeśli dopiero dodany klient
      if (props.newlyAddedClientId) {
        formData.value.owner = props.newlyAddedClientId;
      }
    }
  }
});

watch(() => props.editingDevice, (newDevice) => {
  if (newDevice && props.modelValue) {
    populateFormFromDevice(newDevice);
  }
}, { immediate: true });

// Lifecycle
onMounted(() => {
  clientsStore.fetchClients();
  manufacturersStore.fetchManufacturers();
});
</script>

<style scoped>
.device-form-card {
  overflow: hidden;
}

/* Header */
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

/* Content */
.form-content {
  padding: 24px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

/* Section */
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

/* Footer */
.form-footer {
  padding: 16px 24px;
  background: rgb(var(--v-theme-surface));
}

/* Preview card */
.preview-card {
  border-radius: 12px;
  background: rgba(var(--v-theme-primary), 0.02);
  border-color: rgba(var(--v-theme-primary), 0.2);
  transition: all 0.3s ease;
}

.preview-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.4);
}

/* Form fields */
:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}

/* Textarea icon alignment */
:deep(.v-textarea .v-field__prepend-inner) {
  padding-top: 12px;
  align-items: flex-start;
}

/* Scrollbar */
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

/* Mobile */
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

/* Transitions */
.v-expand-transition-enter-active,
.v-expand-transition-leave-active {
  transition: all 0.3s ease;
}
</style>
