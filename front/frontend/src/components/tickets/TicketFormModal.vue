<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="850px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="ticket-form-card" rounded="lg">
      <!-- Nagłówek -->
      <div class="form-header">
        <div class="d-flex align-center">
          <v-avatar
            :color="isEditing ? 'primary' : 'success'"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">
              {{ isEditing ? 'mdi-clipboard-edit' : 'mdi-clipboard-plus' }}
            </v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ formTitle }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ isEditing ? t('tickets.forms.editSubtitle') : t('tickets.forms.addSubtitle') }}
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

          <!-- Sekcja: Podstawowe informacje -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-information</v-icon>
              {{ t('tickets.sections.basicInfo') }}
            </h3>

            <v-row dense>
              <!-- Tytuł -->
              <v-col cols="12">
                <v-text-field
                  v-model="formData.title"
                  :label="t('tickets.forms.titleLabel')"
                  :placeholder="t('tickets.placeholders.title')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-format-title</v-icon>
                  </template>
                </v-text-field>
              </v-col>

              <!-- Opis -->
              <v-col cols="12">
                <v-textarea
                  v-model="formData.description"
                  :label="t('tickets.forms.descriptionLabel')"
                  :placeholder="t('tickets.placeholders.description')"
                  variant="outlined"
                  density="comfortable"
                  rows="3"
                  auto-grow
                  counter
                  maxlength="2000"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20" class="mt-1">mdi-text</v-icon>
                  </template>
                </v-textarea>

                <!-- Przycisk AI -->
                <v-btn
                  size="small"
                  variant="tonal"
                  color="info"
                  class="mt-2"
                  :disabled="!formData.description || formData.description.length < 10"
                  @click="isAiModalOpen = true"
                >
                  <v-icon start size="18">mdi-robot-happy-outline</v-icon>
                  {{ t('tickets.actions.analyzeWithAi') }}
                </v-btn>
              </v-col>

              <!-- Typ zgłoszenia -->
              <v-col cols="12" sm="6">
                <v-select
                  v-model="formData.ticket_type"
                  :items="typeOptions"
                  :label="t('tickets.forms.typeLabel')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon :color="getTypeColor(formData.ticket_type)" size="20">
                      {{ getTypeIcon(formData.ticket_type) }}
                    </v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar
                          :color="getTypeColor(item.raw.value)"
                          size="32"
                          variant="tonal"
                        >
                          <v-icon size="16">{{ getTypeIcon(item.raw.value) }}</v-icon>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <v-chip
                      :color="getTypeColor(item.raw.value)"
                      size="small"
                      variant="tonal"
                    >
                      <v-icon start size="14">{{ getTypeIcon(item.raw.value) }}</v-icon>
                      {{ item.title }}
                    </v-chip>
                  </template>
                </v-select>
              </v-col>

              <!-- Data zaplanowana -->
              <v-col cols="12" sm="6">
                <DatePicker
                  v-model="formData.scheduled_for"
                  :label="t('tickets.forms.scheduledLabel')"
                  prepend-inner-icon="mdi-calendar-clock"
                  clearable
                />
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Klient i urządzenie -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-domain</v-icon>
              {{ t('tickets.sections.clientAndDevice') }}
            </h3>

            <v-row dense>
              <!-- Klient -->
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="formData.client"
                  :items="clientsStore.clients"
                  :loading="clientsStore.isLoading"
                  item-title="name"
                  item-value="id"
                  :label="t('tickets.forms.clientLabel')"
                  :placeholder="t('tickets.placeholders.client')"
                  :rules="[rules.required]"
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
                      {{ item.raw.name }}
                    </div>
                  </template>
                </v-autocomplete>
              </v-col>

              <!-- Urządzenie -->
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="formData.device"
                  :items="devicesForSelectedClient"
                  :loading="devicesStore.isLoading"
                  item-title="displayName"
                  item-value="id"
                  :label="t('tickets.forms.deviceLabel')"
                  :placeholder="t('tickets.placeholders.device')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                  clearable
                  :disabled="!formData.client"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-printer-pos</v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar color="secondary" size="32" variant="tonal">
                          <v-icon size="16">mdi-printer-pos</v-icon>
                        </v-avatar>
                      </template>
                      <template #subtitle>
                        <div class="d-flex align-center ga-2">
                          <v-chip size="x-small" variant="tonal">
                            {{ item.raw.unique_number }}
                          </v-chip>
                          <DeviceStatusChip :status="item.raw.status" />
                        </div>
                      </template>
                    </v-list-item>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>

            <!-- Alert gdy nie wybrano klienta -->
            <v-alert
              v-if="!formData.client"
              type="info"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              <template #prepend>
                <v-icon size="18">mdi-information</v-icon>
              </template>
              <span class="text-caption">
                {{ t('tickets.hints.selectClientFirst') }}
              </span>
            </v-alert>

            <!-- Info o wybranym urządzeniu -->
            <v-expand-transition>
              <v-alert
                v-if="selectedDevice && selectedDevice.status === 'serviced'"
                type="warning"
                variant="tonal"
                density="compact"
                class="mt-4"
              >
                <template #prepend>
                  <v-icon size="18">mdi-alert</v-icon>
                </template>
                <span class="text-caption">
                  {{ t('tickets.warnings.deviceInService') }}
                </span>
              </v-alert>
            </v-expand-transition>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Przypisanie -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-account-hard-hat</v-icon>
              {{ t('tickets.sections.assignment') }}
            </h3>

            <v-row dense>
              <!-- Serwisant -->
              <v-col cols="12">
                <v-autocomplete
                  v-model="formData.assigned_technician"
                  :items="activeTechnicians"
                  :loading="techniciansStore.isLoading"
                  item-title="full_name"
                  item-value="id"
                  :label="t('tickets.forms.technicianLabel')"
                  :placeholder="t('tickets.placeholders.technician')"
                  variant="outlined"
                  density="comfortable"
                  clearable
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-account</v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar
                          :color="item.raw.is_active ? 'success' : 'grey'"
                          size="32"
                          variant="tonal"
                        >
                          <span class="text-caption font-weight-bold">
                            {{ getInitials(item.raw.full_name) }}
                          </span>
                        </v-avatar>
                      </template>
                      <template #subtitle>
                        <v-chip
                          size="x-small"
                          :color="item.raw.role === 'admin' ? 'error' : 'primary'"
                          variant="tonal"
                        >
                          {{ item.raw.role === 'admin' ? 'Administrator' : 'Serwisant' }}
                        </v-chip>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <div class="d-flex align-center">
                      <v-avatar color="success" size="24" variant="tonal" class="mr-2">
                        <span style="font-size: 10px;" class="font-weight-bold">
                          {{ getInitials(item.raw.full_name) }}
                        </span>
                      </v-avatar>
                      {{ item.raw.full_name }}
                    </div>
                  </template>
                </v-autocomplete>
              </v-col>
            </v-row>

            <!-- Podpowiedź o przypisaniu -->
            <v-alert
              v-if="!formData.assigned_technician"
              type="info"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              <template #prepend>
                <v-icon size="18">mdi-lightbulb</v-icon>
              </template>
              <span class="text-caption">
                {{ t('tickets.hints.noTechnicianAssigned') }}
              </span>
            </v-alert>
          </div>

          <!-- Podgląd zgłoszenia -->
          <div v-if="formData.title && formData.client && formData.device" class="preview-section mt-6">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-eye</v-icon>
              {{ t('common.preview') }}
            </h3>

            <v-card variant="outlined" class="preview-card">
              <div class="pa-4">
                <div class="d-flex align-center justify-space-between mb-3">
                  <div class="d-flex align-center">
                    <v-avatar
                      :color="getTypeColor(formData.ticket_type)"
                      size="40"
                      variant="tonal"
                      class="mr-3"
                    >
                      <v-icon size="20">{{ getTypeIcon(formData.ticket_type) }}</v-icon>
                    </v-avatar>
                    <div>
                      <span class="text-body-1 font-weight-bold">{{ formData.title }}</span>
                      <div class="d-flex align-center ga-2 mt-1">
                        <v-chip
                          :color="getTypeColor(formData.ticket_type)"
                          size="x-small"
                          variant="tonal"
                        >
                          {{ getTypeLabel(formData.ticket_type) }}
                        </v-chip>
                        <v-chip size="x-small" color="info" variant="tonal">
                          <v-icon start size="10">mdi-clock</v-icon>
                          {{ t('tickets.status.open') }}
                        </v-chip>
                      </div>
                    </div>
                  </div>
                </div>

                <v-divider class="my-3" />

                <div class="d-flex flex-wrap ga-4">
                  <div class="d-flex align-center">
                    <v-icon size="16" color="grey" class="mr-2">mdi-office-building</v-icon>
                    <span class="text-caption">{{ selectedClientName }}</span>
                  </div>
                  <div class="d-flex align-center">
                    <v-icon size="16" color="grey" class="mr-2">mdi-printer-pos</v-icon>
                    <span class="text-caption">{{ selectedDeviceName }}</span>
                  </div>
                  <div v-if="formData.assigned_technician" class="d-flex align-center">
                    <v-icon size="16" color="grey" class="mr-2">mdi-account</v-icon>
                    <span class="text-caption">{{ selectedTechnicianName }}</span>
                  </div>
                  <div v-if="formData.scheduled_for" class="d-flex align-center">
                    <v-icon size="16" color="grey" class="mr-2">mdi-calendar</v-icon>
                    <span class="text-caption">{{ formatDate(formData.scheduled_for) }}</span>
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
          {{ isEditing ? t('common.save') : t('tickets.actions.add') }}
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Modal AI -->
    <AiSuggestionModal
      v-model="isAiModalOpen"
      :description="formData.description"
    />
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useTicketsStore } from '@/stores/tickets';
import { useClientsStore } from '@/stores/clients';
import { useDevicesStore } from '@/stores/devices';
import { useTechniciansStore } from '@/stores/technicians';
import type { ServiceTicket, ServiceTicketPayload, FiscalDevice } from '@/types';
import DatePicker from '@/components/common/DatePicker.vue';
import DeviceStatusChip from '@/components/devices/DeviceStatusChip.vue';
import AiSuggestionModal from '@/components/ai/AiSuggestionModal.vue';

