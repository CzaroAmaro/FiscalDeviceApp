<template>
  <v-navigation-drawer
    v-model="isDrawerOpen"
    location="right"
    temporary
    width="480"
    class="client-details-drawer"
  >
    <template v-if="client">
      <div class="drawer-header">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="48" class="mr-3">
              <v-icon size="24">mdi-domain</v-icon>
            </v-avatar>
            <div>
              <h2 class="text-h6 font-weight-bold mb-0">
                {{ client.name }}
              </h2>
              <p class="text-body-2 text-medium-emphasis mb-0">
                {{ t('clients.details.clientSince', { date: formatDate(client.created_at) }) }}
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
      </div>

      <v-divider />

      <div class="drawer-content">
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-office-building</v-icon>
            {{ t('clients.sections.companyData') }}
          </h3>

          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">{{ t('clients.headers.nip') }}</span>
              <span class="detail-value font-weight-medium">
                {{ formatNip(client.nip) }}
                <v-btn
                  icon
                  variant="text"
                  size="x-small"
                  class="ml-1"
                  @click="copyToClipboard(client.nip)"
                >
                  <v-icon size="14">mdi-content-copy</v-icon>
                  <v-tooltip activator="parent" location="top">{{ t('common.copy') }}</v-tooltip>
                </v-btn>
              </span>
            </div>

            <div v-if="client.regon" class="detail-item">
              <span class="detail-label">{{ t('clients.headers.regon') }}</span>
              <span class="detail-value">{{ client.regon }}</span>
            </div>
          </div>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-map-marker</v-icon>
            {{ t('clients.details.sections.address') }}
          </h3>

          <v-card variant="tonal" color="primary" class="address-card">
            <v-card-text class="pa-3">
              <div class="d-flex align-start">
                <v-icon color="primary" class="mr-3 mt-1">mdi-map-marker</v-icon>
                <div>
                  <p class="text-body-1 mb-1">
                    {{ client.address || t('clients.details.noAddress') }}
                  </p>
                  <v-btn
                    v-if="client.latitude && client.longitude"
                    size="small"
                    variant="text"
                    color="primary"
                    class="px-0"
                    @click="$emit('show-on-map', client)"
                  >
                    <v-icon start size="16">mdi-map</v-icon>
                    {{ t('clients.details.showOnMap') }}
                  </v-btn>
                  <span
                    v-else
                    class="text-caption text-medium-emphasis"
                  >
                    {{ t('clients.details.noGpsCoordinates') }}
                  </span>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-card-account-phone</v-icon>
            {{ t('clients.sections.contactData') }}
          </h3>

          <div class="contact-list">
            <div class="contact-item">
              <div class="contact-icon">
                <v-icon size="20" color="primary">mdi-phone</v-icon>
              </div>
              <div class="contact-content">
                <span class="contact-label">{{ t('clients.details.phone') }}</span>
                <template v-if="client.phone_number">
                  <a
                    :href="`tel:${client.phone_number}`"
                    class="contact-value contact-link"
                  >
                    {{ formatPhone(client.phone_number) }}
                  </a>
                </template>
                <span v-else class="contact-value text-medium-emphasis">
                  {{ t('clients.details.notProvided') }}
                </span>
              </div>
              <v-btn
                v-if="client.phone_number"
                icon
                variant="text"
                size="small"
                color="primary"
                :href="`tel:${client.phone_number}`"
              >
                <v-icon size="18">mdi-phone</v-icon>
                <v-tooltip activator="parent" location="top">{{ t('clients.details.actions.call') }}</v-tooltip>
              </v-btn>
            </div>

            <div class="contact-item">
              <div class="contact-icon">
                <v-icon size="20" color="primary">mdi-email</v-icon>
              </div>
              <div class="contact-content">
                <span class="contact-label">{{ t('clients.details.email') }}</span>
                <template v-if="client.email">
                  <a
                    :href="`mailto:${client.email}`"
                    class="contact-value contact-link"
                  >
                    {{ client.email }}
                  </a>
                </template>
                <span v-else class="contact-value text-medium-emphasis">
                  {{ t('clients.details.notProvided') }}
                </span>
              </div>
              <v-btn
                v-if="client.email"
                icon
                variant="text"
                size="small"
                color="primary"
                :href="`mailto:${client.email}`"
              >
                <v-icon size="18">mdi-email-fast</v-icon>
                <v-tooltip activator="parent" location="top">{{ t('clients.details.actions.sendEmail') }}</v-tooltip>
              </v-btn>
            </div>
          </div>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-chart-box</v-icon>
            {{ t('clients.details.sections.statistics') }}
          </h3>

          <div v-if="isLoadingStats" class="d-flex justify-center py-4">
            <v-progress-circular indeterminate color="primary" size="32" />
          </div>

          <v-row v-else dense>
            <v-col cols="4">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="primary" class="mb-1">
                    mdi-printer-pos
                  </v-icon>
                  <div class="text-h5 font-weight-bold">
                    {{ stats.devices_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ t('clients.details.stats.devices', stats.devices_count) }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="4">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="info" class="mb-1">
                    mdi-ticket
                  </v-icon>
                  <div class="text-h5 font-weight-bold">
                    {{ stats.tickets_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ t('clients.details.stats.tickets', stats.tickets_count) }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="4">
              <v-card
                variant="outlined"
                class="stat-card"
                :class="{ 'border-warning': stats.open_tickets_count > 0 }"
              >
                <v-card-text class="pa-3 text-center">
                  <v-icon
                    size="24"
                    :color="stats.open_tickets_count > 0 ? 'warning' : 'success'"
                    class="mb-1"
                  >
                    {{ stats.open_tickets_count > 0 ? 'mdi-alert-circle' : 'mdi-check-circle' }}
                  </v-icon>
                  <div
                    class="text-h5 font-weight-bold"
                    :class="stats.open_tickets_count > 0 ? 'text-warning' : 'text-success'"
                  >
                    {{ stats.open_tickets_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    {{ t('clients.details.stats.openTickets') }}
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <v-divider class="my-4" />

        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-information</v-icon>
            {{ t('clients.details.sections.info') }}
          </h3>

          <div class="info-list">
            <div class="info-item">
              <v-icon size="16" color="grey" class="mr-2">mdi-calendar-plus</v-icon>
              <span class="text-body-2 text-medium-emphasis">
                {{ t('clients.details.addedOn') }}: {{ formatDateTime(client.created_at) }}
              </span>
            </div>
            <div v-if="client.latitude && client.longitude" class="info-item">
              <v-icon size="16" color="success" class="mr-2">mdi-map-check</v-icon>
              <span class="text-body-2 text-medium-emphasis">
                {{ t('clients.details.gpsAvailable') }}
              </span>
            </div>
            <div v-else class="info-item">
              <v-icon size="16" color="warning" class="mr-2">mdi-map-marker-off</v-icon>
              <span class="text-body-2 text-medium-emphasis">
                {{ t('clients.details.gpsUnavailable') }}
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
          @click="$emit('edit', client)"
        >
          {{ t('common.edit') }}
        </v-btn>
        <v-btn
          v-if="client.latitude && client.longitude"
          variant="tonal"
          color="info"
          prepend-icon="mdi-map-marker"
          class="flex-grow-1"
          @click="$emit('show-on-map', client)"
        >
          {{ t('clients.details.map') }}
        </v-btn>
        <v-btn
          v-if="client.email"
          variant="tonal"
          prepend-icon="mdi-email"
          class="flex-grow-1"
          :href="`mailto:${client.email}`"
        >
          {{ t('clients.headers.email') }}
        </v-btn>
      </div>
    </template>

    <div v-else class="empty-state">
      <v-icon size="64" color="grey-lighten-2">mdi-domain-off</v-icon>
      <p class="text-body-1 text-medium-emphasis mt-4">
        {{ t('clients.details.selectClient') }}
      </p>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import type { Client, ClientStats } from '@/types';
import { useSnackbarStore } from '@/stores/snackbar';
import { fetchClientStats } from '@/api/clients';

const props = defineProps<{
  modelValue: boolean;
  client: Client | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'edit', client: Client): void;
  (e: 'show-on-map', client: Client): void;
}>();

const { t } = useI18n();
const snackbarStore = useSnackbarStore();

const isDrawerOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const isLoadingStats = ref(false);
const stats = ref<ClientStats>({
  devices_count: 0,
  tickets_count: 0,
  open_tickets_count: 0,
});

watch(() => props.client, async (newClient) => {
  if (newClient) {
    isLoadingStats.value = true;
    try {
      stats.value = await fetchClientStats(newClient.id);
    } catch (error) {
      console.error('Error fetching stats:', error);
      stats.value = {
        devices_count: 0,
        tickets_count: 0,
        open_tickets_count: 0,
      };
    } finally {
      isLoadingStats.value = false;
    }
  }
}, { immediate: true });

function formatDate(date: string | null | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function formatDateTime(date: string | null | undefined): string {
  if (!date) return '—';
  return new Date(date).toLocaleDateString('pl-PL', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function formatNip(nip: string): string {
  if (!nip) return '—';
  const cleaned = nip.replace(/\D/g, '');
  if (cleaned.length !== 10) return nip;
  return `${cleaned.slice(0, 3)}-${cleaned.slice(3, 6)}-${cleaned.slice(6, 8)}-${cleaned.slice(8)}`;
}

function formatPhone(phone: string): string {
  if (!phone) return '—';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 9) {
    return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`;
  }
  return phone;
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
.client-details-drawer {
  display: flex;
  flex-direction: column;
}

.client-details-drawer :deep(.v-navigation-drawer__content) {
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

.address-card {
  border-radius: 12px;
}

.contact-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: rgba(var(--v-theme-on-surface), 0.03);
  border-radius: 10px;
  gap: 12px;
}

.contact-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(var(--v-theme-primary), 0.1);
  border-radius: 10px;
}

.contact-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.contact-label {
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  color: rgba(var(--v-theme-on-surface), 0.5);
}

.contact-value {
  font-size: 0.9375rem;
}

.contact-link {
  color: rgb(var(--v-theme-primary));
  text-decoration: none;
}

.contact-link:hover {
  text-decoration: underline;
}

.stat-card {
  border-radius: 12px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card.border-warning {
  border-color: rgb(var(--v-theme-warning)) !important;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
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
