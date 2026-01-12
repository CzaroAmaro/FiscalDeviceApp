<template>
  <v-container fluid class="kanban-container pa-4">
    <div class="page-header mb-6">
      <div class="d-flex align-center justify-space-between flex-wrap ga-4">
        <div>
          <h1 class="text-h4 font-weight-bold mb-1">
            {{ t('tickets.title') }}
          </h1>
        </div>

        <div class="d-flex align-center ga-3">
          <div class="d-flex ga-2">
            <v-chip color="warning" variant="tonal" size="small">
              <v-icon start size="14">mdi-alert-circle</v-icon>
              {{ ticketsByStatus['open']?.length || 0 }} otwartych
            </v-chip>
            <v-chip color="info" variant="tonal" size="small">
              <v-icon start size="14">mdi-progress-clock</v-icon>
              {{ ticketsByStatus['in_progress']?.length || 0 }} w toku
            </v-chip>
            <v-chip color="success" variant="tonal" size="small">
              <v-icon start size="14">mdi-check-circle</v-icon>
              {{ ticketsByStatus['closed']?.length || 0 }} zamkniętych
            </v-chip>
          </div>

          <v-btn
            color="primary"
            prepend-icon="mdi-plus"
            @click="handleToolbarAction('add')"
          >
            Nowe zgłoszenie
          </v-btn>
        </div>
      </div>
    </div>

    <div v-if="isLoading && tickets.length === 0" class="loading-state">
      <v-progress-circular indeterminate size="64" color="primary" />
      <p class="text-body-1 text-medium-emphasis mt-4">Ładowanie zgłoszeń...</p>
    </div>

    <div v-else class="kanban-board">
      <KanbanColumn
        v-for="column in columns"
        :key="column.status"
        :title="column.title"
        :status="column.status"
        :icon="column.icon"
        :color="column.color"
        :tickets="ticketsByStatus[column.status] || []"
        :is-loading="isLoading"
        :moving-ticket-id="movingTicketId"
        @ticket-moved="handleTicketMoved"
        @edit="handleEdit"
        @resolve="handleResolve"
        @delete="handleDelete"
        @reopen="handleReopen"
      />
    </div>

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

    <v-dialog v-model="isConfirmOpen" max-width="450" persistent>
      <v-card rounded="lg">
        <v-card-title class="d-flex align-center pa-4">
          <v-avatar color="error" variant="tonal" class="mr-3">
            <v-icon>mdi-delete-alert</v-icon>
          </v-avatar>
          <span>{{ t('common.confirmDelete') }}</span>
        </v-card-title>
        <v-card-text class="pb-2">
          <br>
          <span class="text-medium-emphasis">{{ t('common.confirmDeleteMsg') }}</span>
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn
            variant="text"
            :disabled="isDeleting"
            @click="isConfirmOpen = false"
          >
            {{ t('common.cancel') }}
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            :loading="isDeleting"
            @click="handleDeleteConfirm"
          >
            {{ t('common.delete') }}
          </v-btn>
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
import { useSnackbarStore } from '@/stores/snackbar';
import type { ServiceTicket } from '@/types';

import KanbanColumn from '@/components/tickets/KanbanColumn.vue';
import TicketFormModal from '@/components/tickets/TicketFormModal.vue';
import TicketResolveModal from '@/components/tickets/TicketResolveModal.vue';

const { t } = useI18n();
const ticketsStore = useTicketsStore();
const snackbarStore = useSnackbarStore();
const { tickets, isLoading, movingTicketId } = storeToRefs(ticketsStore);

const isFormOpen = ref(false);
const itemToEdit = ref<ServiceTicket | null>(null);
const isResolveModalOpen = ref(false);
const itemToResolve = ref<ServiceTicket | null>(null);
const isConfirmOpen = ref(false);
const isDeleting = ref(false);
const itemToDelete = ref<ServiceTicket | null>(null);

