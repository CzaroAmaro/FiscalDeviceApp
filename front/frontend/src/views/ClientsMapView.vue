<template>
  <v-container fluid class="map-container pa-4">
    <div class="page-header mb-4">
      <div class="d-flex align-center justify-space-between flex-wrap ga-4">
        <div>
          <div class="d-flex align-center ga-2 mb-1">
            <v-btn
              v-if="focusedClientId"
              icon
              variant="text"
              size="small"
              @click="clearFocus"
            >
              <v-icon>mdi-arrow-left</v-icon>
              <v-tooltip activator="parent" location="bottom">Wróć do widoku wszystkich</v-tooltip>
            </v-btn>
            <h1 class="text-h4 font-weight-bold mb-0">
              {{ focusedClient ? focusedClient.name : t('clientsMap.title') }}
            </h1>
          </div>
          <p class="text-body-2 text-medium-emphasis mb-0">
            {{ focusedClient ? 'Lokalizacja klienta na mapie' : 'Lokalizacje klientów na mapie interaktywnej' }}
          </p>
        </div>

        <div class="d-flex align-center ga-3">
          <v-chip color="primary" variant="tonal" size="small">
            <v-icon start size="14">mdi-map-marker</v-icon>
            {{ clientsStore.clientLocations.length }} lokalizacji
          </v-chip>
          <v-chip
            v-if="clientsWithOpenTickets > 0"
            color="warning"
            variant="tonal"
            size="small"
          >
            <v-icon start size="14">mdi-alert-circle</v-icon>
            {{ clientsWithOpenTickets }} z otwartymi zgłoszeniami
          </v-chip>
        </div>
      </div>
    </div>

    <v-row>
      <v-col cols="12" md="3" lg="3" xl="2" order="2" order-md="1">
        <v-card rounded="lg" class="sidebar-card">
          <div class="pa-4">
            <h3 class="text-subtitle-2 font-weight-bold mb-3 d-flex align-center">
              <v-icon start size="18">mdi-magnify</v-icon>
              Szukaj klienta
            </h3>

            <v-text-field
              v-model="searchQuery"
              prepend-inner-icon="mdi-magnify"
              placeholder="Wpisz nazwę..."
              variant="outlined"
              density="compact"
              hide-details
              clearable
              class="mb-4"
            />

            <v-btn
              block
              variant="tonal"
              color="primary"
              prepend-icon="mdi-refresh"
              :loading="clientsStore.isLoadingLocations"
              @click="refreshData"
            >
              Odśwież dane
            </v-btn>
          </div>

          <v-divider />

          <div class="clients-list">
            <div class="pa-3 bg-grey-lighten-4">
              <span class="text-caption font-weight-medium text-medium-emphasis">
                KLIENCI ({{ filteredClients.length }})
              </span>
            </div>

            <v-list density="compact" class="py-0">
              <v-list-item
                v-for="client in visibleClients"
                :key="client.id"
                :class="{ 'selected-client': selectedClientId === client.id }"
                class="client-list-item"
                @click="focusOnClient(client)"
              >
                <template #prepend>
                  <v-avatar
                    :color="client.has_open_tickets ? 'warning' : 'primary'"
                    size="32"
                    variant="tonal"
                  >
                    <v-icon size="16">mdi-domain</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="text-body-2 font-weight-medium">
                  {{ client.name }}
                </v-list-item-title>
                <v-list-item-subtitle class="text-caption">
                  <v-icon
                    v-if="client.has_open_tickets"
                    size="12"
                    color="warning"
                    class="mr-1"
                  >
                    mdi-alert-circle
                  </v-icon>
                  {{ client.has_open_tickets ? 'Ma otwarte zgłoszenia' : 'Brak zgłoszeń' }}
                </v-list-item-subtitle>

                <template #append>
                  <v-icon size="16" color="grey">mdi-chevron-right</v-icon>
                </template>
              </v-list-item>

              <v-list-item
                v-if="filteredClients.length > visibleClientsCount"
                class="text-center"
                @click="visibleClientsCount += 20"
              >
                <v-btn variant="text" size="small" color="primary">
                  Pokaż więcej ({{ filteredClients.length - visibleClientsCount }})
                </v-btn>
              </v-list-item>

              <v-list-item v-if="filteredClients.length === 0">
                <div class="text-center py-4 text-medium-emphasis">
                  <v-icon size="32" class="mb-2">mdi-map-marker-off</v-icon>
                  <p class="text-body-2 mb-0">Brak klientów do wyświetlenia</p>
                </div>
              </v-list-item>
            </v-list>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" md="9" lg="9" xl="10" order="1" order-md="2">
        <v-card rounded="lg" class="map-card">
          <div class="map-toolbar pa-3">
            <div class="d-flex align-center justify-space-between">
              <div class="d-flex align-center ga-2">
                <v-chip
                  :color="mapStyle === 'street' ? 'primary' : undefined"
                  :variant="mapStyle === 'street' ? 'flat' : 'outlined'"
                  size="small"
                  @click="mapStyle = 'street'"
                >
                  <v-icon start size="16">mdi-map</v-icon>
                  Ulice
                </v-chip>
                <v-chip
                  :color="mapStyle === 'satellite' ? 'primary' : undefined"
                  :variant="mapStyle === 'satellite' ? 'flat' : 'outlined'"
                  size="small"
                  @click="mapStyle = 'satellite'"
                >
                  <v-icon start size="16">mdi-satellite-variant</v-icon>
                  Satelita
                </v-chip>
              </div>

              <div class="d-flex align-center ga-1">
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="handleZoomIn"
                >
                  <v-icon>mdi-plus</v-icon>
                  <v-tooltip activator="parent" location="bottom">Przybliż</v-tooltip>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="handleZoomOut"
                >
                  <v-icon>mdi-minus</v-icon>
                  <v-tooltip activator="parent" location="bottom">Oddal</v-tooltip>
                </v-btn>
                <v-btn
                  icon
                  variant="text"
                  size="small"
                  @click="handleFitBounds"
                >
                  <v-icon>mdi-fit-to-screen</v-icon>
                  <v-tooltip activator="parent" location="bottom">Dopasuj widok</v-tooltip>
                </v-btn>
              </div>
            </div>
          </div>

          <v-divider />

          <v-progress-linear
            v-if="clientsStore.isLoadingLocations"
            indeterminate
            color="primary"
            height="3"
          />

          <v-alert
            v-if="clientsStore.error"
            type="error"
            variant="tonal"
            density="compact"
            class="ma-3"
            closable
          >
            {{ clientsStore.error }}
          </v-alert>

          <div class="map-wrapper">
            <l-map
              ref="mapRef"
              :zoom="currentZoom"
              :center="currentCenter"
              :use-global-leaflet="true"
              :options="mapOptions"
              @update:zoom="onZoomUpdate"
              @update:center="onCenterUpdate"
              @ready="onMapReady"
            >
              <l-tile-layer
                :key="mapStyle"
                :url="tileLayerUrl"
                layer-type="base"
                name="MapTiles"
                :attribution="attribution"
              />

              <l-marker
                v-for="client in filteredClients"
                :key="client.id"
                :lat-lng="[client.latitude, client.longitude]"
              >
                <l-popup :options="{ maxWidth: 280 }">
                  <div class="popup-content">
                    <div class="popup-header">
                      <div
                        class="popup-avatar"
                        :class="client.has_open_tickets ? 'bg-warning' : 'bg-primary'"
                      >
                        <span class="popup-avatar-icon">🏢</span>
                      </div>
                      <div class="popup-header-text">
                        <h4 class="popup-title">{{ client.name }}</h4>
                        <p v-if="client.has_open_tickets" class="popup-subtitle">
                          ⚠️ Ma otwarte zgłoszenia
                        </p>
                      </div>
                    </div>
                  </div>
                </l-popup>
              </l-marker>
            </l-map>

            <div class="map-legend">
              <div class="legend-item">
                <span class="legend-marker default"></span>
                <span class="text-caption">Klient</span>
              </div>
              <div class="legend-item">
                <span class="legend-marker warning"></span>
                <span class="text-caption">Z otwartymi zgłoszeniami</span>
              </div>
            </div>
          </div>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRoute, useRouter } from 'vue-router';
