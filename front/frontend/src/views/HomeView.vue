<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">Pulpit</h1>

    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Wszystkie urządzenia"
          :value="devicesStore.deviceCount"
          :loading="devicesStore.isLoading"
          icon="mdi-printer-pos"
          color="primary"
          :to="{ name: 'device-list' }"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Aktywni serwisanci"
          :value="techniciansStore.technicianCount"
          :loading="techniciansStore.isLoading"
          icon="mdi-account-hard-hat"
          color="success"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Zlecenia w toku"
          :value="ticketsStore.inProgressCount"
          :loading="ticketsStore.isLoading"
          icon="mdi-clipboard-text-clock-outline"
          color="warning"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Klienci"
          :value="clientsStore.clientCount"
          :loading="clientsStore.isLoading"
          icon="mdi-account-multiple"
          color="secondary"
          :to="{ name: 'client-list' }"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import DashboardStatCard from '@/components/dashboard/DashboardStatCard.vue';
import { useDevicesStore } from '@/stores/devices';
import { useClientsStore } from '@/stores/clients';
import { useTechniciansStore } from '@/stores/technicians';
import { useTicketsStore } from '@/stores/tickets';

const devicesStore = useDevicesStore();
const clientsStore = useClientsStore();
const techniciansStore = useTechniciansStore();
const ticketsStore = useTicketsStore();

onMounted(() => {
  devicesStore.fetchDevices();
  clientsStore.fetchClients();
  techniciansStore.fetchTechnicians();
  ticketsStore.fetchTickets();
});
</script>
