<template>
  <v-container fluid>
    <TableToolbar
      :title="t('devices.title')"
      :selected-count="selectedDevices.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <v-card>
      <DataTable
        v-model="selectedDevices"
        :headers="deviceHeaders"
        :items="devicesStore.devices"
        :loading="devicesStore.isLoading"
        :loading-text="t('common.loadingData')"
        :no-data-text="t('common.noDataFound')"
      >
        <template #item.status="{ item }">
          <DeviceStatusChip :status="item.status" />
        </template>
      </DataTable>
    </v-card>

    <DeviceFormModal
      v-model="isFormModalOpen"
      :editing-device="deviceToEdit"
      @save-success="onSaveSuccess"
    />

    <v-dialog v-model="isConfirmOpen" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5">{{ t('common.confirmDelete') }}</v-card-title>
        <v-card-text>
          <span v-if="selectedDevices.length === 1">
            {{ t('devices.deleteConfirm', { name: selectedDevices[0].model_name, serial: selectedDevices[0].serial_number }) }}
          </span>
          <span v-else>
            {{ t('devices.deleteConfirmMulti', { count: selectedDevices.length }) }}
          </span>
          <br>{{ t('common.confirmDeleteMsg') }}
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="isConfirmOpen = false" :disabled="isDeleting">{{ t('common.cancel') }}</v-btn>
          <v-btn color="error" @click="handleDeleteConfirm" :loading="isDeleting">{{ t('common.delete') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useDevicesStore } from '@/stores/devices';
import type { FiscalDevice } from '@/types';
import { deviceHeaders } from '@/config/tables/deviceHeaders';
import { useI18n } from 'vue-i18n';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';

import DeviceFormModal from '@/components/devices/DeviceFormModal.vue';
import DeviceStatusChip from '@/components/devices/DeviceStatusChip.vue';

const devicesStore = useDevicesStore();
const { t } = useI18n();

const selectedDevices = ref<FiscalDevice[]>([]);
const isFormModalOpen = ref(false);
const deviceToEdit = ref<FiscalDevice | null>(null);
const isConfirmOpen = ref(false);
const isDeleting = ref(false);
const snackbar = reactive({ show: false, text: '', color: 'success' });

onMounted(() => {
  devicesStore.fetchDevices();
});

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('devices.toolbar.add'), icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: t('devices.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('devices.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

function handleToolbarAction(actionId: string) {
  switch (actionId) {
    case 'add':
      deviceToEdit.value = null;
      isFormModalOpen.value = true;
      break;
    case 'edit':
      if (selectedDevices.value.length === 1) {
        deviceToEdit.value = selectedDevices.value[0];
        isFormModalOpen.value = true;
      }
      break;
    case 'delete':
      isConfirmOpen.value = true;
      break;
  }
}

function onSaveSuccess(message: string) {
  selectedDevices.value = [];
  showSnackbar(message);
}

watch(isFormModalOpen, (isOpen) => {
  if (!isOpen) {
    deviceToEdit.value = null;
  }
});

async function handleDeleteConfirm() {
  isDeleting.value = true;
  try {
    const deletePromises = selectedDevices.value.map(device => devicesStore.deleteDevice(device.id));
    await Promise.all(deletePromises);

    const message = selectedDevices.value.length === 1
      ? t('devices.deleteSuccessSingle', { name: selectedDevices.value[0].model_name })
      : t('devices.deleteSuccessMulti', { count: selectedDevices.value.length });

    showSnackbar(message, 'info');
    selectedDevices.value = [];
  } catch {
    showSnackbar(t('devices.deleteError'), 'error');
  } finally {
    isDeleting.value = false;
    isConfirmOpen.value = false;
  }
}

function showSnackbar(text: string, color = 'success') {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
}
</script>
