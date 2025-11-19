<template>
  <v-container fluid>
    <TableToolbar
      :title="t('tickets.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction" />

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="ticketHeaders"
        :items="items"
        :loading="isLoading"
      >
        <template #item.status="{ item }">
          <v-chip :color="statusColor(item.status_display)" size="small" variant="flat" label>
            {{ item.status_display }}
          </v-chip>
        </template>
        <template #item.resolution="{ item }">
          <v-chip v-if="item.status === 'closed'" :color="resolutionColor(item.resolution)" size="x-small" label>
            {{ item.resolution_display }}
          </v-chip>
        </template>
      </DataTable>
    </v-card>

    <TicketFormModal
      v-model="isFormOpen"
      :editing-ticket="itemToEdit"
      @save-success="handleFormSave"
    />

    <TicketResolveModal
      v-if="itemToResolve"
      v-model="isResolveModalOpen"
      :ticket="itemToResolve"
      @save-success="handleResolveSuccess"
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
import { useTicketsStore } from '@/stores/tickets';
import { useResourceView } from '@/composables/useResourceView';
import { getTicketHeaders } from '@/config/tables/ticketHeaders';
import type { ServiceTicket } from '@/types';
import TicketResolveModal from '@/components/tickets/TicketResolveModal.vue';
import { useSnackbarStore } from '@/stores/snackbar';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import TicketFormModal from '@/components/tickets/TicketFormModal.vue';

const { t } = useI18n();
const ticketsStore = useTicketsStore();
const { tickets, isLoading } = storeToRefs(ticketsStore);
const isResolveModalOpen = ref(false);
const itemToResolve = ref<ServiceTicket | null>(null);
const snackbarStore = useSnackbarStore();

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
} = useResourceView<ServiceTicket>({
  resourceName: 'ticket',
  items: tickets,
  isLoading: isLoading,
  fetchItems: ticketsStore.fetchTickets,
  deleteItem: ticketsStore.deleteTicket,
  customActions: {
    resolve: (selected) => {
      // Funkcja `resolve` zostanie wywołana przez `handleToolbarAction` z `useResourceView`
      if (selected.length === 1) {
        itemToResolve.value = selected[0];
        isResolveModalOpen.value = true;
      }
    },
  },
});

const ticketHeaders = computed(() => getTicketHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('tickets.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
  { id: 'edit', label: t('tickets.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'resolve', label: 'Zakończ zgłoszenie', icon: 'mdi-check-circle', color: 'primary', requiresSelection: 'single' },
  { id: 'delete', label: t('tickets.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

function handleResolveSuccess(message: string) {
  selectedItems.value = [];
  snackbarStore.showSuccess(message);
  isResolveModalOpen.value = false;
  itemToResolve.value = null;
}

const resolutionColor = (resolution: string) => {
  switch (resolution) {
    case 'completed': return 'success';
    case 'failed': return 'error';
    case 'cancelled': return 'grey';
    default: return 'default';
  }
};

const statusColor = (status: string) => {
  switch (status) {
    case 'open': return 'blue';
    case 'in_progress': return 'orange';
    case 'closed': return 'success';
    default: return 'default';
  }
};

onMounted(() => fetchItems());
</script>
