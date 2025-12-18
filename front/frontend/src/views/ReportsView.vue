<template>
  <v-container fluid>
    <v-card class="report-card">
      <v-card-title class="d-flex align-center text-h5">
        <v-icon start>mdi-file-chart-outline</v-icon>
        Generator Raportów Zbiorczych
      </v-card-title>
      <v-card-subtitle>Wybierz kryteria, aby wygenerować raport PDF dla urządzeń.</v-card-subtitle>
      <v-divider class="mt-4"></v-divider>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <h3 class="text-subtitle-1 font-weight-medium mb-3">1. Wybierz zakres urządzeń</h3>

            <!-- KLIENCI -->
            <div class="mb-1 d-flex align-center justify-space-between">
              <span>Klienci</span>
              <div>
                <v-btn class="btn-all" size="x-small" variant="text" @click="selectAllClients">Zaznacz wszystko</v-btn>
                <v-btn class="btn-clear" size="x-small" variant="text" @click="parameters.clients = []">Wyczyść</v-btn>
              </div>
            </div>

            <v-select
              v-model="parameters.clients"
              :items="filterOptions?.clients || []"
              item-title="name"
              item-value="id"
              multiple
              chips
              clearable
              class="scroll-select"
              label="Klienci (opcjonalnie)"
            ></v-select>

            <!-- PRODUCENCI -->
            <div class="mt-4 mb-1 d-flex align-center justify-space-between">
              <span>Producenci</span>
              <div>
                <v-btn class="btn-all" size="x-small" variant="text" @click="selectAllBrands">Zaznacz wszystko</v-btn>
                <v-btn class="btn-clear" size="x-small" variant="text" @click="parameters.device_brands = []">Wyczyść</v-btn>
              </div>
            </div>

            <v-select
              v-model="parameters.device_brands"
              :items="filterOptions?.brands || []"
              item-title="name"
              item-value="id"
              multiple
              chips
              clearable
              class="scroll-select"
              label="Producenci (opcjonalnie)"
            ></v-select>

            <!-- URZĄDZENIA -->
            <div class="mt-4 mb-1 d-flex align-center justify-space-between">
              <span>Urządzenia</span>
              <div>
                <v-btn class="btn-all" size="x-small" variant="text" @click="selectAllDevices">Zaznacz wszystko</v-btn>
                <v-btn class="btn-clear" size="x-small" variant="text" @click="parameters.devices = []">Wyczyść</v-btn>
              </div>
            </div>

            <v-select
              v-model="parameters.devices"
              :items="filteredDevicesForSelect"
              :loading="isDevicesLoading"
              item-title="display_name"
              item-value="id"
              multiple
              chips
              clearable
              class="scroll-select"
              label="Konkretne urządzenia (opcjonalnie)"
              no-data-text="Brak urządzeń pasujących do filtrów"
            ></v-select>
          </v-col>

          <!-- PRAWA KOLUMNA: ZAWARTOŚĆ I AKCJE -->
          <v-col cols="12" md="6">
            <h3 class="text-subtitle-1 font-weight-medium mb-3">2. Wybierz zawartość raportu</h3>
            <v-checkbox
              v-model="parameters.include_service_history"
              label="Dołącz historię zleceń serwisowych"
              hide-details
            ></v-checkbox>

            <v-expand-transition>
              <div v-if="parameters.include_service_history" class="ml-8 mt-2 date-range-box">
                <p class="text-caption mb-2">Określ zakres dat dla historii zleceń:</p>

                <!-- Zamienione na Twój komponent DatePicker (od) -->
                <DatePicker
                  v-model="parameters.history_date_from"
                  label="Historia od"
                  clearable
                ></DatePicker>

                <!-- Zamienione na Twój komponent DatePicker (do) -->
                <DatePicker
                  v-model="parameters.history_date_to"
                  label="Historia do"
                  clearable
                  class="mt-2"
                ></DatePicker>
              </div>
            </v-expand-transition>

            <v-checkbox
              v-model="parameters.include_event_log"
              label="Dołącz dziennik zdarzeń (przeglądy, itp.)"
              class="mt-3"
              hide-details
            ></v-checkbox>
          </v-col>
        </v-row>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-btn variant="text" @click="handleClearForm">Wyczyść formularz</v-btn>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          size="large"
          variant="flat"
          :loading="reportsStore.isLoading"
          :disabled="isExportDisabled"
          prepend-icon="mdi-file-pdf-box"
          @click="handleExportPdf"
        >
          Eksportuj PDF
        </v-btn>
      </v-card-actions>

      <v-alert v-if="reportsStore.error || devicesStore.error" type="error" closable class="ma-4">
        {{ reportsStore.error || devicesStore.error }}
      </v-alert>

    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted, computed, watch } from 'vue';
import { useReportsStore } from '@/stores/reports';
import { useDevicesStore } from '@/stores/devices';
import { storeToRefs } from 'pinia';
import DatePicker from '@/components/common/DatePicker.vue';

const reportsStore = useReportsStore();
const devicesStore = useDevicesStore();

const { parameters, filterOptions } = storeToRefs(reportsStore);
const { filteredForSelect: filteredDevicesForSelect, isLoadingForSelect: isDevicesLoading } = storeToRefs(devicesStore);

const isExportDisabled = computed(() => {
  const noBaseFilters = !parameters.value.clients?.length && !parameters.value.device_brands?.length && !parameters.value.devices?.length;
  return noBaseFilters || reportsStore.isLoading || isDevicesLoading.value;
});

const selectAllClients = () => {
  parameters.value.clients = (filterOptions.value?.clients || []).map(c => c.id);
};

const selectAllBrands = () => {
  parameters.value.device_brands = (filterOptions.value?.brands || []).map(b => b.id);
};

const selectAllDevices = () => {
  parameters.value.devices = filteredDevicesForSelect.value.map(d => d.id);
};

watch(
  () => [parameters.value.clients, parameters.value.device_brands],
  async (newValue) => {
    // Wyczyść wybrane urządzenia, jeśli zmienią się filtry nadrzędne
    parameters.value.devices = [];

    const [clients, brands] = newValue;
    // Wywołaj akcję. Komponent automatycznie się zaktualizuje dzięki `storeToRefs`
    await devicesStore.fetchFilteredForSelect({
      clients: clients,
      brands: brands
    });
  },
  { deep: true }
);

const handleExportPdf = () => {
  reportsStore.error = null;
  devicesStore.error = null;
  reportsStore.exportReport('pdf');
};

const handleClearForm = () => {
  reportsStore.clearParameters();
};

onMounted(() => {
  if (!reportsStore.filterOptions) {
    reportsStore.fetchFilterOptions();
  }
});
</script>

<style scoped>
.btn-all{
  background-color: #1976d2;
  color: white;
}
.btn-clear{

}
.scroll-select :deep(.v-field__input) {
  max-height: 110px !important;
  overflow-y: auto !important;
  align-items: flex-start !important; /* żeby nie rozciągało pola */
}

/* Zmniejsza odstępy między chipami */
.scroll-select :deep(.v-select__selection) {
  padding-top: 4px;
  padding-bottom: 4px;
}

.date-range-box {
  border-left: 2px solid #e0e0e0;
  padding-left: 1rem;
}
</style>