import { useClientsStore } from '@/stores/clients';
import type { ClientLocation } from '@/types';

import { LMap, LTileLayer, LMarker, LPopup } from '@vue-leaflet/vue-leaflet';

interface LeafletMapInstance {
  leafletObject: {
    setView: (center: [number, number], zoom: number, options?: { animate?: boolean }) => void;
    fitBounds: (bounds: [number, number][], options?: { padding?: [number, number] }) => void;
    zoomIn: () => void;
    zoomOut: () => void;
    getZoom: () => number;
    getCenter: () => { lat: number; lng: number };
  };
}

const { t } = useI18n();
const route = useRoute();
const router = useRouter();
const clientsStore = useClientsStore();

const mapRef = ref<LeafletMapInstance | null>(null);
const mapReady = ref(false);

const currentZoom = ref(6);
const currentCenter = ref<[number, number]>([52.237049, 21.017532]);
const mapStyle = ref<'street' | 'satellite'>('street');

const selectedClientId = ref<number | null>(null);
const searchQuery = ref('');
const visibleClientsCount = ref(20);

const focusedClientId = computed(() => {
  const id = route.query.clientId;
  return id ? Number(id) : null;
});

const focusedClient = computed(() => {
  if (!focusedClientId.value) return null;
  return clientsStore.clientLocations.find(c => c.id === focusedClientId.value) || null;
});

