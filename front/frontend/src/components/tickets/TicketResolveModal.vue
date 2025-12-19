<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="600px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="resolve-form-card" rounded="lg">
      <!-- Nagłówek -->
      <div class="form-header form-header--resolve">
        <div class="d-flex align-center">
          <v-avatar
            color="success"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">mdi-check-circle</v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ t('tickets.resolve.title') }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ t('tickets.resolve.subtitle', { number: ticket.ticket_number }) }}
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

      <!-- Informacje o zgłoszeniu -->
      <div class="ticket-info-banner">
        <v-row dense align="center">
          <v-col cols="12" sm="6">
            <div class="d-flex align-center">
              <v-avatar
                :color="getTypeColor(ticket.ticket_type)"
                size="40"
                variant="tonal"
                class="mr-3"
              >
                <v-icon size="20">{{ getTypeIcon(ticket.ticket_type) }}</v-icon>
              </v-avatar>
              <div>
                <span class="text-body-2 font-weight-bold d-block">{{ ticket.title }}</span>
                <span class="text-caption text-medium-emphasis">
                  {{ ticket.ticket_type_display }}
                </span>
              </div>
            </div>
          </v-col>
          <v-col cols="12" sm="6">
            <div class="d-flex flex-wrap ga-2 justify-sm-end">
              <v-chip size="small" variant="tonal" color="primary">
                <v-icon start size="14">mdi-office-building</v-icon>
                {{ ticket.client.name }}
              </v-chip>
              <v-chip size="small" variant="tonal">
                <v-icon start size="14">mdi-printer-pos</v-icon>
                {{ ticket.device_info }}
              </v-chip>
            </div>
          </v-col>
        </v-row>
      </div>

      <v-divider />

      <!-- Formularz -->
      <v-card-text class="form-content">
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <!-- Alert błędu -->
          <v-alert
            v-if="error"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-6"
            closable
            @click:close="error = null"
          >
            <template #prepend>
              <v-icon>mdi-alert-circle</v-icon>
            </template>
            {{ error }}
          </v-alert>

          <!-- Sekcja: Wynik rozwiązania -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-clipboard-check</v-icon>
              {{ t('tickets.resolve.resultSection') }}
            </h3>

            <v-row dense>
              <v-col cols="12">
                <v-select
                  v-model="formData.resolution"
                  :items="resolutionOptions"
                  item-title="title"
                  item-value="value"
                  :label="t('tickets.resolve.resultLabel')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon :color="getResolutionColor(formData.resolution)" size="20">
                      {{ getResolutionIcon(formData.resolution) }}
                    </v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar
                          :color="getResolutionColor(item.raw.value)"
                          size="32"
                          variant="tonal"
                        >
                          <v-icon size="16">{{ getResolutionIcon(item.raw.value) }}</v-icon>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <v-chip
                      :color="getResolutionColor(item.raw.value)"
                      size="small"
                      variant="tonal"
                    >
                      <v-icon start size="14">{{ getResolutionIcon(item.raw.value) }}</v-icon>
                      {{ item.title }}
                    </v-chip>
                  </template>
                </v-select>
              </v-col>
            </v-row>

            <!-- Alert o konsekwencjach -->
            <v-expand-transition>
              <v-alert
                v-if="formData.resolution"
                :type="getResolutionAlertType(formData.resolution)"
                variant="tonal"
                density="compact"
                class="mt-4"
              >
                <template #prepend>
                  <v-icon size="18">{{ getResolutionIcon(formData.resolution) }}</v-icon>
                </template>
                <span class="text-caption">
                  {{ getResolutionDescription(formData.resolution) }}
                </span>
              </v-alert>
            </v-expand-transition>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Notatki -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-note-text</v-icon>
              {{ t('tickets.resolve.notesSection') }}
            </h3>

            <v-row dense>
              <v-col cols="12">
                <v-textarea
                  v-model="formData.resolution_notes"
                  :label="t('tickets.resolve.notesLabel')"
                  :placeholder="t('tickets.resolve.notesPlaceholder')"
                  variant="outlined"
                  density="comfortable"
                  rows="4"
                  auto-grow
                  counter
                  maxlength="2000"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20" class="mt-1">mdi-text</v-icon>
                  </template>
                </v-textarea>
              </v-col>
            </v-row>

            <!-- Podpowiedzi do notatek -->
            <div class="mt-3">
              <span class="text-caption text-medium-emphasis d-block mb-2">
                {{ t('tickets.resolve.quickNotes') }}
              </span>
              <div class="d-flex flex-wrap ga-2">
                <v-chip
                  v-for="note in quickNotes"
                  :key="note"
                  size="small"
                  variant="outlined"
                  @click="appendQuickNote(note)"
                >
                  <v-icon start size="14">mdi-plus</v-icon>
                  {{ note }}
                </v-chip>
              </div>
            </div>
          </div>

          <!-- Podsumowanie -->
          <div v-if="formData.resolution" class="summary-section mt-6">
            <v-card variant="outlined" class="summary-card">
              <div class="pa-4">
                <div class="d-flex align-center mb-3">
                  <v-icon color="primary" class="mr-2">mdi-clipboard-list</v-icon>
                  <span class="text-body-2 font-weight-bold">
                    {{ t('tickets.resolve.summary') }}
                  </span>
                </div>

                <v-divider class="mb-3" />

                <div class="summary-grid">
                  <div class="summary-item">
                    <span class="summary-label">{{ t('tickets.resolve.ticketNumber') }}</span>
                    <span class="summary-value">{{ ticket.ticket_number }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">{{ t('tickets.resolve.result') }}</span>
                    <v-chip
                      :color="getResolutionColor(formData.resolution)"
                      size="x-small"
                      variant="flat"
                    >
                      {{ getResolutionLabel(formData.resolution) }}
                    </v-chip>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">{{ t('tickets.resolve.closedAt') }}</span>
                    <span class="summary-value">{{ currentDateTime }}</span>
                  </div>
                  <div v-if="ticket.assigned_technician" class="summary-item">
                    <span class="summary-label">{{ t('tickets.resolve.closedBy') }}</span>
                    <span class="summary-value">{{ ticket.assigned_technician.full_name }}</span>
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
          :color="getResolutionColor(formData.resolution) || 'success'"
          variant="flat"
          :loading="isSaving"
          :disabled="!formData.resolution"
          @click="handleFormSubmit"
        >
          <v-icon start>mdi-check</v-icon>
          {{ t('tickets.resolve.confirm') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useTicketsStore } from '@/stores/tickets';
import type { ServiceTicket, TicketResolutionPayload } from '@/types';

// Props & Emits
const props = defineProps<{
  modelValue: boolean;
  ticket: ServiceTicket;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

// Composables
const { t } = useI18n();
const ticketsStore = useTicketsStore();
const display = useDisplay();

// Responsive
const isMobile = computed(() => display.smAndDown.value);

// Refs
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);
const isSaving = ref(false);
const error = ref<string | null>(null);

// Form data
const formData = ref<TicketResolutionPayload>({
  resolution: '',
  resolution_notes: '',
});

// Quick notes templates
const quickNotes = [
  'Wymieniono części',
  'Aktualizacja oprogramowania',
  'Czyszczenie urządzenia',
  'Kalibracja',
  'Szkolenie użytkownika',
];

// Computed
const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const currentDateTime = computed(() => {
  return new Date().toLocaleString('pl-PL', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
});

const resolutionOptions = computed(() => [
  { title: t('tickets.resolutions.completed'), value: 'completed' },
  { title: t('tickets.resolutions.failed'), value: 'failed' },
  { title: t('tickets.resolutions.cancelled'), value: 'cancelled' },
]);

// Validation rules
const rules = {
  required: (v: string) => !!v || t('validation.required'),
};

// Methods
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

function getResolutionColor(resolution: string): string {
  const colors: Record<string, string> = {
    completed: 'success',
    failed: 'error',
    cancelled: 'warning',
  };
  return colors[resolution] || 'grey';
}

function getResolutionIcon(resolution: string): string {
  const icons: Record<string, string> = {
    completed: 'mdi-check-circle',
    failed: 'mdi-close-circle',
    cancelled: 'mdi-cancel',
  };
  return icons[resolution] || 'mdi-help-circle';
}

function getResolutionLabel(resolution: string): string {
  const option = resolutionOptions.value.find(o => o.value === resolution);
  return option?.title || resolution;
}

function getResolutionAlertType(resolution: string): 'success' | 'error' | 'warning' | 'info' {
  const types: Record<string, 'success' | 'error' | 'warning'> = {
    completed: 'success',
    failed: 'error',
    cancelled: 'warning',
  };
  return types[resolution] || 'info';
}

function getResolutionDescription(resolution: string): string {
  const descriptions: Record<string, string> = {
    completed: t('tickets.resolve.descriptions.completed'),
    failed: t('tickets.resolve.descriptions.failed'),
    cancelled: t('tickets.resolve.descriptions.cancelled'),
  };
  return descriptions[resolution] || '';
}

function appendQuickNote(note: string) {
  if (formData.value.resolution_notes) {
    formData.value.resolution_notes += `\n• ${note}`;
  } else {
    formData.value.resolution_notes = `• ${note}`;
  }
}

function resetForm() {
  formData.value = {
    resolution: '',
    resolution_notes: '',
  };
  error.value = null;
}

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  const validation = await formRef.value?.validate();
  if (!validation?.valid) return;

  isSaving.value = true;
  error.value = null;

  try {
    await ticketsStore.resolveTicket(props.ticket.id, formData.value);
    emit('save-success', t('tickets.resolve.success'));
    closeDialog();
  } catch (err) {
    error.value = err instanceof Error ? err.message : t('common.errors.unknown');
    console.error('Błąd zamykania zgłoszenia:', err);
  } finally {
    isSaving.value = false;
  }
}

// Watchers
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    resetForm();
  }
});
</script>

<style scoped>
.resolve-form-card {
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

.form-header--resolve {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-success), 0.08) 0%,
    rgba(var(--v-theme-success), 0.02) 100%
  );
}

/* Ticket info banner */
.ticket-info-banner {
  padding: 16px 24px;
  background: rgba(var(--v-theme-on-surface), 0.02);
}

/* Content */
.form-content {
  padding: 24px;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

/* Section */
.form-section {
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

/* Summary */
.summary-section {
  margin-top: 24px;
}

.summary-card {
  border-radius: 12px;
  background: rgba(var(--v-theme-success), 0.02);
  border-color: rgba(var(--v-theme-success), 0.2);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 0.75rem;
  color: rgba(var(--v-theme-on-surface), 0.6);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.summary-value {
  font-size: 0.875rem;
  font-weight: 500;
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

  .ticket-info-banner {
    padding: 12px 16px;
  }

  .form-content {
    padding: 16px;
    max-height: calc(100vh - 300px);
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

  .summary-grid {
    grid-template-columns: 1fr;
  }
}

/* Transitions */
.v-expand-transition-enter-active,
.v-expand-transition-leave-active {
  transition: all 0.3s ease;
}
</style>
