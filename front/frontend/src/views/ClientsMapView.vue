<template>
  <v-container fluid>
    <v-card>
      <v-toolbar flat>
        <v-toolbar-title>{{ t('clientsMap.title') }}</v-toolbar-title>
        <v-spacer />
        <v-switch
          v-model="showOnlyWithOpenTickets"
          :label="t('clientsMap.filterLabel')"
          color="primary"
          hide-details
          class="mr-4"
        />
        <v-btn icon @click="clientsStore.fetchClientLocations(true)">
          <v-icon>mdi-refresh</v-icon>
        </v-btn>
      </v-toolbar>

      <v-card-text class="pa-0">
        <v-progress-linear v-if="clientsStore.isLoadingLocations" indeterminate />
        <v-alert v-if="clientsStore.error" type="error" density="compact" tile>
          {{ clientsStore.error }}
        </v-alert>

        <div style="height: 75vh; width: 100%">
          <l-map
            :zoom="zoom"
            :center="center"
            :use-global-leaflet="true"
          >
            <l-tile-layer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              layer-type="base"
              name="OpenStreetMap"
              :attribution="attribution"
            />


              <l-marker
                v-for="client in filteredClients"
                :key="client.id"
                :lat-lng="[client.latitude, client.longitude]"
              >
                <l-popup>
                  <div>{{ client.name }}</div>
                </l-popup>
              </l-marker>

          </l-map>
        </div>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useClientsStore } from '@/stores/clients';
import type { ClientLocation } from '@/types';

import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';

const { t } = useI18n();
const clientsStore = useClientsStore();

const zoom = ref(6);
const center = ref([52.237049, 21.017532]);
const attribution =
  '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors';

const showOnlyWithOpenTickets = ref(false);

const filteredClients = computed<ClientLocation[]>(() => {
  if (!showOnlyWithOpenTickets.value) {
    return clientsStore.clientLocations;
  }
  return clientsStore.clientLocations.filter((c) => c.has_open_tickets);
});

onMounted(() => {
  clientsStore.fetchClientLocations();
});
</script>

<style scoped>
.leaflet-popup-content a {
  color: #1976d2;
  text-decoration: none;
}
.leaflet-popup-content a:hover {
  text-decoration: underline;
}
</style>
