<template>
  <v-dialog :model-value="modelValue" max-width="500" persistent @update:model-value="$emit('update:modelValue', $event)">
    <v-card>
      <v-card-title class="text-h5">Wykonaj przegląd</v-card-title>
      <v-card-subtitle v-if="device">
        {{ device.brand.name }} {{ device.model_name }} ({{ device.unique_number }})
      </v-card-subtitle>
      <v-card-text>
        <p class="mb-4">Wybierz serwisanta, który wykonał przegląd. Na liście znajdują się tylko osoby z ważnymi uprawnieniami dla tej marki.</p>

        <v-select
          v-model="selectedTechnicianId"
          :items="eligibleTechnicians"
          item-title="full_name"
          item-value="id"
          label="Serwisant wykonujący przegląd"
          :loading="isLoading"
          :error-messages="error"
          no-data-text="Brak uprawnionych serwisantów"
        />
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text :disabled="isSubmitting" @click="$emit('update:modelValue', false)">Anuluj</v-btn>
        <v-btn color="success" :loading="isSubmitting" :disabled="!selectedTechnicianId" @click="handleSubmit">
          Potwierdź wykonanie
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { getEligibleTechnicians } from '@/api/devices';
import type { FiscalDevice, TechnicianSummary } from '@/types';

const props = defineProps<{
  modelValue: boolean;
  device: FiscalDevice | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'success', technicianId: number): void;
}>();

const isLoading = ref(false);
const isSubmitting = ref(false);
const selectedTechnicianId = ref<number | null>(null);
const eligibleTechnicians = ref<TechnicianSummary[]>([]);
const error = ref<string | null>(null);

async function fetchTechnicians() {
  if (!props.device) return;

  isLoading.value = true;
  error.value = null;
  try {
    eligibleTechnicians.value = await getEligibleTechnicians(props.device.id);
  } catch (err: any) {
    error.value = err.message || 'Błąd podczas pobierania listy serwisantów.';
  } finally {
    isLoading.value = false;
  }
}

function handleSubmit() {
  if (selectedTechnicianId.value) {
    emit('success', selectedTechnicianId.value);
  }
}

// Reset state when modal is closed
watch(() => props.modelValue, (newValue) => {
  if (!newValue) {
    selectedTechnicianId.value = null;
    eligibleTechnicians.value = [];
    error.value = null;
  } else {
    // Fetch data when modal opens
    fetchTechnicians();
  }
});
</script>
