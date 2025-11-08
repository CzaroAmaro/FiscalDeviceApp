<template>
  <v-dialog v-model="isDialogOpen" max-width="600px" persistent>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>

      <v-card-text>
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <!-- POPRAWKA: Usunięto v-html -->
          <v-alert v-if="state.error" type="error" density="compact" class="mb-4">
            {{ state.error }}
          </v-alert>

          <v-container class="pa-0">
            <v-row>
              <!-- POPRAWKA: Użycie funkcji 't' do tłumaczeń -->
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.first_name" :label="t('technicians.forms.firstName')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.last_name" :label="t('technicians.forms.lastName')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.email" :label="t('technicians.forms.email')" type="email" :rules="[rules.required, rules.email]" />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="formData.phone_number" :label="t('technicians.forms.phoneLabel')" />
              </v-col>

              <v-divider class="my-4" />

              <v-col cols="12" sm="6">
                <v-select v-model="formData.role" :items="roleOptions" :label="t('technicians.forms.roleLabel')" :rules="[rules.required]" />
              </v-col>
              <v-col cols="12" sm="6" class="d-flex align-center">
                <v-switch v-model="formData.is_active" :label="t('technicians.forms.activeLabel')" color="primary" inset hide-details />
              </v-col>

              <template v-if="!isEditing">
                <v-divider class="my-4" />
                <v-col cols="12">
                  <v-switch v-model="formData.create_user_account" :label="t('technicians.forms.createUserAccountLabel')" color="primary" inset hide-details />
                </v-col>
                <v-expand-transition>
                  <v-col v-if="formData.create_user_account" cols="12">
                    <v-row>
                      <v-col cols="12" sm="6">
                        <v-text-field v-model="formData.username" :label="t('technicians.forms.username')" :rules="formData.create_user_account ? [rules.required] : []" />
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-text-field v-model="formData.password" :label="t('technicians.forms.password')" type="password" :rules="formData.create_user_account ? [rules.required] : []" />
                      </v-col>
                    </v-row>
                  </v-col>
                </v-expand-transition>
              </template>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn color="grey-darken-1" text @click="closeDialog">{{ t('common.cancel') }}</v-btn>
        <v-btn color="primary" :loading="state.isSaving" @click="handleFormSubmit">{{ t('common.save') }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>template>

<script setup lang="ts">
import { computed, toRefs, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useTechniciansStore } from '@/stores/technicians';
import { useForm } from '@/composables/useForm';
import type { Technician, TechnicianPayload } from '@/types';

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

// POPRAWKA: Prawidłowa dekonstrukcja i użycie
const {
  formData,
  formRef,
  isEditing,
  state,
  resetForm,
  submit
} = useForm<TechnicianPayload, Technician, Technician>(
  {
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    role: 'technician',
    is_active: true,
    create_user_account: true,
    username: '',
    password: '',
  },
  editingTechnician,
  (payload) => techniciansStore.addTechnician(payload),
  (id, payload) => techniciansStore.updateTechnician(id, payload)
);

// POPRAWKA: 'watch' używa teraz 'resetForm' w obu przypadkach, ale z różnym skutkiem
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    // Funkcja resetForm z useForm sama wie, czy jest w trybie edycji,
    // i odpowiednio ustawi dane z 'editingItem' lub 'initialData'.
    resetForm();

    // Dodatkowo, jeśli edytujemy, ręcznie ustawiamy dane, których nie ma w `editingItem`
    // To jest potrzebne, bo `resetForm` kopiuje z `editingItem`, który nie ma `first_name` etc. na najwyższym poziomie
    if (isEditing.value && props.editingTechnician) {
      formData.first_name = props.editingTechnician.first_name;
      formData.last_name = props.editingTechnician.last_name;
      formData.email = props.editingTechnician.email;
      formData.phone_number = props.editingTechnician.phone_number;
      formData.role = props.editingTechnician.role;
      formData.is_active = props.editingTechnician.is_active;
    }
  }
});


const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const roleOptions = computed(() => [
  { title: t('technicians.roles.admin'), value: 'admin' },
  { title: t('technicians.roles.technician'), value: 'technician' },
]);

const formTitle = computed(() =>
  isEditing.value ? t('technicians.forms.editTitle') : t('technicians.forms.addTitle')
);

const rules = {
  required: (v: string | number) => !!v || t('validation.required'),
  email: (v: string) => /.+@.+\..+/.test(v) || t('validation.email'),
};

function closeDialog() { isDialogOpen.value = false; }

async function handleFormSubmit() {
  try {
    // POPRAWKA: Modyfikujemy formData przed wywołaniem submit, jeśli trzeba
    if (!formData.create_user_account) {
      // Usuwamy pola, aby nie wysyłać ich do API
      delete formData.username;
      delete formData.password;
    }

    // Wywołujemy submit bez argumentów
    await submit();

    const message = isEditing.value
      ? t('technicians.messages.updateSuccess')
      : t('technicians.messages.addSuccess');
    emit('save-success', message);
    closeDialog();
  } catch (error) {
    console.error('Zapis serwisanta nie powiódł się:', error);
  }
}
</script>
