<template>
  <v-navigation-drawer
    v-model="isDrawerOpen"
    location="right"
    temporary
    width="480"
    class="certification-details-drawer"
  >
    <template v-if="certification">
      <!-- Nagłówek -->
      <div class="drawer-header">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-avatar
              :color="statusColor"
              size="56"
              class="mr-3"
            >
              <v-icon size="28" color="white">
                {{ statusIcon }}
              </v-icon>
            </v-avatar>
            <div>
              <h2 class="text-h6 font-weight-bold mb-0">
                Certyfikat
              </h2>
              <p class="text-body-2 text-medium-emphasis mb-0">
                {{ certification.certificate_number }}
                <v-btn
                  icon
                  variant="text"
                  size="x-small"
                  class="ml-1"
                  @click="copyToClipboard(certification.certificate_number)"
                >
                  <v-icon size="14">mdi-content-copy</v-icon>
                  <v-tooltip activator="parent" location="top">Kopiuj</v-tooltip>
                </v-btn>
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

        <!-- Status badge -->
        <div class="mt-4">
          <v-chip
            :color="statusColor"
            :prepend-icon="statusIcon"
            variant="flat"
          >
            {{ statusText }}
          </v-chip>
        </div>
      </div>

      <v-divider />

      <!-- Zawartość -->
      <div class="drawer-content">
        <!-- Sekcja: Serwisant -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-account</v-icon>
            Serwisant
          </h3>

          <v-card variant="tonal" color="primary" class="person-card">
            <v-card-text class="pa-3">
              <div class="d-flex align-center">
                <v-avatar color="primary" size="48" class="mr-3">
                  <span class="text-subtitle-1 font-weight-bold text-white">
                    {{ getInitials(certification.technician_name) }}
                  </span>
                </v-avatar>
                <div>
                  <p class="text-body-1 font-weight-medium mb-0">
                    {{ certification.technician_name }}
                  </p>
                  <p class="text-caption text-medium-emphasis mb-0">
                    Posiadacz certyfikatu
                  </p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Producent -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-factory</v-icon>
            Producent / Marka
          </h3>

          <v-card variant="outlined" class="manufacturer-card">
            <v-card-text class="pa-3">
              <div class="d-flex align-center">
                <v-avatar color="secondary" size="48" variant="tonal" class="mr-3">
                  <v-icon size="24">mdi-certificate</v-icon>
                </v-avatar>
                <div>
                  <p class="text-body-1 font-weight-medium mb-0">
                    {{ certification.manufacturer_name }}
                  </p>
                  <p class="text-caption text-medium-emphasis mb-0">
                    Uprawnienia do serwisowania urządzeń tego producenta
                  </p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Ważność -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-calendar-range</v-icon>
            Okres ważności
          </h3>

          <div class="validity-timeline">
            <!-- Data wydania -->
            <div class="timeline-item">
              <div class="timeline-dot bg-success"></div>
              <div class="timeline-content">
                <span class="timeline-label">Data wydania</span>
                <span class="timeline-value">
                  {{ formatDate(certification.issue_date) }}
                </span>
              </div>
            </div>

            <!-- Pasek postępu -->
            <div class="validity-progress my-3">
              <v-progress-linear
                :model-value="validityProgress"
                :color="statusColor"
                height="8"
                rounded
              />
              <div class="d-flex justify-space-between mt-1">
                <span class="text-caption text-medium-emphasis">Początek</span>
                <span class="text-caption font-weight-medium" :class="`text-${statusColor}`">
                  {{ validityProgressText }}
                </span>
                <span class="text-caption text-medium-emphasis">Koniec</span>
              </div>
            </div>

            <!-- Data wygaśnięcia -->
            <div class="timeline-item">
              <div class="timeline-dot" :class="`bg-${statusColor}`"></div>
              <div class="timeline-content">
                <span class="timeline-label">Data wygaśnięcia</span>
                <span class="timeline-value" :class="{ 'text-error': isExpired, 'text-warning': isExpiringSoon }">
                  {{ formatDate(certification.expiry_date) }}
                  <v-chip
                    v-if="isExpired"
                    color="error"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    Wygasł
                  </v-chip>
                  <v-chip
                    v-else-if="isExpiringSoon"
                    color="warning"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    Wkrótce wygaśnie
                  </v-chip>
                </span>
              </div>
            </div>
          </div>

          <!-- Alert o wygaśnięciu -->
          <v-alert
            v-if="isExpired"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            <template #prepend>
              <v-icon>mdi-alert-circle</v-icon>
            </template>
            <div>
              <strong>Certyfikat wygasł!</strong>
              <p class="mb-0 text-caption">
                Certyfikat wygasł {{ daysAgoText }}. Serwisant nie może wykonywać przeglądów urządzeń tego producenta.
              </p>
            </div>
          </v-alert>

          <v-alert
            v-else-if="isExpiringSoon"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            <template #prepend>
              <v-icon>mdi-clock-alert</v-icon>
            </template>
            <div>
              <strong>Certyfikat wkrótce wygaśnie!</strong>
              <p class="mb-0 text-caption">
                Pozostało {{ daysLeftText }}. Rozważ przedłużenie certyfikatu.
              </p>
            </div>
          </v-alert>

          <v-alert
            v-else
            type="success"
            variant="tonal"
            density="compact"
            class="mt-4"
          >
            <template #prepend>
              <v-icon>mdi-check-circle</v-icon>
            </template>
            <div>
              <strong>Certyfikat ważny</strong>
              <p class="mb-0 text-caption">
                Pozostało {{ daysLeftText }} do wygaśnięcia.
              </p>
            </div>
          </v-alert>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Szczegóły -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-information</v-icon>
            Szczegóły
          </h3>

          <div class="details-grid">
            <div class="detail-item">
              <span class="detail-label">Numer certyfikatu</span>
              <span class="detail-value font-weight-medium">
                {{ certification.certificate_number }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Okres ważności</span>
              <span class="detail-value">
                {{ totalValidityDays }} dni
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Pozostało</span>
              <span class="detail-value" :class="`text-${statusColor}`">
                {{ isExpired ? 'Wygasł' : `${daysLeft} dni` }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Stopka z akcjami -->
      <div class="drawer-footer">
        <v-btn
          variant="tonal"
          color="primary"
          prepend-icon="mdi-pencil"
          class="flex-grow-1"
          @click="$emit('edit', certification)"
        >
          Edytuj
        </v-btn>
        <v-btn
          v-if="isExpiringSoon || isExpired"
          variant="tonal"
          color="warning"
          prepend-icon="mdi-refresh"
          class="flex-grow-1"
          @click="$emit('renew', certification)"
        >
          Odnów
        </v-btn>
        <v-btn
          variant="tonal"
          color="error"
          prepend-icon="mdi-delete"
          class="flex-grow-1"
          @click="$emit('delete', certification)"
        >
          Usuń
        </v-btn>
      </div>
    </template>

    <!-- Pusty stan -->
    <div v-else class="empty-state">
      <v-icon size="64" color="grey-lighten-2">mdi-certificate-outline</v-icon>
      <p class="text-body-1 text-medium-emphasis mt-4">
        Wybierz certyfikat, aby zobaczyć szczegóły
      </p>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Certification } from '@/types';
import { useSnackbarStore } from '@/stores/snackbar';

const props = defineProps<{
  modelValue: boolean;
  certification: Certification | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'edit', certification: Certification): void;
  (e: 'renew', certification: Certification): void;
  (e: 'delete', certification: Certification): void;
}>();

