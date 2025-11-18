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
          <v-chip
            :color="statusColor(item.status)"
            size="small"
            variant="flat"
            label
          >
            {{ item.status }}
          </v-chip>
        </template>
      </DataTable>
    </v-card>

    <TicketFormModal
      v-model="isFormOpen"
      :editing-ticket="itemToEdit"
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
import { useTicketsStore } from '@/stores/tickets';
import { useResourceView } from '@/composables/useResourceView';
import { getTicketHeaders } from '@/config/tables/ticketHeaders';
import type { ServiceTicket } from '@/types';

import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import TicketFormModal from '@/components/tickets/TicketFormModal.vue';

const { t } = useI18n();
const ticketsStore = useTicketsStore();
const { tickets, isLoading } = storeToRefs(ticketsStore);

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
});

const ticketHeaders = computed(() => getTicketHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('tickets.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
  { id: 'edit', label: t('tickets.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('tickets.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

const statusColor = (status: string) => {
  switch (status) {
    case 'Nowe': return 'blue';
    case 'W toku': return 'orange';
    case 'Zakończone': return 'success';
    case 'Anulowane': return 'grey';
    case 'Oczekujące na klienta': return 'purple';
    default: return 'default';
  }
};

onMounted(() => fetchItems());
</script>
