<template>
  <v-card
    class="kanban-card"
    :class="{ 'is-moving': isMoving, 'is-closed': ticket.status === 'closed' }"
    :data-ticket-id="ticket.id"
    rounded="lg"
    elevation="1"
  >
    <v-overlay
      :model-value="isMoving"
      contained
      scrim="rgba(0,0,0,0.3)"
      class="align-center justify-center"
    >
      <v-progress-circular indeterminate color="white" size="32" />
    </v-overlay>

    <div class="card-top-bar" :class="`bg-${priorityColor}`"></div>

    <div class="card-content pa-3">
      <div class="d-flex align-start justify-space-between mb-2">
        <div class="flex-grow-1 mr-2">
          <h4 class="card-title text-subtitle-2 font-weight-bold mb-1">
            {{ ticket.title }}
          </h4>
          <div class="d-flex align-center ga-2 flex-wrap">
            <span class="text-caption text-medium-emphasis">
              #{{ ticket.ticket_number }}
            </span>
            <v-chip
              v-if="ticket.ticket_type"
              size="x-small"
              variant="tonal"
              :color="typeColor"
            >
              {{ ticketTypeDisplayText }}
            </v-chip>
          </div>
        </div>
      </div>

      <div class="client-info mb-3">
        <v-icon size="14" class="mr-1 text-medium-emphasis">mdi-domain</v-icon>
        <span class="text-body-2">
          {{ ticket.client?.name || 'Brak klienta' }}
        </span>
      </div>

      <div v-if="ticket.assigned_technician" class="technician-info mb-3">
        <v-avatar size="24" :color="avatarColor" class="mr-2">
          <span class="text-caption font-weight-bold white--text">
            {{ getInitials(ticket.assigned_technician.full_name) }}
          </span>
        </v-avatar>
        <span class="text-body-2">{{ ticket.assigned_technician.full_name }}</span>
      </div>

      <div class="card-footer d-flex align-center justify-space-between">
        <div class="d-flex align-center ga-2">
          <v-chip
            :color="statusColor(ticket.status)"
            size="x-small"
            variant="flat"
            label
          >
            <v-icon start size="10">{{ statusIcon }}</v-icon>
            {{ statusDisplayText }}
          </v-chip>
        </div>

        <div class="card-actions">
          <v-btn
            v-if="ticket.status === 'closed'"
            icon
            size="x-small"
            variant="text"
            color="warning"
            @click.stop="$emit('reopen', ticket)"
          >
            <v-icon size="16">mdi-undo-variant</v-icon>
            <v-tooltip activator="parent" location="top">Przywróć</v-tooltip>
          </v-btn>

          <v-btn
            icon
            size="x-small"
            variant="text"
            @click.stop="$emit('edit', ticket)"
          >
            <v-icon size="16">mdi-pencil-outline</v-icon>
            <v-tooltip activator="parent" location="top">Edytuj</v-tooltip>
          </v-btn>

          <v-btn
            v-if="ticket.status !== 'closed'"
            icon
            size="x-small"
            variant="text"
            color="success"
            @click.stop="$emit('resolve', ticket)"
          >
            <v-icon size="16">mdi-check-circle-outline</v-icon>
            <v-tooltip activator="parent" location="top">Zakończ</v-tooltip>
          </v-btn>

          <v-btn
            icon
            size="x-small"
            variant="text"
            color="error"
            @click.stop="$emit('delete', ticket)"
          >
            <v-icon size="16">mdi-delete-outline</v-icon>
            <v-tooltip activator="parent" location="top">Usuń</v-tooltip>
          </v-btn>
        </div>
      </div>
    </div>
  </v-card>
</template>

<script setup lang="ts">
import type { ServiceTicket } from '@/types';
import { statusColor } from '@/utils/colors';
import { computed } from 'vue';

const props = defineProps<{
  ticket: ServiceTicket;
  isMoving: boolean;
}>();

defineEmits<{
  (e: 'edit', ticket: ServiceTicket): void;
  (e: 'resolve', ticket: ServiceTicket): void;
  (e: 'delete', ticket: ServiceTicket): void;
  (e: 'reopen', ticket: ServiceTicket): void;
}>();

const statusDisplayText = computed(() => {
  switch (props.ticket.status) {
    case 'open': return 'Otwarte';
    case 'in_progress': return 'W toku';
    case 'closed': return 'Zamknięte';
    default: return props.ticket.status_display || 'Nieznany';
  }
});

const statusIcon = computed(() => {
  switch (props.ticket.status) {
    case 'open': return 'mdi-alert-circle';
    case 'in_progress': return 'mdi-progress-clock';
    case 'closed': return 'mdi-check-circle';
    default: return 'mdi-help-circle';
  }
});

const ticketTypeDisplayText = computed(() => {
  if (props.ticket.ticket_type_display) return props.ticket.ticket_type_display;
  switch (props.ticket.ticket_type) {
    case 'incident': return 'Incydent';
    case 'request': return 'Zapytanie';
    case 'problem': return 'Problem';
    default: return props.ticket.ticket_type || 'Inny';
  }
});

const typeColor = computed(() => {
  switch (props.ticket.ticket_type) {
    case 'incident': return 'error';
    case 'request': return 'info';
    case 'problem': return 'warning';
    default: return 'grey';
  }
});

const priorityColor = computed(() => {
  switch (props.ticket.ticket_type) {
    case 'incident': return 'error';
    case 'problem': return 'warning';
    default: return 'primary';
  }
});

const avatarColors = ['primary', 'secondary', 'success', 'info', 'warning'];
const avatarColor = computed(() => {
  const id = props.ticket.assigned_technician?.id || 0;
  return avatarColors[id % avatarColors.length];
});

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
};
</script>

<style scoped>
.kanban-card {
  cursor: grab;
  transition: all 0.2s ease;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), 0.08);
}

.kanban-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.kanban-card:active {
  cursor: grabbing;
}

.kanban-card.is-moving {
  opacity: 0.7;
}

.kanban-card.is-closed {
  opacity: 0.7;
}

.kanban-card.is-closed:hover {
  opacity: 1;
}

.card-top-bar {
  height: 4px;
  width: 100%;
}

.card-title {
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.client-info,
.technician-info {
  display: flex;
  align-items: center;
}

.card-footer {
  padding-top: 8px;
  border-top: 1px solid rgba(var(--v-border-color), 0.08);
}

.card-actions {
  display: flex;
  gap: 2px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.kanban-card:hover .card-actions {
  opacity: 1;
}

@media (hover: none) {
  .card-actions {
    opacity: 1;
  }
}
</style>
