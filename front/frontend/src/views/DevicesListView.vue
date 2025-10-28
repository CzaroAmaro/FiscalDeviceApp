<template>
  <v-container fluid>
    <TableToolbar
      :title="t('devices.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction" />

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="deviceHeaders"
        :items="items"
        :loading="isLoading"
      >
        <template #item.status="{ item }">
          <DeviceStatusChip :status="item.status" />
        </template>
      </DataTable>
    </v-card>

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

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import DeviceFormModal from '@/components/devices/DeviceFormModal.vue';
import DeviceStatusChip from '@/components/devices/DeviceStatusChip.vue';
import ClientFormModal from '@/components/clients/ClientFormModal.vue';

const { t } = useI18n();
const snackbarStore = useSnackbarStore();
const devicesStore = useDevicesStore();

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
});

const isClientModalOpen = ref(false);
const newlyCreatedClientId = ref<number | null>(null);

const deviceHeaders = computed(() => getDeviceHeaders(t));
// Rozwiązanie błędu z typem `ToolbarAction` przez zapewnienie, że każdy obiekt jest w pełni zgodny
const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('devices.toolbar.add'), icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: t('devices.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('devices.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

function onClientSaveSuccess(message: string, newClient?: Client) {
  snackbarStore.showSuccess(message);
  if (newClient) {
    newlyCreatedClientId.value = newClient.id;
    // Opcjonalnie: odśwież listę klientów w tle, jeśli inne komponenty z niej korzystają
    // useClientsStore().fetchClients(true);
  }
}

onMounted(() => fetchItems());
</script>
