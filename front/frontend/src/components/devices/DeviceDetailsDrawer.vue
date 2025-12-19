<template>
  <v-navigation-drawer
    v-model="isDrawerOpen"
    location="right"
    temporary
    width="480"
    class="device-details-drawer"
  >
    <template v-if="device">
      <!-- Nagłówek -->
      <div class="drawer-header">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="48" class="mr-3">
              <v-icon size="24">mdi-printer-pos</v-icon>
            </v-avatar>
            <div>
              <h2 class="text-h6 font-weight-bold mb-0">
                {{ device.brand.name }}
              </h2>
              <p class="text-body-2 text-medium-emphasis mb-0">
                {{ device.model_name }}
              </p>
            </div>
          </div>
          <v-btn
            icon
            variant="text"
            size="small"
            @click="isDrawerOpen = false"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </div>

        <!-- Status -->
        <div class="mt-4">
          <DeviceStatusChip :status="device.status" size="default" />
        </div>
      </div>

      <v-divider />

      <!-- Zawartość -->
      <div class="drawer-content">
        <!-- Sekcja: Identyfikacja -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-card-account-details</v-icon>
            Identyfikacja
          </h3>

          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Numer unikatowy</span>
              <span class="detail-value font-weight-medium">
                {{ device.unique_number }}
                <v-btn
                  icon
                  variant="text"
                  size="x-small"
                  class="ml-1"
                  @click="copyToClipboard(device.unique_number)"
                >
                  <v-icon size="14">mdi-content-copy</v-icon>
                  <v-tooltip activator="parent" location="top">Kopiuj</v-tooltip>
                </v-btn>
              </span>
            </div>

            <div class="detail-item">
              <span class="detail-label">Numer seryjny</span>
              <span class="detail-value">{{ device.serial_number || '—' }}</span>
            </div>
          </div>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Właściciel -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-domain</v-icon>
            Właściciel
          </h3>

          <v-card variant="tonal" color="primary" class="owner-card">
            <v-card-text class="pa-3">
              <div class="d-flex align-center">
                <v-avatar color="primary" size="40" class="mr-3">
                  <v-icon>mdi-domain</v-icon>
                </v-avatar>
                <div>
                  <p class="text-body-1 font-weight-medium mb-0">
                    {{ device.owner.name }}
                  </p>
                  <p class="text-caption text-medium-emphasis mb-0">
                    NIP: {{ device.owner.nip }}
                  </p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Przeglądy -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-calendar-check</v-icon>
            Przeglądy
          </h3>

          <div class="timeline">
            <div class="timeline-item">
              <div class="timeline-dot" :class="saleStatusClass"></div>
              <div class="timeline-content">
                <span class="detail-label">Data sprzedaży</span>
                <span class="detail-value">
                  {{ formatDate(device.sale_date) }}
                </span>
              </div>
            </div>

            <div class="timeline-item">
              <div class="timeline-dot" :class="lastServiceStatusClass"></div>
              <div class="timeline-content">
                <span class="detail-label">Ostatni przegląd</span>
                <span class="detail-value">
                  {{ formatDate(device.last_service_date) }}
                </span>
              </div>
            </div>

            <div class="timeline-item">
              <div
                class="timeline-dot"
                :class="nextServiceStatusClass"
              ></div>
              <div class="timeline-content">
                <span class="detail-label">Następny przegląd</span>
                <span
                  class="detail-value"
                  :class="{ 'text-error': isOverdue, 'text-warning': isUpcoming }"
                >
                  {{ formatDate(device.next_service_date) }}
                  <v-chip
                    v-if="isOverdue"
                    color="error"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    Przeterminowany
                  </v-chip>
                  <v-chip
                    v-else-if="isUpcoming"
                    color="warning"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    Wkrótce
                  </v-chip>
                </span>
              </div>
            </div>
          </div>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Zgłoszenia -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-ticket</v-icon>
            Zgłoszenia serwisowe
          </h3>

          <v-card variant="outlined" class="tickets-card">
            <v-card-text class="pa-3 text-center">
              <div class="text-h4 font-weight-bold" :class="ticketsCountColor">
                {{ device.tickets_count || 0 }}
              </div>
              <div class="text-caption text-medium-emphasis">
                {{ ticketsCountLabel }}
              </div>
            </v-card-text>
          </v-card>
        </div>

        <!-- Sekcja: Informacje dodatkowe -->
        <template v-if="device.operating_instructions || device.remarks">
          <v-divider class="my-4" />

          <div class="detail-section">
            <h3 class="section-title">
              <v-icon start size="18">mdi-information</v-icon>
              Informacje dodatkowe
            </h3>

            <div v-if="device.operating_instructions" class="info-block mb-3">
              <span class="info-label">Sposób użytkowania</span>
              <p class="info-text">{{ device.operating_instructions }}</p>
            </div>

            <div v-if="device.remarks" class="info-block">
              <span class="info-label">Uwagi</span>
              <p class="info-text">{{ device.remarks }}</p>
            </div>
          </div>
        </template>
      </div>

      <!-- Stopka z akcjami -->
      <div class="drawer-footer">
        <v-btn
          variant="tonal"
          color="primary"
          prepend-icon="mdi-pencil"
          class="flex-grow-1"
          @click="$emit('edit', device)"
        >
          Edytuj
        </v-btn>
        <v-btn
          variant="tonal"
          color="success"
          prepend-icon="mdi-check-decagram"
          class="flex-grow-1"
          @click="$emit('perform-service', device)"
        >
          Wykonaj przegląd
        </v-btn>
        <v-btn
          variant="tonal"
          prepend-icon="mdi-file-pdf-box"
          class="flex-grow-1"
          @click="$emit('export-pdf', device)"
        >
          PDF
        </v-btn>
      </div>
    </template>

    <!-- Pusty stan -->
    <div v-else class="empty-state">
      <v-icon size="64" color="grey-lighten-2">mdi-printer-pos-off</v-icon>
      <p class="text-body-1 text-medium-emphasis mt-4">
        Wybierz urządzenie, aby zobaczyć szczegóły
      </p>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { FiscalDevice } from '@/types';
