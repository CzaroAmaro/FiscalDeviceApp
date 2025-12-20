<template>
  <div class="kanban-column">
    <v-card class="column-card" rounded="lg" elevation="0">
      <div class="column-header" :class="`border-${color}`">
        <div class="d-flex align-center">
          <v-avatar :color="color" size="32" variant="tonal" class="mr-3">
            <v-icon size="18">{{ icon }}</v-icon>
          </v-avatar>
          <div>
            <h3 class="text-subtitle-1 font-weight-bold mb-0">{{ title }}</h3>
          </div>
        </div>
        <v-chip
          :color="color"
          variant="flat"
          size="small"
          class="font-weight-bold"
        >
          {{ filteredTickets.length }}
        </v-chip>
      </div>

      <div class="column-content">
        <draggable
          :list="filteredTickets"
          class="drag-area"
          group="tickets"
          item-key="id"
          :data-status="status"
          :disabled="status === 'closed'"
          :move="checkMove"
          ghost-class="ghost-card"
          chosen-class="chosen-card"
          drag-class="drag-card"
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

        <div v-if="!isLoading && filteredTickets.length === 0" class="empty-column">
          <v-icon :color="color" size="48" class="mb-3 opacity-50">
            {{ icon }}
          </v-icon>
          <p class="text-body-2 text-medium-emphasis mb-0">
            Brak zgłoszeń
          </p>
          <p v-if="status !== 'closed'" class="text-caption text-disabled">
            Przeciągnij tutaj zgłoszenie
          </p>
        </div>

        <div v-if="isLoading && filteredTickets.length === 0" class="d-flex justify-center my-8">
          <v-progress-circular indeterminate :color="color" size="32" />
        </div>
      </div>

      <div v-if="filteredTickets.length > 3" class="column-footer">
        <span class="text-caption text-medium-emphasis">
          {{ filteredTickets.length }} {{ filteredTickets.length === 1 ? 'zgłoszenie' : 'zgłoszeń' }}
        </span>
      </div>
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
  icon: string;
  color: string;
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

const filteredTickets = computed(() => {
  return props.tickets.filter(ticket => ticket.status === props.status);
});

function checkMove(evt: any) {
  if (evt.from === evt.to) return false;
  return true;
}

function onDragEnd(event: DraggableEndEvent) {
  if (event.from === event.to) return;

  const ticketId = Number(event.item.querySelector('[data-ticket-id]')?.getAttribute('data-ticket-id'));
  const newStatus = event.to.dataset.status;
  const oldStatus = event.from.dataset.status;

  if (ticketId && newStatus && oldStatus) {
    emit('ticket-moved', { ticketId, newStatus, oldStatus });
  }
}
</script>

<style scoped>
.kanban-column {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.column-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(var(--v-theme-on-surface), 0.02);
  border: 1px solid rgba(var(--v-border-color), 0.08);
  overflow: hidden;
}

.column-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: rgb(var(--v-theme-surface));
  border-bottom: 3px solid;
}

.border-warning { border-bottom-color: rgb(var(--v-theme-warning)); }
.border-info { border-bottom-color: rgb(var(--v-theme-info)); }
.border-success { border-bottom-color: rgb(var(--v-theme-success)); }

.column-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  min-height: 200px;
}

.drag-area {
  min-height: 100%;
}

.ticket-wrapper {
  margin-bottom: 12px;
}

.ticket-wrapper:last-child {
  margin-bottom: 0;
}

.empty-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.column-footer {
  padding: 12px 16px;
  background: rgb(var(--v-theme-surface));
  border-top: 1px solid rgba(var(--v-border-color), 0.08);
  text-align: center;
}

.ghost-card {
  opacity: 0.4;
  background: rgba(var(--v-theme-primary), 0.1);
  border: 2px dashed rgb(var(--v-theme-primary));
  border-radius: 12px;
}

.chosen-card {
  opacity: 0.9;
}

.drag-card {
  transform: rotate(3deg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.column-content::-webkit-scrollbar {
  width: 6px;
}

.column-content::-webkit-scrollbar-track {
  background: transparent;
}

.column-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.15);
  border-radius: 3px;
}

.column-content::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.25);
}
</style>
