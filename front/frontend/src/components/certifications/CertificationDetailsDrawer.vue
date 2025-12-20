<template>
  <v-navigation-drawer
    v-model="isDrawerOpen"
    location="right"
    temporary
    width="480"
    class="certification-details-drawer"
  >
    <template v-if="certification">
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
                {{ t('certifications.details.title') }}
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
                  <v-tooltip activator="parent" location="top">{{ t('common.copy') }}</v-tooltip>
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

      <div class="drawer-content">
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-account</v-icon>
            {{ t('certifications.sections.technician') }}
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
                    {{ t('certifications.details.certificateHolder') }}
                  </p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-factory</v-icon>
            {{ t('certifications.sections.manufacturer') }}
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
                    {{ t('certifications.details.manufacturerPermission') }}
                  </p>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-calendar-range</v-icon>
            {{ t('certifications.sections.validity') }}
          </h3>

          <div class="validity-timeline">
            <div class="timeline-item">
              <div class="timeline-dot bg-success"></div>
              <div class="timeline-content">
                <span class="timeline-label">{{ t('certifications.details.issueDate') }}</span>
                <span class="timeline-value">
                  {{ formatDate(certification.issue_date) }}
                </span>
              </div>
            </div>

            <div class="validity-progress my-3">
              <v-progress-linear
                :model-value="validityProgress"
                :color="statusColor"
                height="8"
                rounded
              />
              <div class="d-flex justify-space-between mt-1">
                <span class="text-caption text-medium-emphasis">{{ t('certifications.details.start') }}</span>
                <span class="text-caption font-weight-medium" :class="`text-${statusColor}`">
                  {{ validityProgressText }}
                </span>
                <span class="text-caption text-medium-emphasis">{{ t('certifications.details.end') }}</span>
              </div>
            </div>

            <!-- Data wygaśnięcia -->
            <div class="timeline-item">
              <div class="timeline-dot" :class="`bg-${statusColor}`"></div>
              <div class="timeline-content">
                <span class="timeline-label">{{ t('certifications.details.expiryDate') }}</span>
                <span class="timeline-value" :class="{ 'text-error': isExpired, 'text-warning': isExpiringSoon }">
                  {{ formatDate(certification.expiry_date) }}
                  <v-chip
                    v-if="isExpired"
                    color="error"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    {{ t('certifications.status.expired') }}
                  </v-chip>
                  <v-chip
                    v-else-if="isExpiringSoon"
                    color="warning"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    {{ t('certifications.status.expiringSoon') }}
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
              <strong>{{ t('certifications.alerts.expiredTitle') }}</strong>
              <p class="mb-0 text-caption">
                {{ t('certifications.alerts.expiredMessage', { days: daysAgoText }) }}
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
              <strong>{{ t('certifications.alerts.expiringSoonTitle') }}</strong>
              <p class="mb-0 text-caption">
                {{ t('certifications.alerts.expiringSoonMessage', { days: daysLeftText }) }}
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
              <strong>{{ t('certifications.alerts.validTitle') }}</strong>
              <p class="mb-0 text-caption">
                {{ t('certifications.alerts.validMessage', { days: daysLeftText }) }}
              </p>
            </div>
          </v-alert>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-information</v-icon>
            {{ t('certifications.sections.details') }}
          </h3>

          <div class="details-grid">
            <div class="detail-item">
              <span class="detail-label">{{ t('certifications.details.certificateNumber') }}</span>
              <span class="detail-value font-weight-medium">
                {{ certification.certificate_number }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ t('certifications.details.validityPeriod') }}</span>
              <span class="detail-value">
                {{ t('certifications.details.days', { count: totalValidityDays }) }}
              </span>
            </div>
            <div class="detail-item">
              <span class="detail-label">{{ t('certifications.details.remaining') }}</span>
              <span class="detail-value" :class="`text-${statusColor}`">
                {{ isExpired ? t('certifications.status.expired') : t('certifications.details.days', { count: daysLeft }) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="drawer-footer">
        <v-btn
          variant="tonal"
          color="primary"
          prepend-icon="mdi-pencil"
          class="flex-grow-1"
          @click="$emit('edit', certification)"
        >
          {{ t('common.edit') }}
        </v-btn>
        <v-btn
          v-if="isExpiringSoon || isExpired"
          variant="tonal"
          color="warning"
          prepend-icon="mdi-refresh"
          class="flex-grow-1"
          @click="$emit('renew', certification)"
        >
          {{ t('certifications.actions.renew') }}
        </v-btn>
        <v-btn
          variant="tonal"
          color="error"
          prepend-icon="mdi-delete"
          class="flex-grow-1"
          @click="$emit('delete', certification)"
        >
          {{ t('common.delete') }}
        </v-btn>
      </div>
    </template>

    <div v-else class="empty-state">
      <v-icon size="64" color="grey-lighten-2">mdi-certificate-outline</v-icon>
      <p class="text-body-1 text-medium-emphasis mt-4">
        {{ t('certifications.details.selectCertification') }}
      </p>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
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

const { t, locale } = useI18n();
const snackbarStore = useSnackbarStore();

const isDrawerOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

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

const validityProgress = computed(() => {
  if (!issueDate.value || !expiryDate.value) return 0;
  if (isExpired.value) return 100;

  const total = expiryDate.value.getTime() - issueDate.value.getTime();
  const elapsed = today.getTime() - issueDate.value.getTime();

  return Math.min(100, Math.max(0, (elapsed / total) * 100));
});

const validityProgressText = computed(() => {
  if (isExpired.value) return t('certifications.status.expired');
  if (isExpiringSoon.value) return t('certifications.details.daysShort', { count: daysLeft.value });
  return t('certifications.details.percentRemaining', { percent: Math.round(100 - validityProgress.value) });
});

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
  if (isExpired.value) return t('certifications.status.expired');
  if (isExpiringSoon.value) return t('certifications.status.expiring');
  return t('certifications.status.valid');
});

const daysLeftText = computed(() => {
  return t('certifications.details.daysCount', { count: daysLeft.value });
});

const daysAgoText = computed(() => {
  return t('certifications.details.daysAgo', { count: daysAgo.value });
});

function formatDate(date: string | null | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString(locale.value === 'pl' ? 'pl-PL' : 'en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text);
    snackbarStore.showSuccess(t('common.copiedToClipboard'));
  } catch {
    snackbarStore.showError(t('common.copyFailed'));
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

.drawer-header {
  padding: 20px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.08) 0%,
    rgba(var(--v-theme-primary), 0.02) 100%
  );
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

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

.person-card,
.manufacturer-card {
  border-radius: 12px;
}

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

.validity-progress {
  margin-left: -24px;
  padding-left: 0;
}

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

.drawer-footer {
  padding: 16px;
  border-top: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  display: flex;
  gap: 8px;
  background: rgb(var(--v-theme-surface));
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 24px;
}

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
