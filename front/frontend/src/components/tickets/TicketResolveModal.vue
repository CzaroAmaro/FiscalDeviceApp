<!-- components/tickets/TicketResolveModal.vue -->
<template>
  <v-dialog v-model="isDialogOpen" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">Zakończ zgłoszenie: {{ ticket.ticket_number }}</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">
            {{ error }}
          </v-alert>

          <v-container>
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="formData.resolution"
                  :items="resolutionOptions"
                  item-title="title"
                  item-value="value"
                  label="Wynik zgłoszenia"
                  :rules="[v => !!v || 'Wynik jest wymagany.']"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="formData.resolution_notes"
                  label="Notatki z rozwiązania / Opis wykonanych czynności"
                  rows="4"
                  auto-grow
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" text @click="closeDialog">
          Anuluj
        </v-btn>
        <v-btn color="primary" :loading="isSaving" @click="handleFormSubmit">
          Zapisz i zakończ
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue';
import { useTicketsStore } from '@/stores/tickets';
import type { ServiceTicket, TicketResolutionPayload } from '@/types';
import type { VForm } from 'vuetify/components';

const props = defineProps<{
  modelValue: boolean;
  ticket: ServiceTicket;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

const ticketsStore = useTicketsStore();
const formRef = ref<VForm | null>(null);
const isSaving = ref(false);
const error = ref<string | null>(null);

const formData = reactive<TicketResolutionPayload>({
  resolution: '',
  resolution_notes: '',
});

const resolutionOptions = [
  { title: 'Zrealizowane pomyślnie', value: 'completed' },
  { title: 'Niezrealizowane - nie udało się', value: 'failed' },
  { title: 'Anulowane przez klienta', value: 'cancelled' },
];

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  const { valid } = await formRef.value!.validate();
  if (!valid) return;

  isSaving.value = true;
  error.value = null;

  try {
    await ticketsStore.resolveTicket(props.ticket.id, formData);
    emit('save-success', 'Zgłoszenie zostało pomyślnie zakończone.');
    closeDialog();
  } catch (err: any) {
    error.value = err.message || 'Wystąpił błąd podczas zapisywania.';
    console.error('Błąd zamykania zgłoszenia:', err);
  } finally {
    isSaving.value = false;
  }
}
</script>
