<template>
  <v-container fluid>
    <TableToolbar
      :title="t('technicians.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction" />

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="technicianHeaders"
        :items="items"
        :loading="isLoading"
      >
        <!-- Logika StatusChip zaimplementowana bezpośrednio tutaj -->
        <template #item.is_active="{ item }">
          <v-chip
            :color="item.is_active ? 'success' : 'grey'"
            :prepend-icon="item.is_active ? 'mdi-check-circle' : 'mdi-close-circle'"
            size="small"
            variant="flat"
          >
            {{ item.is_active ? t('common.active') : t('common.inactive') }}
          </v-chip>
        </template>
      </DataTable>
    </v-card>

    <TechnicianFormModal
      v-model="isFormOpen"
      :editing-technician="itemToEdit"
      @save-success="handleFormSave"
    />

    <!-- Dialog potwierdzenia usunięcia bez zmian -->
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
import { useTechniciansStore } from '@/stores/technicians';
import { useResourceView } from '@/composables/useResourceView';
import { getTechnicianHeaders } from '@/config/tables/technicianHeaders';
import type { Technician } from '@/types';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import TechnicianFormModal from '@/components/technicians/TechnicianFormModal.vue';
// Import StatusChip.vue został usunięty

const { t } = useI18n();
const techniciansStore = useTechniciansStore();
const { technicians, isLoading } = storeToRefs(techniciansStore);

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
} = useResourceView<Technician>({
  resourceName: 'technician',
  items: technicians,
  isLoading: isLoading,
  fetchItems: techniciansStore.fetchTechnicians,
  deleteItem: techniciansStore.deleteTechnician,
});

const technicianHeaders = computed(() => getTechnicianHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('technicians.toolbar.add'), icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: t('technicians.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('technicians.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

onMounted(() => fetchItems());
</script>
