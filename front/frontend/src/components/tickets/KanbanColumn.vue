<template>
  <div class="kanban-column">
    <v-card class="column-wrapper" color="grey-lighten-4">
      <v-card-title class="text-subtitle-1 font-weight-bold py-2 px-3 bg-grey-lighten-3">
        {{ title }}
        <v-chip size="small" class="ml-2" variant="tonal">{{ filteredTickets.length }}</v-chip>
      </v-card-title>

      <v-card-text class="pa-2 column-content">
        <draggable
          :list="filteredTickets"
          class="drag-area"
          group="tickets"
          item-key="id"
          :data-status="status"
          :disabled="status === 'closed'"
          :move="checkMove"
          @end="onDragEnd"
        >
          <template #item="{ element: ticket }">
            <div :key="ticket.id" class="ticket-wrapper">
              <KanbanCard
                :ticket="ticket"
                :is-moving="ticket.id === movingTicketId"
                @edit="$emit('edit', ticket)"
                @resolve="$emit('resolve', ticket)"
                @delete="$emit('delete', ticket)"
                @reopen="$emit('reopen', ticket)"
              />
            </div>
          </template>
        </draggable>
        <div v-if="isLoading && filteredTickets.length === 0" class="d-flex justify-center my-4">
          <v-progress-circular indeterminate color="primary" />
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup lang="ts">
import draggable from 'vuedraggable';
import type { ServiceTicket } from '@/types';
import KanbanCard from './KanbanCard.vue';
import { computed } from 'vue';

type DraggableEndEvent = {
  to: HTMLElement;
  from: HTMLElement;
  item: HTMLElement;
  newIndex: number;
  oldIndex: number;
};

const props = defineProps<{
  title: string;
  status: 'open' | 'in_progress' | 'closed';
  tickets: ServiceTicket[];
  isLoading: boolean;
  movingTicketId: number | null;
}>();

const emit = defineEmits<{
  (e: 'ticket-moved', payload: { ticketId: number; newStatus: string; oldStatus: string }): void;
  (e: 'edit', ticket: ServiceTicket): void;
  (e: 'resolve', ticket: ServiceTicket): void;
  (e: 'delete', ticket: ServiceTicket): void;
  (e: 'reopen', ticket: ServiceTicket): void;
}>();

// Filtrujemy bilety dla danej kolumny
const filteredTickets = computed(() => {
  return props.tickets.filter(ticket => ticket.status === props.status);
});

// Sprawdzamy czy przeniesienie jest dozwolone
function checkMove(evt: any) {

  // Blokuj przenoszenie do tej samej kolumny
  if (evt.from === evt.to) {
    return false;
  }

  // Dodatkowe reguły biznesowe można dodać tutaj
  return true;
}

function onDragEnd(event: DraggableEndEvent) {
  // Ignorujemy jeśli nie zmieniono kolumny
  if (event.from === event.to) {
    return;
  }

  // Pobieramy dane z atrybutów data-*
  const ticketId = Number(event.item.querySelector('[data-ticket-id]')?.getAttribute('data-ticket-id'));
  const newStatus = event.to.dataset.status;
  const oldStatus = event.from.dataset.status;

  if (ticketId && newStatus && oldStatus) {
    // Emitujemy zdarzenie z oboma statusami
    emit('ticket-moved', {
      ticketId,
      newStatus,
      oldStatus
    });
  }
}
</script>

<style scoped>
/* Style bez zmian */
.kanban-column {
  flex: 1 1 320px;
  min-width: 320px;
  max-width: 400px;
  margin: 0 8px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 150px);
}
.column-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.column-content {
  flex: 1;
  overflow-y: auto;
}
.drag-area {
  min-height: 100px;
  height: 100%;
}
.ticket-wrapper {
  margin-bottom: 8px;
}
</style>
