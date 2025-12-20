<template>
  <v-container fluid>
    <TableToolbar
      :title="t('technicians.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <div class="mb-4 flex items-center gap-3">
      <v-text-field
        v-model="searchQuery"
        density="compact"
        hide-details
        variant="solo"
        prepend-inner-icon="mdi-magnify"
        :label="t('technicians.search.placeholder')"
        clearable
        style="max-width: 360px;"
        @click:clear="onClearSearch"
      />
    </div>

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="technicianHeaders"
        :items="filteredItems"
        :loading="isLoading"
        :items-per-page="25"
      >
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

    <TechnicianDetailsDrawer
      v-model="isDetailsDrawerOpen"
      :technician="itemToView"
      @edit="handleEditFromDrawer"
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
import { useTechniciansStore } from '@/stores/technicians';
import { useResourceView } from '@/composables/useResourceView';
import { getTechnicianHeaders } from '@/config/tables/technicianHeaders';
import type { Technician } from '@/types';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import TechnicianFormModal from '@/components/technicians/TechnicianFormModal.vue';
import TechnicianDetailsDrawer from '@/components/technicians/TechnicianDetailsDrawer.vue';

const { t } = useI18n();
const techniciansStore = useTechniciansStore();
const { technicians, isLoading } = storeToRefs(techniciansStore);

const isDetailsDrawerOpen = ref(false);
const itemToView = ref<Technician | null>(null);

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
  customActions: {
    view_details: (selected) => {
      if (selected.length !== 1) return;
      itemToView.value = selected[0];
      isDetailsDrawerOpen.value = true;
    },
  },
});

const technicianHeaders = computed(() => getTechnicianHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('technicians.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
  { id: 'edit', label: t('technicians.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'view_details', label: t('technicians.toolbar.viewDetails'), icon: 'mdi-eye', requiresSelection: 'single' },
  { id: 'delete', label: t('technicians.toolbar.delete'), icon: 'mdi-delete', color: 'error', requiresSelection: 'multiple' },
]);

const searchQuery = ref('');

const filteredItems = computed(() => {
  const q = (searchQuery.value || '').toString().trim().toLowerCase();
  const all = items.value || [];
  if (!q) return all;

  return all.filter((tech: Technician) => {
    const first = (tech.first_name || '').toString().toLowerCase();
    const last = (tech.last_name || '').toString().toLowerCase();
    const full = (tech.full_name ? tech.full_name : `${first} ${last}`).toString().toLowerCase();
    return first.includes(q) || last.includes(q) || full.includes(q);
  });
});

function onClearSearch() {
  searchQuery.value = '';
}

function handleEditFromDrawer(technician: Technician) {
  isDetailsDrawerOpen.value = false;
  itemToEdit.value = technician;
  isFormOpen.value = true;
}

onMounted(() => fetchItems());
</script>
