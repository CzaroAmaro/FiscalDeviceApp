<!-- front/frontend/src/components/tickets/TicketFormModal.vue -->
<template>
  <v-dialog v-model="isDialogOpen" max-width="800px" persistent>
    <AiSuggestionModal
      v-model="isAiModalOpen"
      :description="formData.description"
    />
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <!-- Używamy teraz `formRef` bezpośrednio -->
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <!-- Używamy teraz `state.error` bezpośrednio -->
          <v-alert v-if="state.error" type="error" density="compact" class="mb-4">
            {{ state.error }}
          </v-alert>

          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.title"
                  :label="t('tickets.forms.titleLabel')"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="formData.description"
                  :label="t('tickets.forms.descriptionLabel')"
                  rows="3"
                />
                <v-btn
                  size="small"
                  variant="tonal"
                  color="info"
                  prepend-icon="mdi-robot-happy-outline"
                  :disabled="!formData.description"
                  @click="isAiModalOpen = true"
                >
                  Analizuj z AI
                </v-btn>
              </v-col>
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="formData.client"
                  :items="clientsStore.clients"
                  :loading="clientsStore.isLoading"
                  item-title="name"
                  item-value="id"
                  :label="t('tickets.forms.clientLabel')"
                  :rules="[rules.required]"
                  clearable
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="formData.device"
                  :items="devicesForSelectedClient"
                  :loading="devicesStore.isLoading"
                  item-title="displayName"
                  item-value="id"
                  :label="t('tickets.forms.deviceLabel')"
                  :rules="[rules.required]"
                  clearable
                  :disabled="!formData.client"
                >
                  <template #item="{ props, item }">
                    <v-list-item v-bind="props" :title="item.raw.displayName" :subtitle="item.raw.owner.name" />
                  </template>
                </v-autocomplete>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="formData.ticket_type"
                  :items="typeOptions"
                  :label="t('tickets.forms.typeLabel')"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="formData.assigned_technician"
                  :items="techniciansStore.technicians"
                  :loading="techniciansStore.isLoading"
                  item-title="full_name"
                  item-value="id"
                  :label="t('tickets.forms.technicianLabel')"
                  clearable
                />
              </v-col>
              <v-col cols="12" sm="6">
                <DatePicker
                  v-model="formData.scheduled_for"
                  :label="t('tickets.forms.scheduledLabel')"
                  clearable
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" text @click="closeDialog">
          {{ t('common.cancel') }}
        </v-btn>
        <v-btn color="primary" :loading="state.isSaving" @click="handleFormSubmit">
          {{ t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, toRefs, onMounted, watch, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTicketsStore } from '@/stores/tickets';
import { useClientsStore } from '@/stores/clients';
import { useDevicesStore } from '@/stores/devices';
import { useTechniciansStore } from '@/stores/technicians';
import { useForm } from '@/composables/useForm';
import type { ServiceTicket, ServiceTicketPayload } from '@/types';
import DatePicker from '@/components/common/DatePicker.vue'
import AiSuggestionModal from '@/components/ai/AiSuggestionModal.vue'

const props = defineProps<{
  modelValue: boolean;
  editingTicket: ServiceTicket | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

const { t } = useI18n();
const ticketsStore = useTicketsStore();
const clientsStore = useClientsStore();
const devicesStore = useDevicesStore();
const techniciansStore = useTechniciansStore();
const { editingTicket } = toRefs(props);
const isAiModalOpen = ref(false);

// --- ZMIANA #1: DESTRUCTURING ---
const {
  formData,
  state,
  formRef,
  isEditing,
  resetForm,
  submit
} = useForm<ServiceTicketPayload, ServiceTicket | null, ServiceTicket>(
  {
    title: '', description: '', ticket_type: 'service',
    client: null, device: null, assigned_technician: null,
    scheduled_for: null,
  },
  editingTicket,
  (payload) => ticketsStore.addTicket(payload),
  (id, payload) => ticketsStore.updateTicket(id, payload)
);

onMounted(() => {
  clientsStore.fetchClients();
  devicesStore.fetchDevices();
  techniciansStore.fetchTechnicians();
});

// --- ZMIANA #2: Użycie `resetForm` i `formData` bezpośrednio ---
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    resetForm();

    if (isEditing.value && props.editingTicket) {
      formData.client = props.editingTicket.client.id;
      formData.device = props.editingTicket.device; // device jest już ID
      formData.assigned_technician = props.editingTicket.assigned_technician?.id ?? null;
      formData.title = props.editingTicket.title;
      formData.description = props.editingTicket.description;
      formData.ticket_type = props.editingTicket.ticket_type;
      formData.scheduled_for = props.editingTicket.scheduled_for ? props.editingTicket.scheduled_for.slice(0, 10) : null;
    }
  }
});

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const formTitle = computed(() =>
  isEditing.value ? t('tickets.forms.editTitle') : t('tickets.forms.addTitle')
);

// --- ZMIANA #3: Dodanie filtrowania urządzeń dla lepszego UX ---
const devicesForSelectedClient = computed(() => {
  if (!formData.client) {
    return [];
  }
  return devicesStore.devices
    .filter(device => device.owner.id === formData.client)
    .map(device => ({
      ...device,
      displayName: `${device.model_name} (${device.unique_number})`
    }));
});

// --- ZMIANA #4: Automatyczne czyszczenie pola urządzenia po zmianie klienta ---
watch(() => formData.client, (newClientId, oldClientId) => {
  if (newClientId !== oldClientId && !isEditing.value) { // Czyść tylko przy tworzeniu nowego
    formData.device = null;
  }
});

const typeOptions = computed(() => [
  { title: 'Przegląd', value: 'service' },
  { title: 'Odczyt', value: 'reading' },
  { title: 'Naprawa', value: 'repair' },
  { title: 'Inne', value: 'other' }
]);

const rules = computed(() => ({
  required: (v: any) => (v !== null && v !== undefined && v !== '') || t('validation.required'),
}));

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  try {
    // --- ZMIANA #5: Użycie `submit()` bezpośrednio ---
    await submit();
    const message = isEditing.value ? t('tickets.forms.editSuccess') : t('tickets.forms.addSuccess');
    emit('save-success', message);
    closeDialog();
  } catch (error) {
    console.error('Zapis zgłoszenia nie powiódł się:', error);
  }
}
</script>
