<template>
  <v-card
    class="mb-3 ticket-card"
    variant="outlined"
    elevation="1"
    :data-ticket-id="ticket.id"
    :class="{ 'is-moving': isMoving }"
  >
    <!-- Nakładka pokazująca ładowanie -->
    <v-overlay
      :model-value="isMoving"
      contained
      scrim="#000000"
      class="align-center justify-center"
    >
      <v-progress-circular indeterminate color="white" />
    </v-overlay>
    <v-card-title class="text-subtitle-2 py-2">
      {{ ticket.title }}
    </v-card-title>
    <v-card-subtitle class="pb-2">
      #{{ ticket.ticket_number }} | {{ ticket.client?.name || 'Brak klienta' }}
    </v-card-subtitle>

    <v-card-text class="py-2">
      <div>
        <v-chip :color="statusColor(ticket.status)" size="small" variant="flat" label>
          {{ statusDisplayText }}
        </v-chip>
        <v-chip v-if="ticket.ticket_type" size="x-small" class="ml-2">
          {{ ticketTypeDisplayText }}
        </v-chip>
      </div>
      <div v-if="ticket.assigned_technician" class="d-flex align-center mt-3">
        <v-avatar size="24" class="mr-2">
          <v-icon>mdi-account-circle</v-icon>
        </v-avatar>
        <span class="text-caption">{{ ticket.assigned_technician?.full_name }}</span>
      </div>
    </v-card-text>

    <v-divider />

    <v-card-actions class="px-3 py-1">
      <v-spacer />

      <v-tooltip v-if="ticket.status === 'closed'" text="Przywróć (otwórz ponownie)" location="top">
        <template #activator="{ props }">
          <v-btn v-bind="props" icon="mdi-undo-variant" size="x-small" variant="text" @click="$emit('reopen', ticket)" />
        </template>
      </v-tooltip>

      <v-tooltip text="Edytuj" location="top">
        <template #activator="{ props }">
          <v-btn v-bind="props" icon="mdi-pencil" size="x-small" variant="text" @click="$emit('edit', ticket)" />
        </template>
      </v-tooltip>
      <v-tooltip text="Zakończ" location="top">
        <template #activator="{ props }">
          <v-btn
            v-if="ticket.status !== 'closed'"
            v-bind="props"
            icon="mdi-check-circle"
            size="x-small"
            color="primary"
            variant="text"
            @click="$emit('resolve', ticket)"
          />
        </template>
      </v-tooltip>
      <v-tooltip text="Usuń" location="top">
        <template #activator="{ props }">
          <v-btn v-bind="props" icon="mdi-delete" size="x-small" color="error" variant="text" @click="$emit('delete', ticket)" />
        </template>
      </v-tooltip>
    </v-card-actions>
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

// Komputed properties dla wyświetlanych tekstów
const statusDisplayText = computed(() => {
  switch (props.ticket.status) {
    case 'open':
      return 'Otwarte';
    case 'in_progress':
      return 'W toku';
    case 'closed':
      return 'Zamknięte';
    default:
      return props.ticket.status_display || 'Nieznany';
  }
});

const ticketTypeDisplayText = computed(() => {
  if (props.ticket.ticket_type_display) {
    return props.ticket.ticket_type_display;
  }

  switch (props.ticket.ticket_type) {
    case 'incident':
      return 'Incydent';
    case 'request':
      return 'Zapytanie';
    case 'problem':
      return 'Problem';
    default:
      return props.ticket.ticket_type || 'Inny';
  }
});
</script>

<style scoped>
.ticket-card {
  cursor: grab;
}
.ticket-card:active {
  cursor: grabbing;
}
.is-moving {
  /* opacity: 0.5; */
}
</style>
