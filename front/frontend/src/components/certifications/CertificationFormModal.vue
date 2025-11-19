<template>
  <v-dialog v-model="isDialogOpen" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <v-alert v-if="state.error" type="error" density="compact" class="mb-4">
            {{ state.error }}
          </v-alert>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-select
                  v-model="formData.technician"
                  :items="techniciansStore.technicians"
                  item-title="full_name"
                  item-value="id"
                  label="Serwisant"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="formData.manufacturer"
                  :items="manufacturersStore.manufacturers"
                  item-title="name"
                  item-value="id"
                  label="Producent"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.certificate_number"
                  label="Numer certyfikatu"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <DatePicker
                  v-model="formData.issue_date"
                  label="Data wydania"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <DatePicker
                  v-model="formData.expiry_date"
                  label="Data ważności"
                  :rules="[rules.required]"
                />
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="closeDialog">Anuluj</v-btn>
        <v-btn color="primary" :loading="state.isSaving" @click="handleFormSubmit">Zapisz</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { watch, computed, onMounted, toRefs } from 'vue';
import { useCertificationsStore } from '@/stores/certifications';
import { useTechniciansStore } from '@/stores/technicians';
import { useManufacturersStore } from '@/stores/manufacturers';
import { useForm } from '@/composables/useForm';
import type { Certification, CertificationPayload } from '@/types';
import DatePicker from '@/components/common/DatePicker.vue';

const props = defineProps<{
  modelValue: boolean;
  editingCertification: Certification | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

const certificationsStore = useCertificationsStore();
const techniciansStore = useTechniciansStore();
const manufacturersStore = useManufacturersStore();
const { editingCertification } = toRefs(props);

const initialFormData: CertificationPayload = {
  technician: 0,
  manufacturer: 0,
  certificate_number: '',
  issue_date: '',
  expiry_date: '',
};

const transformItemToFormPayload = (item: Certification): Partial<CertificationPayload> => ({
  technician: item.technician,
  manufacturer: item.manufacturer,
  certificate_number: item.certificate_number,
  issue_date: item.issue_date,
  expiry_date: item.expiry_date,
});

const { formData, formRef, isEditing, state, resetForm, submit } = useForm<CertificationPayload, Certification>(
  initialFormData,
  editingCertification,
  (payload) => certificationsStore.addCertification(payload),
  (id, payload) => certificationsStore.updateCertification(id, payload),
  undefined, // Nie potrzebujemy transformacji payloadu dla API
  transformItemToFormPayload // Potrzebujemy transformacji itemu na formularz
);

onMounted(() => {
  techniciansStore.fetchTechnicians();
  manufacturersStore.fetchManufacturers();
});

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) resetForm();
});

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const formTitle = computed(() => (isEditing.value ? 'Edytuj certyfikat' : 'Dodaj certyfikat'));
const rules = { required: (v: any) => !!v || 'To pole jest wymagane' };

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  try {
    await submit();
    const message = isEditing.value ? 'Certyfikat zaktualizowany.' : 'Certyfikat dodany.';
    emit('save-success', message);
    closeDialog();
    certificationsStore.fetchCertifications(true);
  } catch (error) {
    console.error('Błąd zapisu:', error);
  }
}
</script>
