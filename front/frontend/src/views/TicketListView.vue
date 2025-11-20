<template>
  <v-container fluid>
    <TableToolbar
      :title="t('tickets.title')"
      :selected-count="0"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <div v-if="isLoading && tickets.length === 0" class="d-flex justify-center mt-16">
      <v-progress-circular indeterminate size="64" color="primary" />
    </div>

    <div v-else class="kanban-board">
      <KanbanColumn
        v-for="column in columns"
        :key="column.status"
        :title="column.title"
        :status="column.status"
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

    <!-- Modale pozostają bez zmian i będą działać poprawnie -->
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
import { useSnackbarStore } from '@/stores/snackbar';
import type { ServiceTicket } from '@/types';

import KanbanColumn from '@/components/tickets/KanbanColumn.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import TicketFormModal from '@/components/tickets/TicketFormModal.vue';
import TicketResolveModal from '@/components/tickets/TicketResolveModal.vue';

const { t } = useI18n();
const ticketsStore = useTicketsStore();
const snackbarStore = useSnackbarStore();
const { tickets, isLoading, movingTicketId } = storeToRefs(ticketsStore);

// --- Stan widoku dla modali ---
const isFormOpen = ref(false);
const itemToEdit = ref<ServiceTicket | null>(null);

const isResolveModalOpen = ref(false);
const itemToResolve = ref<ServiceTicket | null>(null);

const isConfirmOpen = ref(false);
const isDeleting = ref(false);
const itemToDelete = ref<ServiceTicket | null>(null);
const confirmMessage = computed(() => itemToDelete.value ? `Czy na pewno chcesz usunąć zgłoszenie "${itemToDelete.value.title}"?` : '');

// --- Definicja kolumn Kanban ---
const columns = ref([
  { title: t('tickets.statuses.open'), status: 'open' as const },
  { title: t('tickets.statuses.in_progress'), status: 'in_progress' as const },
  { title: t('tickets.statuses.closed'), status: 'closed' as const },
]);

// --- Logika Danych ---
onMounted(() => {
  ticketsStore.fetchTickets(true); // Wymuś odświeżenie danych przy wejściu na widok
});

const ticketsByStatus = computed(() => {
  return tickets.value.reduce((acc, ticket) => {
    const status = ticket.status as 'open' | 'in_progress' | 'closed';
    (acc[status] = acc[status] || []).push(ticket);
    return acc;
  }, {} as Record<'open' | 'in_progress' | 'closed', ServiceTicket[]>);
});

// --- Obsługa Paska Narzędzi (Toolbar) ---
const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('tickets.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
]);

function handleToolbarAction(actionId: string) {
  if (actionId === 'add') {
    itemToEdit.value = null;
    isFormOpen.value = true;
  }
}

// --- Obsługa Zdarzeń z Kanban ---
async function handleTicketMoved({ ticketId, newStatus, oldStatus }: {
  ticketId: number;
  newStatus: string;
  oldStatus: string;
}) {
  // OPTYMISTYCZNA AKTUALIZACJA: Natychmiast aktualizujemy UI
  const ticket = tickets.value.find(t => t.id === ticketId);
  if (ticket) {
    // Tymczasowo zmieniamy status dla natychmiastowej reakcji UI
    ticket.status = newStatus as any;
  }

  try {
    await ticketsStore.updateTicketStatus(ticketId, newStatus as any);
    snackbarStore.showSuccess('Status zgłoszenia został zaktualizowany.');
  } catch {
    // COFNIĘCIE W RAZIE BŁĘDU: Przywracamy poprzedni status
    if (ticket) {
      ticket.status = oldStatus as any;
    }
    snackbarStore.showError('Błąd podczas zmiany statusu. Odświeżam dane...');
    // Wymuszamy odświeżenie danych
    await ticketsStore.fetchTickets(true);
  }
}

async function handleReopen(ticket: ServiceTicket) {
  try {
    // Przywracamy zgłoszenie do statusu 'open'
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

// --- Obsługa Zdarzeń z Modali ---
function handleFormSave(message: string) {
  snackbarStore.showSuccess(message);
  // Nie trzeba odświeżać, bo store już się zaktualizował
}

function handleResolveSuccess(message: string) {
  snackbarStore.showSuccess(message);
  isResolveModalOpen.value = false;
  itemToResolve.value = null;
  // Nie trzeba odświeżać, bo store już się zaktualizował
}

async function handleDeleteConfirm() {
  if (!itemToDelete.value) return;
  isDeleting.value = true;
  try {
    await ticketsStore.deleteTicket(itemToDelete.value.id);
    snackbarStore.showSuccess('Zgłoszenie zostało usunięte.');
    isConfirmOpen.value = false;
    itemToDelete.value = null;
  } catch (error) {
    snackbarStore.showError('Nie udało się usunąć zgłoszenia.');
  } finally {
    isDeleting.value = false;
  }
}
</script>

<style scoped>
.kanban-board {
  display: flex;
  overflow-x: auto;
  padding: 8px 0;
}
</style>
