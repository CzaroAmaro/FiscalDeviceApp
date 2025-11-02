<template>
  <v-container fluid>
    <TableToolbar
      :title="t('clients.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="headers"
        :items="items"
        :loading="isLoading"
      />
    </v-card>

    <ClientFormModal
      v-model="isFormOpen"
      :editing-client="itemToEdit"
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
import { useClientsStore } from '@/stores/clients';
import { useResourceView } from '@/composables/useResourceView'
import { getClientHeaders } from '@/config/tables/clientHeaders'
import type { Client } from '@/types';

import DataTable from "@/components/DataTable.vue";
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import ClientFormModal from '@/components/clients/ClientFormModal.vue';

const { t } = useI18n();
const clientsStore = useClientsStore();
const headers = computed(() => getClientHeaders(t));

const { clients, isLoading } = storeToRefs(clientsStore);

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
} = useResourceView<Client>({
  resourceName: 'client',
  items: clients,
  isLoading: isLoading,
  fetchItems: clientsStore.fetchClients,
  deleteItem: clientsStore.deleteClient,
});

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('clients.toolbar.add'), icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: t('clients.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('clients.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

onMounted(() => fetchItems());
</script>
