<template>
  <v-dialog :model-value="modelValue" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <v-icon start>mdi-robot-happy-outline</v-icon>
        Asystent AI - Sugestie
      </v-card-title>
      <v-divider />

      <v-card-text style="min-height: 250px;">
        <!-- Stan ładowania -->
        <div v-if="isLoading" class="d-flex flex-column align-center justify-center fill-height">
          <v-progress-circular indeterminate size="64" color="primary" />
          <p class="mt-4 text-grey">Analizowanie problemu, proszę czekać...</p>
          <p class="text-caption text-grey">(może to potrwać kilka sekund)</p>
        </div>

        <!-- Stan błędu -->
        <v-alert v-else-if="error" type="error" border="start" variant="tonal" prominent>
          <template #title><h4>Błąd Analizy</h4></template>
          {{ error }}
        </v-alert>

        <!-- Stan sukcesu -->
        <div v-else-if="suggestions">
          <p class="mb-4">
            <strong>Możliwa przyczyna:</strong><br/>
            <span>{{ suggestions.possible_cause }}</span>
          </p>
          <p>
            <strong>Sugerowana kategoria:</strong>
            <v-chip size="small" color="secondary">{{ suggestions.suggested_category }}</v-chip>
          </p>
          <strong>Sugerowane kroki diagnostyczne:</strong>
          <ul class="ml-5 mt-2">
            <li v-for="(step, i) in suggestions.diagnostic_steps" :key="i">{{ step }}</li>
          </ul>
        </div>
      </v-card-text>

      <v-divider />
      <v-card-actions>
        <v-spacer />
        <v-btn text="Zamknij" color="primary" @click="$emit('update:modelValue', false)" />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import api from '@/api';

// Definicja typów dla propsów i sugestii
interface AiSuggestions {
  possible_cause: string;
  suggested_category: string;
  diagnostic_steps: string[];
}

const props = defineProps<{
  modelValue: boolean; // Kontroluje widoczność modala
  description: string; // Opis problemu do analizy
}>();

defineEmits(['update:modelValue']);

// Stan wewnętrzny komponentu
const isLoading = ref(false);
const error = ref<string | null>(null);
const suggestions = ref<AiSuggestions | null>(null);

// Funkcja do wywołania API
async function fetchAiSuggestions() {
  if (!props.description || props.description.trim().length < 10) {
    error.value = "Opis problemu jest zbyt krótki. Opisz go bardziej szczegółowo.";
    return;
  }

  isLoading.value = true;
  error.value = null;
  suggestions.value = null;

  try {
    const response = await api.post<AiSuggestions>('/ai/get-suggestion/', {
      description: props.description,
    });
    suggestions.value = response.data;
  } catch (err: any) {
    error.value = err.response?.data?.error || err.response?.data?.detail || "Wystąpił nieoczekiwany błąd. Sprawdź konsolę przeglądarki.";
    console.error("AI suggestion error:", err.response);
  } finally {
    isLoading.value = false;
  }
}

// Uruchamia analizę, gdy tylko modal staje się widoczny
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    fetchAiSuggestions();
  }
});
</script>