// Props & Emits
const props = defineProps<{
  modelValue: boolean;
  editingTicket: ServiceTicket | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

// Composables
const { t } = useI18n();
const ticketsStore = useTicketsStore();
const clientsStore = useClientsStore();
const devicesStore = useDevicesStore();
const techniciansStore = useTechniciansStore();
const display = useDisplay();

// Responsive
const isMobile = computed(() => display.smAndDown.value);

// Refs
const formRef = ref<{ validate: () => Promise<{ valid: boolean }>; reset: () => void } | null>(null);
const isAiModalOpen = ref(false);

// State
const state = ref({
  isSaving: false,
  error: '',
});

// Initial form data
const getInitialFormData = (): ServiceTicketPayload => ({
  title: '',
  description: '',
  ticket_type: 'service',
  status: 'open',
  client: 0,
  device: 0,
  assigned_technician: null,
  scheduled_for: null,
  resolution_notes: '',
});

// Form data
const formData = ref<ServiceTicketPayload>(getInitialFormData());

// Computed
const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isEditing = computed(() => props.editingTicket !== null);

const formTitle = computed(() =>
  isEditing.value ? t('tickets.forms.editTitle') : t('tickets.forms.addTitle')
);

const isFormValid = computed(() => {
  return formData.value.title.trim() !== '' &&
    formData.value.client > 0 &&
    formData.value.device > 0 &&
    formData.value.ticket_type !== '';
});

const devicesForSelectedClient = computed(() => {
  if (!formData.value.client) return [];
  return devicesStore.devices
    .filter(device => device.owner.id === formData.value.client)
    .map(device => ({
      ...device,
      displayName: `${device.brand.name} ${device.model_name} (${device.unique_number})`
    }));
});

const activeTechnicians = computed(() =>
  techniciansStore.technicians.filter(t => t.is_active)
);

const selectedDevice = computed<FiscalDevice | undefined>(() => {
  if (!formData.value.device) return undefined;
  return devicesStore.devices.find(d => d.id === formData.value.device);
});

const selectedClientName = computed(() => {
  const client = clientsStore.clients.find(c => c.id === formData.value.client);
  return client?.name || '';
});

const selectedDeviceName = computed(() => {
  return selectedDevice.value
    ? `${selectedDevice.value.brand.name} ${selectedDevice.value.model_name}`
    : '';
});

const selectedTechnicianName = computed(() => {
  const tech = techniciansStore.technicians.find(t => t.id === formData.value.assigned_technician);
  return tech?.full_name || '';
});

const typeOptions = computed(() => [
  { title: t('tickets.types.service'), value: 'service' },
  { title: t('tickets.types.reading'), value: 'reading' },
  { title: t('tickets.types.repair'), value: 'repair' },
  { title: t('tickets.types.other'), value: 'other' },
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

function getTypeColor(type: string): string {
  const colors: Record<string, string> = {
    service: 'info',
    reading: 'success',
    repair: 'error',
    other: 'grey',
  };
  return colors[type] || 'grey';
}

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    service: 'mdi-wrench',
    reading: 'mdi-file-document-check',
    repair: 'mdi-hammer-wrench',
    other: 'mdi-dots-horizontal',
  };
  return icons[type] || 'mdi-help';
}

function getTypeLabel(type: string): string {
  const option = typeOptions.value.find(o => o.value === type);
  return option?.title || type;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('pl-PL', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });
}

