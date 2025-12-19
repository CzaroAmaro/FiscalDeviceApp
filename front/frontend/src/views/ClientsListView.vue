<template>
  <v-container fluid>
    <TableToolbar
      :title="t('clients.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarActionWrapper"
    />

    <!-- Pole wyszukiwania -->
    <div class="mb-4 flex items-center gap-3">
      <v-text-field
        v-model="searchQuery"
        density="compact"
        hide-details
        variant="solo"
        prepend-inner-icon="mdi-magnify"
        label="Szukaj po nazwie lub NIP"
        clearable
        style="max-width: 300px;"
        @click:clear="onClearSearch"
      />
    </div>

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="headers"
        :items="filteredItems"
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
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import { useClientsStore } from '@/stores/clients';
import { useResourceView } from '@/composables/useResourceView'
import { getClientHeaders } from '@/config/tables/clientHeaders'
import type { Client } from '@/types';

import DataTable from "@/components/DataTable.vue";
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import ClientFormModal from '@/components/clients/ClientFormModal.vue';

const { t } = useI18n();
const router = useRouter();
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

const searchQuery = ref('');

const filteredItems = computed(() => {
  const q = (searchQuery.value || '').toString().trim().toLowerCase();
  const all = items.value || [];

  if (!q) return all;

  return all.filter((c: Client) => {
    const name = (c.name || '').toString().toLowerCase();
    const nip = (c.nip || '').toString().toLowerCase();
    return name.includes(q) || nip.includes(q);
  });
});

function onClearSearch() {
  searchQuery.value = '';
}

/* -------------------- Toolbar actions -------------------- */
const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('clients.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
  { id: 'edit', label: t('clients.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('clients.toolbar.delete'), icon: 'mdi-delete', color: 'error', requiresSelection: 'multiple' },
  // Zmienione na 'single' - wymaga zaznaczenia dokładnie jednego klienta
  { id: 'view-map', label: t('clients.toolbar.viewOnMap') || 'Zobacz na mapie', icon: 'mdi-map-marker', color: 'primary', requiresSelection: 'single' },
]);

function handleToolbarActionWrapper(actionId: string) {
  if (actionId === 'view-map') {
    // Teraz wiemy, że jest dokładnie jeden zaznaczony klient
    const selected = selectedItems.value[0];
    if (selected) {
      router.push({
        name: 'client-map',
        query: { clientId: selected.id.toString() }
      });
    }
    return;
  }

  handleToolbarAction(actionId);
}

onMounted(() => fetchItems());
</script>

<style scoped>
.search-field {
  max-width: 480px;
  width: 100%;
}
</style>
