<template>
  <v-dialog :model-value="modelValue" @update:model-value="closeDialog" max-width="700px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="submitForm">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.model_name" :label="t('devices.forms.modelLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.serial_number" :label="t('devices.forms.serialLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.production_date" :label="t('devices.forms.prodDateLabel')" type="date" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-select v-model="formData.status" :items="statusOptions" :label="t('devices.forms.statusLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="formData.owner"
                  :items="clientsStore.clients"
                  item-title="name"
                  item-value="id"
                  :label="t('devices.forms.ownerLabel')"
                  :loading="clientsStore.isLoading"
                  :rules="[rules.required]"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" @click="closeDialog">{{ t('common.cancel') }}</v-btn>
        <v-btn color="primary" @click="submitForm" :loading="isLoading">{{ t('common.save') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useDevicesStore } from '@/stores/devices';
import { useClientsStore } from '@/stores/clients';
import type { FiscalDevice } from '@/types';
import type { VForm } from 'vuetify/components';

const { t } = useI18n();

const props = defineProps<{ modelValue: boolean, editingDevice: FiscalDevice | null }>();
const emit = defineEmits(['update:modelValue', 'save-success']);

const devicesStore = useDevicesStore();
const clientsStore = useClientsStore();

const form = ref<VForm | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

const initialFormData = { model_name: '', serial_number: '', production_date: '', status: 'active', owner: null };
const formData = reactive<any>({ ...initialFormData });

const isEditing = computed(() => !!props.editingDevice);
const formTitle = computed(() => isEditing.value ? t('devices.forms.editTitle') : t('devices.forms.addTitle'));

const statusOptions = computed(() => [
  { title: t('devices.forms.statusOptions.active'), value: 'active' },
  { title: t('devices.forms.statusOptions.inactive'), value: 'inactive' },
  { title: t('devices.forms.statusOptions.serviced'), value: 'serviced' },
  { title: t('devices.forms.statusOptions.decommissioned'), value: 'decommissioned' },
]);

onMounted(() => {
  clientsStore.fetchClients();
});

watch(() => props.modelValue, (isOpen) => {
  if (isOpen && props.editingDevice) {
    formData.model_name = props.editingDevice.model_name;
    formData.serial_number = props.editingDevice.serial_number;
    formData.production_date = props.editingDevice.production_date;
    formData.status = props.editingDevice.status;
    formData.owner = props.editingDevice.owner;
  } else if (isOpen) {
    Object.assign(formData, initialFormData);
  }
});

const rules = computed(() => ({
  required: (v: any) => !!v || t('validation.required'),
}));

const closeDialog = () => emit('update:modelValue', false);

async function submitForm() {
  const { valid } = await form.value!.validate();
  if (!valid) return;

  isLoading.value = true;
  error.value = null;
  try {
    if (isEditing.value) {
      await devicesStore.updateDevice(props.editingDevice!.id, formData);
      emit('save-success', t('devices.forms.editSuccess'));
    } else {
      await devicesStore.addDevice(formData);
      emit('save-success', t('devices.forms.addSuccess'));
    }
    closeDialog();
  } catch (err: any) {
    error.value = err.response?.data?.serial_number?.[0] || t('common.serverError');
  } finally {
    isLoading.value = false;
  }
}
</script>
