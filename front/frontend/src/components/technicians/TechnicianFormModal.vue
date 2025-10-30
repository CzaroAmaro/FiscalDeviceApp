<template>
  <v-dialog v-model="isDialogOpen" max-width="600px" persistent>
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
              <!-- ZASTĘPUJEMY v-select prostym polem tekstowym na ID -->
              <v-col cols="12">
                <v-text-field
                  v-model.number="form.formData.user"
                  :label="t('technicians.forms.userIdLabel')"
                  type="number"
                  :rules="[rules.required, rules.isNumber]"
                  :disabled="isEditing"
                />
              </v-col>
              <v-col cols="12" sm="8">
                <v-text-field
                  v-model="form.formData.phone_number"
                  :label="t('technicians.forms.phoneLabel')"
                  :rules="[rules.required]"
                />
              </v-col>
              <v-col cols="12" sm="4">
                <v-switch
                  v-model="form.formData.is_active"
                  :label="t('technicians.forms.activeLabel')"
                  color="primary"
                  inset
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
import { computed, toRefs } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTechniciansStore } from '@/stores/technicians';
import { useForm } from '@/composables/useForm';
import type { Technician } from '@/types';

// Typ Payload jest teraz prostszy
type TechnicianPayload = {
  user: number | undefined;
  phone_number: string;
  is_active: boolean;
};

const props = defineProps<{
  modelValue: boolean;
  editingTechnician: Technician | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

const { t } = useI18n();
const techniciansStore = useTechniciansStore();
const { editingTechnician } = toRefs(props);

// `useForm` jest teraz prostszy, bo nie ma zależności od useUsersStore
const form = useForm<TechnicianPayload, Technician | null, Technician>(
  { user: undefined, phone_number: '', is_active: true },
  editingTechnician,
  // Zapewniamy, że 'user' nie jest undefined przed wysłaniem
  (payload) => techniciansStore.addTechnician(payload as { user: number; phone_number: string; is_active: boolean; }),
  (id, payload) => techniciansStore.updateTechnician(id, payload as { user: number; phone_number: string; is_active: boolean; })
);

const { formRef, isEditing } = form;

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const formTitle = computed(() =>
  isEditing.value
    ? t('technicians.forms.editTitle')
    : t('technicians.forms.addTitle')
);

// Dodajemy prostą walidację dla pola liczbowego
const rules = computed(() => ({
  required: (v: any) => !!v || t('validation.required'),
  isNumber: (v: number) => !isNaN(v) || t('validation.isNumber'),
}));

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  try {
    await form.submit();
    const message = isEditing.value
      ? t('technicians.forms.editSuccess')
      : t('technicians.forms.addSuccess');
    emit('save-success', message);
    closeDialog();
  } catch (error) {
    console.error('Zapis serwisanta nie powiódł się:', error);
  }
}
</script>
