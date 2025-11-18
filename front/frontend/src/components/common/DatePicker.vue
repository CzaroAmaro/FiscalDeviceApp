<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    offset-y
    min-width="auto"
  >
    <template #activator="{ props: menuProps }">
      <v-text-field
        :model-value="modelValue"
        :label="label"
        :rules="rules"
        :clearable="clearable"
        prepend-inner-icon="mdi-calendar"
        readonly
        v-bind="menuProps"
        @click:clear="$emit('update:modelValue', null)"
      />
    </template>
    <v-date-picker
      v-model="dateValue"
      hide-header
      :title="label"
      @update:model-value="menu = false"
    />
  </v-menu>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  modelValue: string | null; // Wartość z v-model (zawsze string YYYY-MM-DD lub null)
  label?: string;
  rules?: any[];
  clearable?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | null): void;
}>();

const menu = ref(false);

/**
 * Formatuje datę do stringa YYYY-MM-DD.
 * To jest wewnętrzna funkcja pomocnicza komponentu.
 */
function formatDateToString(date: Date | string | null | undefined): string | null {
  if (!date) return null;
  try {
    const d = new Date(date);
    if (isNaN(d.getTime())) return null;
    return d.toLocaleDateString('sv-SE'); // Prosty trik na format YYYY-MM-DD
  } catch (e) {
    return null;
  }
}

/**
 * Właściwość computed do obsługi v-model na v-date-picker.
 * v-date-picker pracuje na obiektach Date, a my chcemy przechowywać stringi.
 * Ta właściwość jest "mostem" między tymi dwoma światami.
 */
const dateValue = computed({
  // Getter: konwertuje string z modelu na obiekt Date dla v-date-pickera
  get() {
    return props.modelValue ? new Date(props.modelValue) : null;
  },
  // Setter: pobiera obiekt Date z v-date-pickera, formatuje go i emituje na zewnątrz
  set(val: Date | null) {
    emit('update:modelValue', formatDateToString(val));
  },
});
</script>
