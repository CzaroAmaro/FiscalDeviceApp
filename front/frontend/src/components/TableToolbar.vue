<template>
  <v-toolbar flat class="mb-4 rounded">
    <v-toolbar-title v-if="!hasSelection" class="text-h6 font-weight-regular">
      {{ title }}
    </v-toolbar-title>

    <v-toolbar-title v-else class="text-subtitle-1 font-weight-medium">
      Zaznaczono: {{ selectedCount }}
    </v-toolbar-title>

    <v-spacer></v-spacer>

    <template v-for="action in actions" :key="action.id">
      <v-btn
        :color="action.color || 'primary'"
        :variant="action.variant || 'flat'"
        :prepend-icon="action.icon"
        :loading="action.loading"
        :disabled="isActionDisabled(action)"
        class="ms-2"
        @click="$emit('action', action.id)"
      >
        {{ action.label }}
      </v-btn>
    </template>
  </v-toolbar>
</template>

<script setup lang="ts">
import { computed } from 'vue';

export type ToolbarAction = {
  id: string;
  label: string;
  icon: string;
  color?: string;
  variant?: 'flat' | 'text' | 'outlined';
  requiresSelection: 'none' | 'single' | 'multiple';
  loading?: boolean;
};

const props = defineProps<{
  title: string;
  selectedCount: number;
  actions: ToolbarAction[];
}>();

defineEmits(['action']);

const hasSelection = computed(() => props.selectedCount > 0);

function isActionDisabled(action: ToolbarAction): boolean {
  switch (action.requiresSelection) {
    case 'none':
      return props.selectedCount > 0;
    case 'single':
      return props.selectedCount !== 1;
    case 'multiple':
      return props.selectedCount === 0;
    default:
      return false;
  }
}
</script>
