<!-- src/views/HomeView.vue -->
<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">Pulpit</h1>

    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Wszystkie urządzenia"
          :value="devicesStore.totalDevices"
          :loading="devicesStore.isLoading"
          icon="mdi-printer-pos"
          color="primary"
          :to="{ name: 'devices' }"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Aktywni serwisanci"
          value="12"
          :loading="false"
        icon="mdi-account-hard-hat"
        color="success"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Zlecenia w toku"
          value="3"
          :loading="false"
          icon="mdi-clipboard-text-clock-outline"
          color="warning"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          title="Klienci"
          :value="clientsStore.totalClients"
          :loading="clientsStore.isLoading"
          icon="mdi-account-multiple"
          color="primary"
          :to="{ name: 'clients' }"
        />
      </v-col>

    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import DashboardStatCard from '@/components/dashboard/DashboardStatCard.vue'
import { useDevicesStore } from '@/stores/devices'
import { useClientsStore } from '@/stores/clients'

const devicesStore = useDevicesStore()
const clientsStore = useClientsStore()

onMounted(() => {
  devicesStore.fetchDevices()
  clientsStore.fetchClients()
});
</script>