import DeviceStatusChip from '@/components/devices/DeviceStatusChip.vue';
import { useSnackbarStore } from '@/stores/snackbar';

interface DeviceWithNextService extends FiscalDevice {
  next_service_date?: string | null;
}

const props = defineProps<{
  modelValue: boolean;
  device: DeviceWithNextService | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'edit', device: FiscalDevice): void;
  (e: 'perform-service', device: FiscalDevice): void;
  (e: 'export-pdf', device: FiscalDevice): void;
}>();

const snackbarStore = useSnackbarStore();

const isDrawerOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

// Date formatting
function formatDate(date: string | null | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

// Copy to clipboard
async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    snackbarStore.showSuccess('Skopiowano do schowka');
  } catch {
    snackbarStore.showError('Nie udało się skopiować');
  }
}

// Date status helpers
const isOverdue = computed(() => {
  if (!props.device?.next_service_date) return false;
  return new Date(props.device.next_service_date) < new Date();
});

const isUpcoming = computed(() => {
  if (!props.device?.next_service_date || isOverdue.value) return false;
  const nextDate = new Date(props.device.next_service_date);
  const today = new Date();
  const diffDays = Math.ceil((nextDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  return diffDays <= 30;
});

// Timeline dot classes
const saleStatusClass = computed(() => 'bg-primary');

const lastServiceStatusClass = computed(() => {
  if (!props.device?.last_service_date) return 'bg-grey';
  return 'bg-success';
});

const nextServiceStatusClass = computed(() => {
  if (isOverdue.value) return 'bg-error';
  if (isUpcoming.value) return 'bg-warning';
  return 'bg-grey-lighten-1';
});

// Tickets count
const ticketsCountColor = computed(() => {
  const count = props.device?.tickets_count || 0;
  if (count === 0) return 'text-success';
  if (count <= 3) return 'text-warning';
  return 'text-error';
});

const ticketsCountLabel = computed(() => {
  const count = props.device?.tickets_count || 0;
  if (count === 0) return 'Brak zgłoszeń';
  if (count === 1) return 'zgłoszenie';
  if (count >= 2 && count <= 4) return 'zgłoszenia';
  return 'zgłoszeń';
});
</script>

<style scoped>
.device-details-drawer {
  display: flex;
  flex-direction: column;
}

.device-details-drawer :deep(.v-navigation-drawer__content) {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* Header */
.drawer-header {
  padding: 20px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.08) 0%,
    rgba(var(--v-theme-primary), 0.02) 100%
  );
}

/* Content */
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* Section */
.detail-section {
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

/* Detail grid */
.detail-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.detail-value {
  font-size: 0.9375rem;
  color: rgb(var(--v-theme-on-surface));
  display: flex;
  align-items: center;
}

/* Owner card */
.owner-card {
  border-radius: 12px;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: rgba(var(--v-border-color), 0.3);
}

.timeline-item {
  position: relative;
  padding-bottom: 16px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-dot {
  position: absolute;
  left: -24px;
  top: 4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgb(var(--v-theme-surface));
  z-index: 1;
}

.timeline-dot.bg-primary {
  background-color: rgb(var(--v-theme-primary));
}

.timeline-dot.bg-success {
  background-color: rgb(var(--v-theme-success));
}

.timeline-dot.bg-warning {
  background-color: rgb(var(--v-theme-warning));
}

.timeline-dot.bg-error {
  background-color: rgb(var(--v-theme-error));
}

.timeline-dot.bg-grey {
  background-color: #9e9e9e;
}

.timeline-dot.bg-grey-lighten-1 {
  background-color: #bdbdbd;
}

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Tickets card */
.tickets-card {
  border-radius: 12px;
}

/* Info blocks */
.info-block {
  background: rgba(var(--v-theme-on-surface), 0.03);
  border-radius: 8px;
  padding: 12px;
}

.info-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: rgba(var(--v-theme-on-surface), 0.5);
  margin-bottom: 4px;
}

.info-text {
  font-size: 0.875rem;
  line-height: 1.5;
  margin: 0;
  color: rgba(var(--v-theme-on-surface), 0.8);
}

/* Footer */
.drawer-footer {
  padding: 16px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  display: flex;
  gap: 8px;
  background: rgb(var(--v-theme-surface));
}

/* Empty state */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 24px;
}

/* Scrollbar */
.drawer-content::-webkit-scrollbar {
  width: 6px;
}

.drawer-content::-webkit-scrollbar-track {
  background: transparent;
}

.drawer-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 3px;
}
</style>