// Map options
const mapOptions = {
  zoomControl: false,
  attributionControl: true,
};

const attribution = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors';

const tileLayerUrl = computed(() => {
  if (mapStyle.value === 'satellite') {
    return 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
  }
  return 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
});

const filteredClients = computed<ClientLocation[]>(() => {
  let clients = clientsStore.clientLocations;

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    clients = clients.filter((c) =>
      c.name.toLowerCase().includes(query)
    );
  }

  return clients;
});

const visibleClients = computed(() => {
  return filteredClients.value.slice(0, visibleClientsCount.value);
});

const clientsWithOpenTickets = computed(() => {
  return clientsStore.clientLocations.filter(c => c.has_open_tickets).length;
});

function onZoomUpdate(newZoom: number) {
  currentZoom.value = newZoom;
}

function onCenterUpdate(newCenter: [number, number]) {
  currentCenter.value = newCenter;
}

function onMapReady() {
  mapReady.value = true;

  nextTick(() => {
    setTimeout(() => {
      if (focusedClient.value) {
        focusOnClient(focusedClient.value);
      } else if (filteredClients.value.length > 0) {
        handleFitBounds();
      }
    }, 500);
  });
}

watch(focusedClient, (client) => {
  if (client && mapReady.value) {
    focusOnClient(client);
  }
});

function handleZoomIn() {
  if (mapRef.value?.leafletObject) {
    mapRef.value.leafletObject.zoomIn();
  }
}

function handleZoomOut() {
  if (mapRef.value?.leafletObject) {
    mapRef.value.leafletObject.zoomOut();
  }
}

function handleFitBounds() {
  if (!mapRef.value?.leafletObject || filteredClients.value.length === 0) return;

  const map = mapRef.value.leafletObject;
  const bounds = filteredClients.value.map(c => [c.latitude, c.longitude] as [number, number]);

  if (bounds.length === 1) {
    map.setView(bounds[0], 14);
  } else if (bounds.length > 1) {
    map.fitBounds(bounds, { padding: [50, 50] });
  }
}

function focusOnClient(client: ClientLocation) {
  selectedClientId.value = client.id;

  if (mapRef.value?.leafletObject) {
    mapRef.value.leafletObject.setView(
      [client.latitude, client.longitude],
      15,
      { animate: true }
    );
  }
}

function clearFocus() {
  router.push({ name: 'client-map' });
  selectedClientId.value = null;

  nextTick(() => {
    setTimeout(() => {
      handleFitBounds();
    }, 100);
  });
}

function refreshData() {
  clientsStore.fetchClientLocations(true);
}

watch(searchQuery, () => {
  visibleClientsCount.value = 20;
});

onMounted(() => {
  clientsStore.fetchClientLocations();
});
</script>

<style scoped>
.map-container {
  height: 100%;
}

.page-header {
  padding-bottom: 8px;
}

.sidebar-card {
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.clients-list {
  flex: 1;
  overflow-y: auto;
}

.client-list-item {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.client-list-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05);
}

.selected-client {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
  border-left: 3px solid rgb(var(--v-theme-primary));
}

.map-card {
  height: calc(100vh - 180px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-toolbar {
  background: rgb(var(--v-theme-surface));
}

.map-wrapper {
  flex: 1;
  position: relative;
  min-height: 400px;
}

.map-wrapper :deep(.leaflet-container) {
  height: 100%;
  width: 100%;
  border-radius: 0 0 12px 12px;
  z-index: 0;
}

.map-legend {
  position: absolute;
  bottom: 24px;
  left: 16px;
  background: rgb(var(--v-theme-surface));
  padding: 12px 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-marker.default {
  background-color: #1976D2;
}

.legend-marker.warning {
  background-color: #FB8C00;
}

.popup-content {
  padding: 8px;
  min-width: 200px;
}

.popup-header {
  display: flex;
  align-items: center;
}

.popup-avatar {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
}

.popup-avatar.bg-primary {
  background-color: #1976D2;
}

.popup-avatar.bg-warning {
  background-color: #FB8C00;
}

.popup-avatar-icon {
  font-size: 20px;
}

.popup-header-text {
  flex: 1;
}

.popup-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
}

.popup-subtitle {
  font-size: 0.75rem;
  margin: 4px 0 0;
  color: #FB8C00;
}

/* Scrollbar */
.clients-list::-webkit-scrollbar {
  width: 6px;
}

.clients-list::-webkit-scrollbar-track {
  background: transparent;
}

.clients-list::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 3px;
}

@media (max-width: 960px) {
  .sidebar-card {
    height: auto;
    max-height: 300px;
    margin-bottom: 16px;
  }

  .map-card {
    height: calc(100vh - 500px);
    min-height: 400px;
  }
}
</style>
