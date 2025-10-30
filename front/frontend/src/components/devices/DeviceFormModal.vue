<template>
  <v-dialog v-model="isDialogOpen" max-width="700px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert
            v-if="form.state.error"
            type="error"
            density="compact"
            class="mb-4"
          >
            {{ form.state.error }}
          </v-alert>

          <v-container>
            <v-row>
              <ManufacturerFormModal
                v-model="isManufacturerModalOpen"
                :editing-manufacturer="null"
                @save-success="onManufacturerSaveSuccess"
              />
              <v-col cols="12" sm="6">
                <!-- ZMIANA W v-select DLA 'brand' -->
                <v-select
                  v-model="form.formData.brand"
                  :items="manufacturersStore.manufacturers"
                  item-title="name"
                  item-value="id"
                  :label="t('devices.forms.brandLabel')"
                  :rules="[rules.required]"
                >
                  <template #append-inner>
                    <v-icon
                      icon="mdi-plus-circle-outline"
                      @click.stop="isManufacturerModalOpen = true"
                    />
                  </template>
                </v-select>
              </v-col>

              <v-col cols="12" sm="6">
                <v-combobox
                  v-model="form.formData.model_name"
                  :items="predefinedDeviceModels"
                  :label="t('devices.forms.modelLabel')"
                  :rules="[rules.required]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.unique_number"
                  :label="t('devices.forms.uniqueNumberLabel')"
                  :rules="[rules.required]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.serial_number"
                  :label="t('devices.forms.serialLabel')"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="form.formData.sale_date"
                  :label="t('devices.forms.saleDateLabel')"
                  type="date"
                  :rules="[rules.required]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="form.formData.status"
                  :items="statusOptions"
                  :label="t('devices.forms.statusLabel')"
                />
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="form.formData.owner"
                  :items="clientsStore.clients"
                  item-title="name"
                  item-value="id"
                  :label="t('devices.forms.ownerLabel')"
                  :rules="[rules.required]"
                >
                  <template #append-inner>
                    <v-icon
                      icon="mdi-plus-circle-outline"
                      @click.stop="$emit('request-new-client')"
                    />
                  </template>
                </v-select>
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="form.formData.operating_instructions"
                  :label="t('devices.forms.instructionsLabel')"
                  rows="2"
                />
              </v-col>

              <v-col cols="12">
                <v-textarea
                  v-model="form.formData.remarks"
                  :label="t('devices.forms.remarksLabel')"
                  rows="2"
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
        <v-btn
          color="primary"
          :loading="form.state.isSaving"
          @click="handleFormSubmit"
        >
          {{ t('common.save') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { watch, computed, onMounted, toRefs, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useDevicesStore } from '@/stores/devices';
import { useClientsStore } from '@/stores/clients';
import { useManufacturersStore } from '@/stores/manufacturers';
import { useForm } from '@/composables/useForm';
import { predefinedDeviceModels } from '@/config/deviceModels';
import type { FiscalDevice, DevicePayload, Manufacturer } from '@/types';
import ManufacturerFormModal from '@/components/manufacturers/ManufacturerFormModal.vue';
import { useSnackbarStore } from '@/stores/snackbar';

/* ==========================
   Props & Emits
========================== */
const props = defineProps<{
  modelValue: boolean;
  editingDevice: FiscalDevice | null;
  newlyAddedClientId: number | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
  (e: 'request-new-client'): void;
}>();

/* ==========================
   Stores & composables
========================== */
const { t } = useI18n();
const devicesStore = useDevicesStore();
const clientsStore = useClientsStore();
const manufacturersStore = useManufacturersStore();
const snackbarStore = useSnackbarStore();
const { editingDevice } = toRefs(props);

const isManufacturerModalOpen = ref(false);

/* ==========================
   Formularz
========================== */
const initialFormData: DevicePayload = {
  brand: 0,
  model_name: '',
  unique_number: '',
  serial_number: '',
  sale_date: '',
  last_service_date: null,
  status: 'active',
  operating_instructions: '',
  remarks: '',
  owner: 0,
};

const form = useForm<DevicePayload, FiscalDevice | null, FiscalDevice>(
  initialFormData,
  editingDevice,
  (payload) => devicesStore.addDevice(payload),
  (id, payload) => devicesStore.updateDevice(id, payload)
);

const { formRef, isEditing } = form;

/* ==========================
   Inicjalizacja
========================== */
onMounted(() => {
  clientsStore.fetchClients();
  manufacturersStore.fetchManufacturers();
});

watch(
  () => props.modelValue,
  (isOpen) => {
    if (isOpen) {
      form.resetForm();

      // ustaw właściciela, jeśli dopiero dodany klient
      if (!isEditing.value && props.newlyAddedClientId) {
        form.formData.owner = props.newlyAddedClientId;
      }
    }
  }
);

/* ==========================
   UI helpers
========================== */
const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const formTitle = computed(() =>
  isEditing.value
    ? t('devices.forms.editTitle')
    : t('devices.forms.addTitle')
);

const statusOptions = computed(() => [
  { title: t('devices.forms.statusOptions.active'), value: 'active' },
  { title: t('devices.forms.statusOptions.inactive'), value: 'inactive' },
  { title: t('devices.forms.statusOptions.serviced'), value: 'serviced' },
  {
    title: t('devices.forms.statusOptions.decommissioned'),
    value: 'decommissioned',
  },
]);

const rules = computed(() => ({
  required: (v: unknown) => !!v || t('validation.required'),
}));

/* ==========================
   Akcje
========================== */
function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  try {
    await form.submit();
    const message = isEditing.value
      ? t('devices.forms.editSuccess')
      : t('devices.forms.addSuccess');
    emit('save-success', message);
    closeDialog();
  } catch (error) {
    console.error('Zapis nie powiódł się:', error);
  }
}

function onManufacturerSaveSuccess(message: string, newManufacturer?: Manufacturer) {
  snackbarStore.showSuccess(message);
  // Odśwież listę producentów w tle
  manufacturersStore.fetchManufacturers(true);
  if (newManufacturer) {
    // Ustaw nowo dodanego producenta jako wybranego w formularzu
    form.formData.brand = newManufacturer.id;
  }
}
</script>