const confirmMessage = computed(() =>
  itemToDelete.value
    ? `Czy na pewno chcesz usunąć zgłoszenie "${itemToDelete.value.title}"?`
    : ''
);

const columns = ref([
  {
    title: t('tickets.statuses.open'),
    status: 'open' as const,
    icon: 'mdi-alert-circle-outline',
    color: 'warning'
  },
  {
    title: t('tickets.statuses.in_progress'),
    status: 'in_progress' as const,
    icon: 'mdi-progress-clock',
    color: 'info'
  },
  {
    title: t('tickets.statuses.closed'),
    status: 'closed' as const,
    icon: 'mdi-check-circle-outline',
    color: 'success'
  },
]);

const ticketsByStatus = computed(() => {
  return tickets.value.reduce((acc, ticket) => {
    const status = ticket.status as 'open' | 'in_progress' | 'closed';
    (acc[status] = acc[status] || []).push(ticket);
    return acc;
  }, {} as Record<'open' | 'in_progress' | 'closed', ServiceTicket[]>);
});

onMounted(() => {
  ticketsStore.fetchTickets(true);
});

function handleToolbarAction(actionId: string) {
  if (actionId === 'add') {
    itemToEdit.value = null;
    isFormOpen.value = true;
  }
}

async function handleTicketMoved({ ticketId, newStatus, oldStatus }: {
  ticketId: number;
  newStatus: string;
  oldStatus: string;
}) {
  const ticket = tickets.value.find(t => t.id === ticketId);
  if (ticket) {
    ticket.status = newStatus as any;
  }

  try {
    await ticketsStore.updateTicketStatus(ticketId, newStatus as any);
    snackbarStore.showSuccess('Status zgłoszenia został zaktualizowany.');
  } catch {
    if (ticket) {
      ticket.status = oldStatus as any;
    }
    snackbarStore.showError('Błąd podczas zmiany statusu.');
    await ticketsStore.fetchTickets(true);
  }
}

async function handleReopen(ticket: ServiceTicket) {
  try {
    await ticketsStore.updateTicketStatus(ticket.id, 'open');
    snackbarStore.showSuccess('Zgłoszenie zostało ponownie otwarte.');
  } catch {
    snackbarStore.showError('Nie udało się przywrócić zgłoszenia.');
  }
}

function handleEdit(ticket: ServiceTicket) {
  itemToEdit.value = ticket;
  isFormOpen.value = true;
}

function handleResolve(ticket: ServiceTicket) {
  itemToResolve.value = ticket;
  isResolveModalOpen.value = true;
}

function handleDelete(ticket: ServiceTicket) {
  itemToDelete.value = ticket;
  isConfirmOpen.value = true;
}

function handleFormSave(message: string) {
  snackbarStore.showSuccess(message);
}

function handleResolveSuccess(message: string) {
  snackbarStore.showSuccess(message);
  isResolveModalOpen.value = false;
  itemToResolve.value = null;
}

async function handleDeleteConfirm() {
  if (!itemToDelete.value) return;
  isDeleting.value = true;
  try {
    await ticketsStore.deleteTicket(itemToDelete.value.id);
    snackbarStore.showSuccess('Zgłoszenie zostało usunięte.');
    isConfirmOpen.value = false;
    itemToDelete.value = null;
  } catch {
    snackbarStore.showError('Nie udało się usunąć zgłoszenia.');
  } finally {
    isDeleting.value = false;
  }
}
</script>

<style scoped>
.kanban-container {
  max-width: 100%;
}

.page-header {
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.kanban-board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 8px 0 16px;
  min-height: calc(100vh - 220px);
}

.kanban-board::-webkit-scrollbar {
  height: 8px;
}

.kanban-board::-webkit-scrollbar-track {
  background: transparent;
}

.kanban-board::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 4px;
}

@media (max-width: 1200px) {
  .kanban-board {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .kanban-board {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .page-header .d-flex {
    flex-direction: column;
    align-items: flex-start !important;
  }
}
</style>
