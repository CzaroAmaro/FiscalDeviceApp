<template>
  <v-navigation-drawer
    v-model="isDrawerOpen"
    location="right"
    temporary
    width="480"
    class="technician-details-drawer"
  >
    <template v-if="technician">
      <!-- Nagłówek -->
      <div class="drawer-header">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-avatar
              :color="technician.is_active ? 'primary' : 'grey'"
              size="56"
              class="mr-3"
            >
              <span class="text-h5 font-weight-bold text-white">
                {{ getInitials(technician.full_name) }}
              </span>
            </v-avatar>
            <div>
              <h2 class="text-h6 font-weight-bold mb-0">
                {{ technician.full_name }}
              </h2>
              <div class="d-flex align-center ga-2 mt-1">
                <v-chip
                  :color="technician.role === 'admin' ? 'primary' : 'secondary'"
                  size="x-small"
                  variant="flat"
                >
                  {{ technician.role_display }}
                </v-chip>
                <v-chip
                  :color="technician.is_active ? 'success' : 'error'"
                  size="x-small"
                  variant="tonal"
                >
                  {{ technician.is_active ? 'Aktywny' : 'Nieaktywny' }}
                </v-chip>
              </div>
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

      <!-- Zawartość -->
      <div class="drawer-content">
        <!-- Sekcja: Dane kontaktowe -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-card-account-details</v-icon>
            Dane kontaktowe
          </h3>

          <div class="contact-list">
            <!-- Email -->
            <div class="contact-item">
              <div class="contact-icon">
                <v-icon size="20" color="primary">mdi-email</v-icon>
              </div>
              <div class="contact-content">
                <span class="contact-label">E-mail</span>
                <template v-if="technician.email">
                  <a
                    :href="`mailto:${technician.email}`"
                    class="contact-value contact-link"
                  >
                    {{ technician.email }}
                  </a>
                </template>
                <span v-else class="contact-value text-medium-emphasis">
                  Nie podano
                </span>
              </div>
              <v-btn
                v-if="technician.email"
                icon
                variant="text"
                size="small"
                color="primary"
                :href="`mailto:${technician.email}`"
              >
                <v-icon size="18">mdi-email-fast</v-icon>
                <v-tooltip activator="parent" location="top">Wyślij email</v-tooltip>
              </v-btn>
            </div>

            <!-- Telefon -->
            <div class="contact-item">
              <div class="contact-icon">
                <v-icon size="20" color="primary">mdi-phone</v-icon>
              </div>
              <div class="contact-content">
                <span class="contact-label">Telefon</span>
                <template v-if="technician.phone_number">
                  <a
                    :href="`tel:${technician.phone_number}`"
                    class="contact-value contact-link"
                  >
                    {{ formatPhone(technician.phone_number) }}
                  </a>
                </template>
                <span v-else class="contact-value text-medium-emphasis">
                  Nie podano
                </span>
              </div>
              <v-btn
                v-if="technician.phone_number"
                icon
                variant="text"
                size="small"
                color="primary"
                :href="`tel:${technician.phone_number}`"
              >
                <v-icon size="18">mdi-phone</v-icon>
                <v-tooltip activator="parent" location="top">Zadzwoń</v-tooltip>
              </v-btn>
            </div>
          </div>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Konto użytkownika -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-account-circle</v-icon>
            Konto użytkownika
          </h3>

          <v-card
            variant="tonal"
            :color="technician.user ? 'success' : 'warning'"
            class="account-card"
          >
            <v-card-text class="pa-3">
              <div class="d-flex align-center">
                <v-avatar
                  :color="technician.user ? 'success' : 'warning'"
                  size="40"
                  class="mr-3"
                >
                  <v-icon color="white">
                    {{ technician.user ? 'mdi-account-check' : 'mdi-account-off' }}
                  </v-icon>
                </v-avatar>
                <div>
                  <template v-if="technician.user">
                    <p class="text-body-1 font-weight-medium mb-0">
                      {{ technician.user.username }}
                    </p>
                    <p class="text-caption text-medium-emphasis mb-0">
                      Konto aktywne
                    </p>
                  </template>
                  <template v-else>
                    <p class="text-body-1 font-weight-medium mb-0">
                      Brak konta
                    </p>
                    <p class="text-caption text-medium-emphasis mb-0">
                      Serwisant nie ma dostępu do systemu
                    </p>
                  </template>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Statystyki zgłoszeń -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-ticket</v-icon>
            Zgłoszenia serwisowe
          </h3>

          <div v-if="isLoadingStats" class="d-flex justify-center py-4">
            <v-progress-circular indeterminate color="primary" size="32" />
          </div>

          <v-row v-else dense>
            <v-col cols="6">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="warning" class="mb-1">
                    mdi-alert-circle
                  </v-icon>
                  <div class="text-h5 font-weight-bold text-warning">
                    {{ stats.open_tickets_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Otwarte
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="6">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="info" class="mb-1">
                    mdi-progress-clock
                  </v-icon>
                  <div class="text-h5 font-weight-bold text-info">
                    {{ stats.in_progress_tickets_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    W toku
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="6">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="success" class="mb-1">
                    mdi-check-circle
                  </v-icon>
                  <div class="text-h5 font-weight-bold text-success">
                    {{ stats.closed_tickets_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Zamknięte
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="6">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="primary" class="mb-1">
                    mdi-clipboard-list
                  </v-icon>
                  <div class="text-h5 font-weight-bold">
                    {{ stats.assigned_tickets_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Łącznie
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Certyfikaty -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-certificate</v-icon>
            Certyfikaty / Uprawnienia
          </h3>

          <div v-if="isLoadingStats" class="d-flex justify-center py-4">
            <v-progress-circular indeterminate color="primary" size="32" />
          </div>

          <v-row v-else dense>
            <v-col cols="4">
              <v-card variant="outlined" class="stat-card">
                <v-card-text class="pa-3 text-center">
                  <v-icon size="24" color="success" class="mb-1">
                    mdi-shield-check
                  </v-icon>
                  <div class="text-h5 font-weight-bold text-success">
                    {{ stats.valid_certifications_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Ważne
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="4">
              <v-card
                variant="outlined"
                class="stat-card"
                :class="{ 'border-warning': stats.expiring_soon_count > 0 }"
              >
                <v-card-text class="pa-3 text-center">
                  <v-icon
                    size="24"
                    :color="stats.expiring_soon_count > 0 ? 'warning' : 'grey'"
                    class="mb-1"
                  >
                    mdi-clock-alert
                  </v-icon>
                  <div
                    class="text-h5 font-weight-bold"
                    :class="stats.expiring_soon_count > 0 ? 'text-warning' : ''"
                  >
                    {{ stats.expiring_soon_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Wygasa
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col cols="4">
              <v-card
                variant="outlined"
                class="stat-card"
                :class="{ 'border-error': stats.expired_certifications_count > 0 }"
              >
                <v-card-text class="pa-3 text-center">
                  <v-icon
                    size="24"
                    :color="stats.expired_certifications_count > 0 ? 'error' : 'grey'"
                    class="mb-1"
                  >
                    mdi-shield-off
                  </v-icon>
                  <div
                    class="text-h5 font-weight-bold"
                    :class="stats.expired_certifications_count > 0 ? 'text-error' : ''"
                  >
                    {{ stats.expired_certifications_count }}
                  </div>
                  <div class="text-caption text-medium-emphasis">
                    Wygasłe
                  </div>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <!-- Alert o wygasających certyfikatach -->
          <v-alert
            v-if="stats.expiring_soon_count > 0"
            type="warning"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            <template #prepend>
              <v-icon>mdi-alert</v-icon>
            </template>
            {{ stats.expiring_soon_count }} {{ getCertLabel(stats.expiring_soon_count) }} wygasa w ciągu 30 dni
          </v-alert>

          <v-alert
            v-if="stats.expired_certifications_count > 0"
            type="error"
            variant="tonal"
            density="compact"
            class="mt-3"
          >
            <template #prepend>
              <v-icon>mdi-alert-circle</v-icon>
            </template>
            {{ stats.expired_certifications_count }} {{ getCertLabel(stats.expired_certifications_count) }} wygasło
          </v-alert>
        </div>

        <v-divider class="my-4" />

        <!-- Sekcja: Informacje -->
        <div class="detail-section">
          <h3 class="section-title">
            <v-icon start size="18">mdi-information</v-icon>
            Informacje
          </h3>

          <div class="info-list">
            <div class="info-item">
              <v-icon size="16" color="grey" class="mr-2">mdi-shield-account</v-icon>
              <span class="text-body-2 text-medium-emphasis">
                Rola: {{ technician.role_display }}
              </span>
            </div>
            <div class="info-item">
              <v-icon
                size="16"
                :color="technician.is_active ? 'success' : 'error'"
                class="mr-2"
              >
                {{ technician.is_active ? 'mdi-check-circle' : 'mdi-close-circle' }}
              </v-icon>
              <span class="text-body-2 text-medium-emphasis">
                Status: {{ technician.is_active ? 'Aktywny' : 'Nieaktywny' }}
              </span>
            </div>
            <div v-if="technician.user" class="info-item">
              <v-icon size="16" color="success" class="mr-2">mdi-account-check</v-icon>
              <span class="text-body-2 text-medium-emphasis">
                Ma dostęp do systemu
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
          @click="$emit('edit', technician)"
        >
          Edytuj
        </v-btn>
        <v-btn
          v-if="technician.email"
          variant="tonal"
          prepend-icon="mdi-email"
          class="flex-grow-1"
          :href="`mailto:${technician.email}`"
        >
          Email
        </v-btn>
        <v-btn
          v-if="technician.phone_number"
          variant="tonal"
          prepend-icon="mdi-phone"
          class="flex-grow-1"
          :href="`tel:${technician.phone_number}`"
        >
          Zadzwoń
        </v-btn>
      </div>
    </template>

    <!-- Pusty stan -->
    <div v-else class="empty-state">
      <v-icon size="64" color="grey-lighten-2">mdi-account-off</v-icon>
      <p class="text-body-1 text-medium-emphasis mt-4">
        Wybierz serwisanta, aby zobaczyć szczegóły
      </p>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import type { Technician, TechnicianStats } from '@/types';
import { fetchTechnicianStats } from '@/api/technicians';

const props = defineProps<{
  modelValue: boolean;
  technician: Technician | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'edit', technician: Technician): void;
}>();

const isDrawerOpen = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

// Stats
const isLoadingStats = ref(false);
const stats = ref<TechnicianStats>({
  assigned_tickets_count: 0,
  open_tickets_count: 0,
  in_progress_tickets_count: 0,
  closed_tickets_count: 0,
  valid_certifications_count: 0,
  expiring_soon_count: 0,
  expired_certifications_count: 0,
});

// Fetch stats when technician changes
watch(() => props.technician, async (newTechnician) => {
  if (newTechnician) {
    isLoadingStats.value = true;
    try {
      stats.value = await fetchTechnicianStats(newTechnician.id);
    } catch (error) {
      console.error('Błąd pobierania statystyk:', error);
      stats.value = {
        assigned_tickets_count: 0,
        open_tickets_count: 0,
        in_progress_tickets_count: 0,
        closed_tickets_count: 0,
        valid_certifications_count: 0,
        expiring_soon_count: 0,
        expired_certifications_count: 0,
      };
    } finally {
      isLoadingStats.value = false;
    }
  }
}, { immediate: true });

// Get initials from name
function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

// Phone formatting
function formatPhone(phone: string): string {
  if (!phone) return '—';
  const cleaned = phone.replace(/\D/g, '');
  if (cleaned.length === 9) {
    return `${cleaned.slice(0, 3)} ${cleaned.slice(3, 6)} ${cleaned.slice(6)}`;
  }
  return phone;
}

// Certificate label
function getCertLabel(count: number): string {
  if (count === 1) return 'certyfikat';
  if (count >= 2 && count <= 4) return 'certyfikaty';
  return 'certyfikatów';
}
</script>

<style scoped>
.technician-details-drawer {
  display: flex;
  flex-direction: column;
}

.technician-details-drawer :deep(.v-navigation-drawer__content) {
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

/* Contact list */
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

/* Account card */
.account-card {
  border-radius: 12px;
}

/* Stat cards */
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

.stat-card.border-error {
  border-color: rgb(var(--v-theme-error)) !important;
}

/* Info list */
.info-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  align-items: center;
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
