<template>
  <v-container fluid>
    <TableToolbar
      :title="t('devices.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <!-- Pole wyszukiwania -->
    <div class="mb-4 flex items-center gap-3">
      <v-text-field
        v-model="searchQuery"
        density="compact"
        hide-details
        variant="solo"
        prepend-inner-icon="mdi-magnify"
        label="Szukaj po numerze unikatowym lub właścicielu"
        clearable
        style="max-width: 360px;"
        @click:clear="onClearSearch"
      />
    </div>

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="deviceHeaders"
        :items="filteredItems"
        :loading="isLoading"
        :items-per-page="25"
      >
        <template #item.status="{ item }">
          <DeviceStatusChip :status="item.status" />
        </template>
      </DataTable>
    </v-card>

    <!-- Formularze i modale -->
    <DeviceFormModal
      v-model="isFormOpen"
      :editing-device="itemToEdit"
      :newly-added-client-id="newlyCreatedClientId"
      @save-success="handleFormSave"
      @request-new-client="isClientModalOpen = true"
    />

    <ClientFormModal
      v-model="isClientModalOpen"
      :editing-client="null"
      @save-success="onClientSaveSuccess"
    />

    <!-- NOWY: Panel boczny ze szczegółami -->
    <DeviceDetailsDrawer
      v-model="isDetailsDrawerOpen"
      :device="itemToView"
      @edit="handleEditFromDrawer"
      @perform-service="handlePerformServiceFromDrawer"
      @export-pdf="handleExportPdfFromDrawer"
    />

    <PerformServiceModal
      v-model="isServiceModalOpen"
      :device="itemToPerformService"
      @success="handlePerformServiceConfirm"
    />

    <v-dialog v-model="isConfirmOpen" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5">{{ t('common.confirmDelete') }}</v-card-title>
        <v-card-text>
          {{ confirmMessage }}
          <br>{{ t('common.confirmDeleteMsg') }}
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text :disabled="isDeleting" @click="isConfirmOpen = false">{{ t('common.cancel') }}</v-btn>
          <v-btn color="error" :loading="isDeleting" @click="handleDeleteConfirm">{{ t('common.delete') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useDevicesStore } from '@/stores/devices';
import { useSnackbarStore } from '@/stores/snackbar';
import { useResourceView } from '@/composables/useResourceView';
import { getDeviceHeaders } from '@/config/tables/deviceHeaders';
import type { FiscalDevice, Client } from '@/types';
import { downloadDeviceReport, sendInspectionReminders, performDeviceService } from '@/api/devices';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import DeviceFormModal from '@/components/devices/DeviceFormModal.vue';
import DeviceStatusChip from '@/components/devices/DeviceStatusChip.vue';
import ClientFormModal from '@/components/clients/ClientFormModal.vue';
import DeviceDetailsDrawer from '@/components/devices/DeviceDetailsDrawer.vue';
import PerformServiceModal from '@/components/devices/PerformServiceModal.vue';

const { t } = useI18n();
const snackbarStore = useSnackbarStore();
const devicesStore = useDevicesStore();

const isExporting = ref(false);
const isSendingReminders = ref(false);
const isPerformingService = ref(false);

// Panel szczegółów
const isDetailsDrawerOpen = ref(false);
const itemToView = ref<FiscalDevice | null>(null);

const isServiceModalOpen = ref(false);
const itemToPerformService = ref<FiscalDevice | null>(null);

const { devices, isLoading } = storeToRefs(devicesStore);

const {
  selectedItems,
  itemToEdit,
  isFormOpen,
  isConfirmOpen,
  isDeleting,
  items,
  confirmMessage,
  handleToolbarAction,
  handleFormSave,
  handleDeleteConfirm,
  fetchItems,
} = useResourceView<FiscalDevice>({
  resourceName: 'device',
  items: devices,
  isLoading: isLoading,
  fetchItems: devicesStore.fetchDevices,
  deleteItem: devicesStore.deleteDevice,
  customActions: {
    export_pdf: async (selected) => {
      if (selected.length !== 1) return;
      await handleExportPdf(selected[0]);
    },
    send_email: async (selected) => {
      if (selected.length === 0) return;

      isSendingReminders.value = true;
      try {
        const ids = selected.map(device => device.id);
        const response = await sendInspectionReminders(ids);
        snackbarStore.showSuccess(response.detail || `Zlecono wysłanie ${response.sent_count} przypomnień.`);
        selectedItems.value = [];
      } catch (error: unknown) {
        const message = error instanceof Error ? error.message : 'Wystąpił błąd podczas wysyłania przypomnień.';
        snackbarStore.showError(message);
      } finally {
        isSendingReminders.value = false;
      }
    },
    view_details: (selected) => {
      if (selected.length !== 1) return;
      itemToView.value = selected[0];
      isDetailsDrawerOpen.value = true;
    },
    perform_service: (selected) => {
      if (selected.length !== 1) return;
      itemToPerformService.value = selected[0];
      isServiceModalOpen.value = true;
    },
  },
});

const isClientModalOpen = ref(false);
const newlyCreatedClientId = ref<number | null>(null);

const deviceHeaders = computed(() => getDeviceHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('devices.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
  { id: 'edit', label: t('devices.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'export_pdf', label: t('devices.toolbar.exportPdf'), icon: 'mdi-file-pdf-box', requiresSelection: 'single', loading: isExporting.value },
  { id: 'delete', label: t('devices.toolbar.delete'), icon: 'mdi-delete', color: 'error', requiresSelection: 'multiple' },
  { id: 'send_email', label: 'Wyślij email', icon: 'mdi-email', requiresSelection: 'multiple', loading: isSendingReminders.value },
  { id: 'perform_service', label: 'Wykonaj przegląd', icon: 'mdi-check-decagram', requiresSelection: 'single', loading: isPerformingService.value },
  { id: 'view_details', label: 'Podgląd', icon: 'mdi-eye', requiresSelection: 'single' },
]);

// Export PDF helper
async function handleExportPdf(device: FiscalDevice) {
  isExporting.value = true;
  try {
    await downloadDeviceReport(device.id);
    snackbarStore.showSuccess('Raport PDF został wygenerowany.');
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Wystąpił błąd podczas eksportu.';
    snackbarStore.showError(message);
  } finally {
    isExporting.value = false;
  }
}

// Handlers z Drawera
function handleEditFromDrawer(device: FiscalDevice) {
  isDetailsDrawerOpen.value = false;
  itemToEdit.value = device;
  isFormOpen.value = true;
}

function handlePerformServiceFromDrawer(device: FiscalDevice) {
  isDetailsDrawerOpen.value = false;
  itemToPerformService.value = device;
  isServiceModalOpen.value = true;
}

function handleExportPdfFromDrawer(device: FiscalDevice) {
  handleExportPdf(device);
}

async function handlePerformServiceConfirm(technicianId: number) {
  if (!itemToPerformService.value) return;

  isPerformingService.value = true;
  isServiceModalOpen.value = false;

  try {
    const deviceId = itemToPerformService.value.id;
    const updatedDevice = await performDeviceService(deviceId, technicianId);

    devicesStore.updateDeviceInList(updatedDevice);
    snackbarStore.showSuccess('Przegląd został wykonany.');
    selectedItems.value = [];

    // Aktualizuj też widok w drawerze jeśli otwarty
    if (itemToView.value?.id === deviceId) {
      itemToView.value = updatedDevice;
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : 'Wystąpił błąd podczas aktualizacji.';
    snackbarStore.showError(message);
  } finally {
    isPerformingService.value = false;
    itemToPerformService.value = null;
  }
}

function onClientSaveSuccess(message: string, newClient?: Client) {
  snackbarStore.showSuccess(message);
  if (newClient) {
    newlyCreatedClientId.value = newClient.id;
  }
}

const searchQuery = ref('');

const filteredItems = computed(() => {
  const q = (searchQuery.value || '').toString().trim().toLowerCase();
  const all = items.value || [];

  if (!q) return all;

  return all.filter((d: FiscalDevice) => {
    const unique = (d.unique_number || '').toString().toLowerCase();
    const ownerName = (d.owner?.name || '').toString().toLowerCase();
    const serial = (d.serial_number || '').toString().toLowerCase();
    return unique.includes(q) || ownerName.includes(q) || serial.includes(q);
  });
});

function onClearSearch() {
  searchQuery.value = '';
}

onMounted(() => fetchItems());
</script>
