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
      <v-tooltip :text="action.label" location="bottom">
        <template #activator="{ props }">
          <div v-bind="props" class="d-inline-block mx-1">
            <v-btn
              :icon="action.icon"
              :color="action.color || 'blue'"
              variant="flat"
              class="text-white"
              size="40"
              :loading="action.loading"
              :disabled="isActionDisabled(action)"
              @click="$emit('action', action.id)"
            />
          </div>
        </template>
      </v-tooltip>
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
  variant?: 'flat' | 'text' | 'outlined' | 'elevated' | 'tonal' | 'plain';
  requiresSelection: 'none' | 'single' | 'multiple';
  loading?: boolean;
};

const props = defineProps<{
  title: string;
  selectedCount: number;
  actions: ToolbarAction[];
}>();

defineEmits<{
  (e: 'action', actionId: string): void;
}>();

const hasSelection = computed(() => props.selectedCount > 0);

function isActionDisabled(action: ToolbarAction): boolean {
  if (action.loading) {
    return true;
  }

  switch (action.requiresSelection) {
    case 'none':
      return false;
    case 'single':
      return props.selectedCount !== 1;
    case 'multiple':
      return props.selectedCount === 0;
    default:
      return false;
  }
}
</script>