const snackbarStore = useSnackbarStore();

const isDrawerOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

// Date calculations
const today = new Date();
today.setHours(0, 0, 0, 0);

const expiryDate = computed(() => {
  if (!props.certification?.expiry_date) return null;
  const date = new Date(props.certification.expiry_date);
  date.setHours(0, 0, 0, 0);
  return date;
});

const issueDate = computed(() => {
  if (!props.certification?.issue_date) return null;
  const date = new Date(props.certification.issue_date);
  date.setHours(0, 0, 0, 0);
  return date;
});

const daysLeft = computed(() => {
  if (!expiryDate.value) return 0;
  const diff = expiryDate.value.getTime() - today.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
});

const daysAgo = computed(() => {
  if (!expiryDate.value) return 0;
  return Math.abs(daysLeft.value);
});

const totalValidityDays = computed(() => {
  if (!issueDate.value || !expiryDate.value) return 0;
  const diff = expiryDate.value.getTime() - issueDate.value.getTime();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
});

const isExpired = computed(() => daysLeft.value < 0);
const isExpiringSoon = computed(() => !isExpired.value && daysLeft.value <= 30);
const isValid = computed(() => !isExpired.value && !isExpiringSoon.value);

// Progress calculation
const validityProgress = computed(() => {
  if (!issueDate.value || !expiryDate.value) return 0;
  if (isExpired.value) return 100;

  const total = expiryDate.value.getTime() - issueDate.value.getTime();
  const elapsed = today.getTime() - issueDate.value.getTime();

  return Math.min(100, Math.max(0, (elapsed / total) * 100));
});

