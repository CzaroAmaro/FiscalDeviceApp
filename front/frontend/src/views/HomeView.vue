<template>
  <v-container fluid>
    <h1 class="text-h4 mb-6">{{ t('dashboard.title') }}</h1>

    <v-row>
      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          :title="t('dashboard.cards.devices')"
          :value="devicesStore.deviceCount"
          :loading="devicesStore.isLoading"
          icon="mdi-printer-pos"
          color="primary"
          :to="{ name: 'device-list' }"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          :title="t('dashboard.cards.technicians')"
          :value="techniciansStore.technicianCount"
          :loading="techniciansStore.isLoading"
          icon="mdi-account-hard-hat"
          color="success"
          :to="{ name: 'technician-list' }"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          :title="t('dashboard.cards.ticketsInProgress')"
          :value="ticketsStore.inProgressCount"
          :loading="ticketsStore.isLoading"
          icon="mdi-clipboard-text-clock-outline"
          color="warning"
          :to="{ name: 'ticket-list', query: { status: 'in-progress' } }"
        />
      </v-col>

      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          :title="t('dashboard.cards.clients')"
          :value="clientsStore.clientCount"
          :loading="clientsStore.isLoading"
          icon="mdi-account-multiple"
          color="secondary"
          :to="{ name: 'client-list' }"
        />
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          :title="t('dashboard.cards.manufacturers')"
          :value="manufacturersStore.manufacturerCount"
          :loading="manufacturersStore.isLoading"
          icon="mdi-factory"
          color="red"
          :to="{ name: 'manufacturer-list' }"
        />
      </v-col>
      <v-col cols="12" sm="6" md="4" lg="3">
        <DashboardStatCard
          :title="t('dashboard.cards.certifications')"
          :value="certificationsStore.certifications.length"
          :loading="certificationsStore.isLoading"
          icon="mdi-certificate"
          color="teal"
          :to="{ name: 'certification-list' }"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import DashboardStatCard from '@/components/dashboard/DashboardStatCard.vue'
import { useDevicesStore } from '@/stores/devices'
import { useClientsStore } from '@/stores/clients'
import { useTechniciansStore } from '@/stores/technicians'
import { useTicketsStore } from '@/stores/tickets'
import { useI18n } from 'vue-i18n';
import { useManufacturersStore } from '@/stores/manufacturers.ts'
import { useCertificationsStore } from '@/stores/certifications.ts'

const { t } = useI18n();

const devicesStore = useDevicesStore()
const clientsStore = useClientsStore()
const techniciansStore = useTechniciansStore()
const ticketsStore = useTicketsStore()
const manufacturersStore = useManufacturersStore()
const certificationsStore = useCertificationsStore()

onMounted(() => {
  devicesStore.fetchDevices()
  clientsStore.fetchClients()
  techniciansStore.fetchTechnicians()
  ticketsStore.fetchTickets()
  manufacturersStore.fetchManufacturers()
  certificationsStore.fetchCertifications()
})
</script>
