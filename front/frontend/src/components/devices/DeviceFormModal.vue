<template>
  <v-dialog :model-value="modelValue" max-width="700px" persistent @update:model-value="closeDialog">
    <v-card>
      <v-card-title><span class="text-h5">{{ formTitle }}</span></v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="submitForm">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">{{ error }}</v-alert>
          <v-container>
            <v-row>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="formData.brand"
                  :items="manufacturersStore.manufacturers"
                  item-title="name"
                  item-value="id"
                  :label="t('devices.forms.brandLabel')"
                  :loading="manufacturersStore.isLoading"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-combobox
                  v-model="formData.model_name"
                  :items="predefinedDeviceModels"
                  :label="t('devices.forms.modelLabel')"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.unique_number" :label="t('devices.forms.uniqueNumberLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.serial_number" :label="t('devices.forms.serialLabel')" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.sale_date" :label="t('devices.forms.saleDateLabel')" type="date" :rules="[rules.required]" />
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
                >
                  <template #append-inner>
                    <v-tooltip :text="t('devices.forms.addNewClientTooltip')">
                      <template #activator="{ props: tooltipProps }">
                        <v-icon
                          v-bind="tooltipProps"
                          icon="mdi-plus-circle-outline"
                          @click.stop="$emit('request-new-client')"
                        ></v-icon>
                      </template>
                    </v-tooltip>
                  </template>
                </v-select>
              </v-col>
              <v-col cols="12"><v-textarea v-model="formData.operating_instructions" :label="t('devices.forms.instructionsLabel')" rows="2" /></v-col>
              <v-col cols="12"><v-textarea v-model="formData.remarks" :label="t('devices.forms.remarksLabel')" rows="2" /></v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" @click="closeDialog">{{ t('common.cancel') }}</v-btn>
        <v-btn color="primary" :loading="isLoading" @click="submitForm">{{ t('common.save') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useDevicesStore, type DevicePayload } from '@/stores/devices';
import { useClientsStore } from '@/stores/clients';
import { useManufacturersStore } from '@/stores/manufacturers';
import type { FiscalDevice } from '@/types';
import type { VForm } from 'vuetify/components';
import { predefinedDeviceModels } from "@/config/deviceModels";

const props = defineProps<{ modelValue: boolean; editingDevice: FiscalDevice | null; newlyAddedClientId: number | null; }>();
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
  (e: 'request-new-client'): void;
}>();

const { t } = useI18n();
const devicesStore = useDevicesStore();
const clientsStore = useClientsStore();
const manufacturersStore = useManufacturersStore();

const form = ref<VForm | null>(null);
const isLoading = ref(false);
const error = ref<string | null>(null);

// Definiujemy typ formularza, który pozwala na `null` dla relacji
type DeviceFormData = Omit<DevicePayload, 'brand' | 'owner'> & { brand: number | null, owner: number | null };

const initialFormData: DeviceFormData = {
  brand: null,
  model_name: '',
  unique_number: '',
  serial_number: '',
  sale_date: '',
  status: 'active',
  operating_instructions: '',
  remarks: '',
  owner: null,
};
const formData = reactive<DeviceFormData>({ ...initialFormData });

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
  manufacturersStore.fetchManufacturers();
});

watch(() => props.modelValue, (isOpen) => {
  error.value = null;
  if (!isOpen) return;

  if (props.editingDevice) {
    Object.assign(formData, { ...props.editingDevice });
  } else {
    Object.assign(formData, initialFormData);
    if (props.newlyAddedClientId) {
      formData.owner = props.newlyAddedClientId;
    }
  }
});

const rules = computed(() => ({
  required: (v: any) => !!v || t('validation.required'),
}));

const closeDialog = () => emit('update:modelValue', false);

async function submitForm() {
  const { valid } = await form.value!.validate();
  if (!valid) return;

  // Sprawdzenie, czy relacje nie są null, zanim wyślemy dane
  if (formData.brand === null || formData.owner === null) {
    error.value = "Marka i właściciel są wymagani."; // TODO: Przenieść do i18n
    return;
  }

  isLoading.value = true;
  error.value = null;

  // Stworzenie payloadu z pewnością, że brand i owner nie są null
  const payload: DevicePayload = { ...formData, brand: formData.brand, owner: formData.owner };

  try {
    if (isEditing.value) {
      await devicesStore.updateDevice(props.editingDevice!.id, payload);
      emit('save-success', t('devices.forms.editSuccess'));
    } else {
      await devicesStore.addDevice(payload);
      emit('save-success', t('devices.forms.addSuccess'));
    }
    closeDialog();
  } catch (err: any) {
    const errorData = err.response?.data;
    if (errorData?.unique_number) {
      error.value = t('devices.forms.errors.uniqueNumber', { value: errorData.unique_number[0] });
    } else { error.value = t('common.serverError'); }
  } finally {
    isLoading.value = false;
  }
}
</script>
