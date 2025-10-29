<template>
  <v-container fluid>
    <TableToolbar
      :title="t('manufacturers.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction" />

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="manufacturerHeaders"
        :items="items"
        :loading="isLoading"
      />
    </v-card>

    <ManufacturerFormModal
      v-model="isFormOpen"
      :editing-manufacturer="itemToEdit"
      @save-success="handleFormSave"
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
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useManufacturersStore } from '@/stores/manufacturers';
import { useResourceView } from '@/composables/useResourceView';
import { getManufacturerHeaders } from '@/config/tables/manufacturerHeaders';
import type { Manufacturer } from '@/types';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import ManufacturerFormModal from '@/components/manufacturers/ManufacturerFormModal.vue';

const { t } = useI18n();
const manufacturersStore = useManufacturersStore();
const { manufacturers, isLoading } = storeToRefs(manufacturersStore);

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
} = useResourceView<Manufacturer>({
  resourceName: 'manufacturer',
  items: manufacturers,
  isLoading: isLoading,
  fetchItems: manufacturersStore.fetchManufacturers,
  deleteItem: manufacturersStore.deleteManufacturer,
});

const manufacturerHeaders = computed(() => getManufacturerHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('manufacturers.toolbar.add'), icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: t('manufacturers.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('manufacturers.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

onMounted(() => fetchItems());
</script>
