<template>
  <v-data-table
    v-model="selectedItems"
    :headers="headers"
    :items="items"
    :loading="loading"
    item-value="id"
    show-select
    return-object
    :loading-text="loadingText"
    :no-data-text="noDataText"
    density="compact"
    class="elevation-1"
  >
    <template v-for="(_, slotName) in $slots" v-slot:[slotName]="scope">
      <slot :name="slotName" v-bind="scope" />
    </template>
  </v-data-table>
</template>

<script setup lang="ts" generic="T extends { id: number }">
import { computed } from 'vue';
import type { VDataTable } from 'vuetify/components';

// BARDZIEJ PRECYZYJNY TYP DLA NAGŁÓWKÓW
type ReadonlyHeaders = InstanceType<typeof VDataTable>['headers'];

const props = withDefaults(defineProps<{
  modelValue: T[];
  headers: ReadonlyHeaders; // <-- Naprawiony typ
  items: T[];
  loading: boolean;
  loadingText?: string;
  noDataText?: string;
}>(), {
  loadingText: 'Ładowanie danych...',
  noDataText: 'Nie znaleziono danych',
});

const emit = defineEmits<{
  (e: 'update:modelValue', selectedItems: T[]): void;
}>();

const selectedItems = computed({
  get() {
    return props.modelValue;
  },
  set(value) {
    emit('update:modelValue', value);
  },
});
</script>
