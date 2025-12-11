<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">{{ t('dashboard.title') }}</h1>

    <v-row>
      <v-col
        v-for="card in statsCards"
        :key="card.titleKey"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <DashboardStatCard
          :title="t(card.titleKey)"
          :value="card.value"
          :loading="card.loading"
          :icon="card.icon"
          :color="card.color"
          :to="card.to"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import type { RouteLocationRaw } from 'vue-router';

import DashboardStatCard from '@/components/dashboard/DashboardStatCard.vue';
import { useDevicesStore } from '@/stores/devices';
import { useClientsStore } from '@/stores/clients';
import { useTechniciansStore } from '@/stores/technicians';
import { useTicketsStore } from '@/stores/tickets';
import { useManufacturersStore } from '@/stores/manufacturers';
import { useCertificationsStore } from '@/stores/certifications';

const { t } = useI18n();

// Stores
const devicesStore = useDevicesStore();
const clientsStore = useClientsStore();
const techniciansStore = useTechniciansStore();
const ticketsStore = useTicketsStore();
const manufacturersStore = useManufacturersStore();
const certificationsStore = useCertificationsStore();

// Interfejs dla konfiguracji kart
interface StatCardConfig {
  titleKey: string;
  value: number;
  loading: boolean;
  icon: string;
  color: string;
  to: RouteLocationRaw;
}

// Reaktywna konfiguracja kart
const statsCards = computed<StatCardConfig[]>(() => [
  {
    titleKey: 'dashboard.cards.devices',
    value: devicesStore.deviceCount ?? 0,
    loading: devicesStore.isLoading,
    icon: 'mdi-printer-pos',
    color: 'primary',
    to: { name: 'device-list' },
  },
  {
    titleKey: 'dashboard.cards.technicians',
    value: techniciansStore.technicianCount ?? 0,
    loading: techniciansStore.isLoading,
    icon: 'mdi-account-hard-hat',
    color: 'success',
    to: { name: 'technician-list' },
  },
  {
    titleKey: 'dashboard.cards.ticketsInProgress',
    value: ticketsStore.inProgressCount ?? 0,
    loading: ticketsStore.isLoading,
    icon: 'mdi-clipboard-text-clock-outline',
    color: 'warning',
    to: { name: 'ticket-list', query: { status: 'in-progress' } },
  },
  {
    titleKey: 'dashboard.cards.clients',
    value: clientsStore.clientCount ?? 0,
    loading: clientsStore.isLoading,
    icon: 'mdi-account-multiple',
    color: 'secondary',
    to: { name: 'client-list' },
  },
  {
    titleKey: 'dashboard.cards.manufacturers',
    value: manufacturersStore.manufacturerCount ?? 0,
    loading: manufacturersStore.isLoading,
    icon: 'mdi-factory',
    color: 'error', // Zmienione z 'red' na 'error'
    to: { name: 'manufacturer-list' },
  },
  {
    titleKey: 'dashboard.cards.certifications',
    value: certificationsStore.certifications?.length ?? 0,
    loading: certificationsStore.isLoading,
    icon: 'mdi-certificate',
    color: 'teal',
    to: { name: 'certification-list' },
  },
]);

// Fetch data on mount
onMounted(async () => {
  await Promise.allSettled([
    devicesStore.fetchDevices(),
    clientsStore.fetchClients(),
    techniciansStore.fetchTechnicians(),
    ticketsStore.fetchTickets(),
    manufacturersStore.fetchManufacturers(),
    certificationsStore.fetchCertifications(),
  ]);
});
</script>
