<template>
  <v-dialog v-model="isDialogOpen" max-width="800px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert v-if="form.state.error" type="error" density="compact" class="mb-4">
            {{ form.state.error }}
          </v-alert>

          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="form.formData.title"
                  :label="t('tickets.forms.titleLabel')"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="form.formData.description"
                  :label="t('tickets.forms.descriptionLabel')"
                  rows="3"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="form.formData.client"
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
                  v-model="form.formData.device"
                  :items="devicesStore.devices"
                  :loading="devicesStore.isLoading"
                  item-title="unique_number"
                  item-value="id"
                  :label="t('tickets.forms.deviceLabel')"
                  :rules="[rules.required]"
                  clearable
                >
                  <template #item="{ props, item }">
                    <v-list-item v-bind="props" :title="`${item.raw.model_name} (${item.raw.unique_number})`" :subtitle="item.raw.owner.name" />
                  </template>
                </v-autocomplete>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.formData.ticket_type"
                  :items="typeOptions"
                  :label="t('tickets.forms.typeLabel')"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-autocomplete
                  v-model="form.formData.assigned_technician"
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
                  v-model="form.formData.scheduled_for"
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
        <v-btn color="primary" :loading="form.state.isSaving" @click="handleFormSubmit">
          {{ t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, toRefs, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTicketsStore } from '@/stores/tickets';
import { useClientsStore } from '@/stores/clients';
import { useDevicesStore } from '@/stores/devices';
import { useTechniciansStore } from '@/stores/technicians';
import { useForm } from '@/composables/useForm';
import type { ServiceTicket, ServiceTicketPayload } from '@/types';
import { format, parseISO } from 'date-fns';
import DatePicker from '@/components/common/DatePicker.vue'

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

const form = useForm<ServiceTicketPayload, ServiceTicket | null, ServiceTicket>(
  {
    title: '', description: '', ticket_type: 'service',
    client: null, device: null, assigned_technician: null,
    scheduled_for: null,
  },
  editingTicket,
  (payload) => ticketsStore.addTicket(payload),
  (id, payload) => ticketsStore.updateTicket(id, payload)
);

const { formRef, isEditing } = form;

onMounted(() => {
  clientsStore.fetchClients();
  devicesStore.fetchDevices();
  techniciansStore.fetchTechnicians();
});


watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    form.resetForm();

    if (isEditing.value && props.editingTicket) {
      form.formData.client = props.editingTicket.client.id;
      form.formData.assigned_technician = props.editingTicket.assigned_technician?.id ?? null;

      if (props.editingTicket.scheduled_for) {
        form.formData.scheduled_for = props.editingTicket.scheduled_for.slice(0, 10);
      } else {
        form.formData.scheduled_for = null;
      }
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
    await form.submit();
    const message = isEditing.value ? t('tickets.forms.editSuccess') : t('tickets.forms.addSuccess');
    emit('save-success', message);
    closeDialog();
  } catch (error) {
    console.error('Zapis zgłoszenia nie powiódł się:', error);
  }
}
</script>