const validityProgressText = computed(() => {
  if (isExpired.value) return 'Wygasł';
  if (isExpiringSoon.value) return `${daysLeft.value} dni`;
  return `${Math.round(100 - validityProgress.value)}% pozostało`;
});

// Status
const statusColor = computed(() => {
  if (isExpired.value) return 'error';
  if (isExpiringSoon.value) return 'warning';
  return 'success';
});

const statusIcon = computed(() => {
  if (isExpired.value) return 'mdi-shield-off';
  if (isExpiringSoon.value) return 'mdi-shield-alert';
  return 'mdi-shield-check';
});

const statusText = computed(() => {
  if (isExpired.value) return 'Wygasły';
  if (isExpiringSoon.value) return 'Wkrótce wygasa';
  return 'Ważny';
});

// Text helpers
const daysLeftText = computed(() => {
  const d = daysLeft.value;
  if (d === 1) return '1 dzień';
  if (d >= 2 && d <= 4) return `${d} dni`;
  return `${d} dni`;
});

const daysAgoText = computed(() => {
  const d = daysAgo.value;
  if (d === 1) return '1 dzień temu';
  if (d >= 2 && d <= 4) return `${d} dni temu`;
  return `${d} dni temu`;
});

// Format date
function formatDate(date: string | null | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

// Get initials
function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
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
</script>

<style scoped>
.certification-details-drawer {
  display: flex;
  flex-direction: column;
}

.certification-details-drawer :deep(.v-navigation-drawer__content) {
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

/* Cards */
.person-card,
.manufacturer-card {
  border-radius: 12px;
}

/* Validity timeline */
.validity-timeline {
  position: relative;
  padding-left: 24px;
}

.validity-timeline::before {
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
  padding-bottom: 8px;
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

.timeline-dot.bg-success {
  background-color: rgb(var(--v-theme-success));
}

.timeline-dot.bg-warning {
  background-color: rgb(var(--v-theme-warning));
}

.timeline-dot.bg-error {
  background-color: rgb(var(--v-theme-error));
}

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.timeline-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.timeline-value {
  font-size: 0.9375rem;
  color: rgb(var(--v-theme-on-surface));
  display: flex;
  align-items: center;
}

/* Validity progress */
.validity-progress {
  margin-left: -24px;
  padding-left: 0;
}

/* Details grid */
.details-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: center;
  padding: 12px;
  background: rgba(var(--v-theme-on-surface), 0.03);
  border-radius: 8px;
}

.detail-label {
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.detail-value {
  font-size: 0.875rem;
  color: rgb(var(--v-theme-on-surface));
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