function populateFormFromTicket(ticket: ServiceTicket) {
  formData.value = {
    title: ticket.title,
    description: ticket.description,
    ticket_type: ticket.ticket_type,
    status: ticket.status,
    client: ticket.client.id,
    device: ticket.device,
    assigned_technician: ticket.assigned_technician?.id ?? null,
    scheduled_for: ticket.scheduled_for ? ticket.scheduled_for.slice(0, 10) : null,
    resolution_notes: ticket.resolution_notes || '',
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
  if (!validation?.valid) return;

  state.value.isSaving = true;
  state.value.error = '';

  try {
    if (isEditing.value && props.editingTicket) {
      await ticketsStore.updateTicket(props.editingTicket.id, formData.value);
    } else {
      await ticketsStore.addTicket(formData.value);
    }

    const message = isEditing.value
      ? t('tickets.forms.editSuccess')
      : t('tickets.forms.addSuccess');

    emit('save-success', message);
    closeDialog();
    ticketsStore.fetchTickets(true);
  } catch (error) {
    console.error('Błąd zapisu zgłoszenia:', error);
    state.value.error = error instanceof Error ? error.message : t('common.errors.unknown');
  } finally {
    state.value.isSaving = false;
  }
}

// Watchers
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.editingTicket) {
      populateFormFromTicket(props.editingTicket);
    } else {
      handleResetForm();
    }
  }
});

watch(() => props.editingTicket, (newTicket) => {
  if (newTicket && props.modelValue) {
    populateFormFromTicket(newTicket);
  }
}, { immediate: true });

// Czyść urządzenie gdy zmieni się klient
watch(() => formData.value.client, (newClientId, oldClientId) => {
  if (newClientId !== oldClientId && !isEditing.value) {
    formData.value.device = 0;
  }
});

// Lifecycle
onMounted(() => {
  clientsStore.fetchClients();
  devicesStore.fetchDevices();
  techniciansStore.fetchTechnicians();
});
</script>

<style scoped>
.ticket-form-card {
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

/* Form fields */
:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}

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
