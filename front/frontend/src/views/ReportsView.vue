<template>
  <v-container fluid>
    <v-card class="report-card">
      <v-card-title class="d-flex align-center text-h5">
        <v-icon start>mdi-file-chart-outline</v-icon>
        {{ t('reports.generator.title') }}
      </v-card-title>
      <v-card-subtitle>{{ t('reports.generator.subtitle') }}</v-card-subtitle>
      <v-divider class="mt-4"></v-divider>

      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <h3 class="text-subtitle-1 font-weight-medium mb-3">{{ t('reports.generator.step1') }}</h3>

            <div class="mb-1 d-flex align-center justify-space-between">
              <span>{{ t('reports.generator.clients') }}</span>
              <div>
                <v-btn class="btn-all" size="x-small" variant="text" @click="selectAllClients">
                  {{ t('table.selectAll') }}
                </v-btn>
                <v-btn class="btn-clear" size="x-small" variant="text" @click="parameters.clients = []">
                  {{ t('common.clear') }}
                </v-btn>
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
              :label="t('reports.generator.clientsLabel')"
            ></v-select>

            <div class="mt-4 mb-1 d-flex align-center justify-space-between">
              <span>{{ t('reports.generator.manufacturers') }}</span>
              <div>
                <v-btn class="btn-all" size="x-small" variant="text" @click="selectAllBrands">
                  {{ t('table.selectAll') }}
                </v-btn>
                <v-btn class="btn-clear" size="x-small" variant="text" @click="parameters.device_brands = []">
                  {{ t('common.clear') }}
                </v-btn>
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
              :label="t('reports.generator.manufacturersLabel')"
            ></v-select>

            <div class="mt-4 mb-1 d-flex align-center justify-space-between">
              <span>{{ t('reports.generator.devices') }}</span>
              <div>
                <v-btn class="btn-all" size="x-small" variant="text" @click="selectAllDevices">
                  {{ t('table.selectAll') }}
                </v-btn>
                <v-btn class="btn-clear" size="x-small" variant="text" @click="parameters.devices = []">
                  {{ t('common.clear') }}
                </v-btn>
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
              :label="t('reports.generator.devicesLabel')"
              :no-data-text="t('reports.generator.noDevicesMatch')"
            ></v-select>
          </v-col>

          <v-col cols="12" md="6">
            <h3 class="text-subtitle-1 font-weight-medium mb-3">{{ t('reports.generator.step2') }}</h3>
            <v-checkbox
              v-model="parameters.include_service_history"
              :label="t('reports.generator.includeServiceHistory')"
              hide-details
            ></v-checkbox>

            <v-expand-transition>
              <div v-if="parameters.include_service_history" class="ml-8 mt-2 date-range-box">
                <p class="text-caption mb-2">{{ t('reports.generator.historyDateRangeHint') }}</p>

                <DatePicker
                  :model-value="parameters.history_date_from || null"
                  :label="t('reports.generator.historyFrom')"
                  clearable
                  @update:model-value="val => parameters.history_date_from = val"
                ></DatePicker>

                <DatePicker
                  :model-value="parameters.history_date_to || null"
                  :label="t('reports.generator.historyTo')"
                  clearable
                  class="mt-2"
                  @update:model-value="val => parameters.history_date_to = val"
                ></DatePicker>
              </div>
            </v-expand-transition>

            <v-checkbox
              v-model="parameters.include_event_log"
              :label="t('reports.generator.includeEventLog')"
              class="mt-3"
              hide-details
            ></v-checkbox>
          </v-col>
        </v-row>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions class="pa-4">
        <v-btn variant="text" @click="handleClearForm">{{ t('reports.generator.clearForm') }}</v-btn>
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
          {{ t('devices.toolbar.exportPdf') }}
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
import { useI18n } from 'vue-i18n';
import { useReportsStore } from '@/stores/reports';
import { useDevicesStore } from '@/stores/devices';
import { storeToRefs } from 'pinia';
import DatePicker from '@/components/common/DatePicker.vue';

const { t } = useI18n();
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
    parameters.value.devices = [];

    const [clients, brands] = newValue;
    await devicesStore.fetchFilteredForSelect({
      clients: clients,
      brands: brands
    });
  },
  { deep: true }
);

watch(
  () => parameters.value.include_service_history,
  (newValue) => {
    if (newValue) {
      if (parameters.value.history_date_from === undefined) parameters.value.history_date_from = null;
      if (parameters.value.history_date_to === undefined) parameters.value.history_date_to = null;
    }
  }
);

const handleExportPdf = () => {
  reportsStore.error = null;
  devicesStore.error = null;
  reportsStore.exportReport('pdf');
};

const handleClearForm = () => {
  reportsStore.clearParameters();
  parameters.value.include_service_history = false;
  parameters.value.include_event_log = false;
  parameters.value.history_date_from = null;
  parameters.value.history_date_to = null;
};

onMounted(() => {
  if (!reportsStore.filterOptions) {
    reportsStore.fetchFilterOptions();
  }

  if (parameters.value.history_date_from === undefined) parameters.value.history_date_from = null;
  if (parameters.value.history_date_to === undefined) parameters.value.history_date_to = null;
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
  align-items: flex-start !important;
}

.scroll-select :deep(.v-select__selection) {
  padding-top: 4px;
  padding-bottom: 4px;
}

.date-range-box {
  border-left: 2px solid #e0e0e0;
  padding-left: 1rem;
}
</style>
