<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="650px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="technician-form-card" rounded="lg">
      <!-- Nagłówek -->
      <div class="form-header">
        <div class="d-flex align-center">
          <v-avatar
            :color="isEditing ? 'primary' : 'success'"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">
              {{ isEditing ? 'mdi-account-edit' : 'mdi-account-plus' }}
            </v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ formTitle }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ isEditing ? t('technicians.forms.editSubtitle') : t('technicians.forms.addSubtitle') }}
            </p>
          </div>
        </div>
        <v-btn
          icon
          variant="text"
          size="small"
          @click="closeDialog"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>

      <v-divider />

      <!-- Formularz -->
      <v-card-text class="form-content">
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
          <!-- Alert błędu -->
          <v-alert
            v-if="state.error"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-6"
            closable
            @click:close="state.error = ''"
          >
            <template #prepend>
              <v-icon>mdi-alert-circle</v-icon>
            </template>
            {{ state.error }}
          </v-alert>

          <!-- Sekcja: Dane osobowe -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-account-details</v-icon>
              {{ t('technicians.sections.personalData') }}
            </h3>

            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.first_name"
                  :label="t('technicians.forms.firstName')"
                  :placeholder="t('technicians.placeholders.firstName')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-account</v-icon>
                  </template>
                </v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.last_name"
                  :label="t('technicians.forms.lastName')"
                  :placeholder="t('technicians.placeholders.lastName')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-account-outline</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Dane kontaktowe -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-card-account-phone</v-icon>
              {{ t('technicians.sections.contactData') }}
            </h3>

            <v-row dense>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.email"
                  :label="t('technicians.forms.email')"
                  :placeholder="t('technicians.placeholders.email')"
                  type="email"
                  :rules="[rules.required, rules.email]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-email</v-icon>
                  </template>
                </v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="formData.phone_number"
                  :label="t('technicians.forms.phoneLabel')"
                  :placeholder="t('technicians.placeholders.phone')"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-phone</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <!-- Sekcja: Rola i status -->
          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-shield-account</v-icon>
              {{ t('technicians.sections.roleAndStatus') }}
            </h3>

            <v-row dense>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="formData.role"
                  :items="roleOptions"
                  :label="t('technicians.forms.roleLabel')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-badge-account</v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar
                          :color="item.raw.value === 'admin' ? 'error' : 'primary'"
                          size="32"
                          variant="tonal"
                        >
                          <v-icon size="16">
                            {{ item.raw.value === 'admin' ? 'mdi-shield-crown' : 'mdi-wrench' }}
                          </v-icon>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <div class="d-flex align-center">
                      <v-avatar
                        :color="item.raw.value === 'admin' ? 'error' : 'primary'"
                        size="24"
                        variant="tonal"
                        class="mr-2"
                      >
                        <v-icon size="12">
                          {{ item.raw.value === 'admin' ? 'mdi-shield-crown' : 'mdi-wrench' }}
                        </v-icon>
                      </v-avatar>
                      {{ item.title }}
                    </div>
                  </template>
                </v-select>
              </v-col>
              <v-col cols="12" sm="6" class="d-flex align-center">
                <v-card
                  variant="outlined"
                  class="status-card pa-3 w-100"
                  :class="{ 'status-active': formData.is_active }"
                >
                  <div class="d-flex align-center justify-space-between">
                    <div class="d-flex align-center">
                      <v-avatar
                        :color="formData.is_active ? 'success' : 'grey'"
                        size="32"
                        variant="tonal"
                        class="mr-3"
                      >
                        <v-icon size="16">
                          {{ formData.is_active ? 'mdi-check-circle' : 'mdi-cancel' }}
                        </v-icon>
                      </v-avatar>
                      <div>
                        <span class="text-body-2 font-weight-medium">
                          {{ t('technicians.forms.activeLabel') }}
                        </span>
                        <p class="text-caption text-medium-emphasis mb-0">
                          {{ formData.is_active ? t('technicians.status.activeHint') : t('technicians.status.inactiveHint') }}
                        </p>
                      </div>
                    </div>
                    <v-switch
                      v-model="formData.is_active"
                      color="success"
                      hide-details
                      density="compact"
                    />
                  </div>
                </v-card>
              </v-col>
            </v-row>

            <!-- Alert dla administratora -->
            <v-alert
              v-if="formData.role === 'admin'"
              type="warning"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              <template #prepend>
                <v-icon>mdi-shield-alert</v-icon>
              </template>
              {{ t('technicians.warnings.adminRole') }}
            </v-alert>
          </div>

          <!-- Sekcja: Konto użytkownika (tylko przy dodawaniu) -->
          <template v-if="!isEditing">
            <v-divider class="my-6" />

            <div class="form-section">
              <h3 class="section-title">
                <v-icon start size="18" color="primary">mdi-account-key</v-icon>
                {{ t('technicians.sections.userAccount') }}
              </h3>

              <v-card
                variant="outlined"
                class="account-card pa-4"
                :class="{ 'account-active': formData.create_user_account }"
              >
                <div class="d-flex align-center justify-space-between mb-3">
                  <div class="d-flex align-center">
                    <v-avatar
                      :color="formData.create_user_account ? 'primary' : 'grey'"
                      size="40"
                      variant="tonal"
                      class="mr-3"
                    >
                      <v-icon size="20">
                        {{ formData.create_user_account ? 'mdi-account-check' : 'mdi-account-off' }}
                      </v-icon>
                    </v-avatar>
                    <div>
                      <span class="text-body-1 font-weight-medium">
                        {{ t('technicians.forms.createUserAccountLabel') }}
                      </span>
                      <p class="text-caption text-medium-emphasis mb-0">
                        {{ t('technicians.forms.createUserAccountHint') }}
                      </p>
                    </div>
                  </div>
                  <v-switch
                    v-model="formData.create_user_account"
                    color="primary"
                    hide-details
                    density="compact"
                  />
                </div>

                <v-expand-transition>
                  <div v-if="formData.create_user_account">
                    <v-divider class="mb-4" />
                    <v-row dense>
                      <v-col cols="12" sm="6">
                        <v-text-field
                          v-model="formData.username"
                          :label="t('technicians.forms.username')"
                          :placeholder="t('technicians.placeholders.username')"
                          :rules="formData.create_user_account ? [rules.required] : []"
                          variant="outlined"
                          density="comfortable"
                        >
                          <template #prepend-inner>
                            <v-icon color="primary" size="20">mdi-account-circle</v-icon>
                          </template>
                        </v-text-field>
                      </v-col>
                      <v-col cols="12" sm="6">
                        <v-text-field
                          v-model="formData.password"
                          :label="t('technicians.forms.password')"
                          :placeholder="t('technicians.placeholders.password')"
                          :type="showPassword ? 'text' : 'password'"
                          :rules="formData.create_user_account ? [rules.required, rules.minLength] : []"
                          variant="outlined"
                          density="comfortable"
                        >
                          <template #prepend-inner>
                            <v-icon color="primary" size="20">mdi-lock</v-icon>
                          </template>
                          <template #append-inner>
                            <v-icon
                              size="20"
                              style="cursor: pointer;"
                              @click="showPassword = !showPassword"
                            >
                              {{ showPassword ? 'mdi-eye-off' : 'mdi-eye' }}
                            </v-icon>
                          </template>
                        </v-text-field>
                      </v-col>
                    </v-row>

                    <!-- Podpowiedź dotycząca hasła -->
                    <v-alert
                      type="info"
                      variant="tonal"
                      density="compact"
                      class="mt-2"
                    >
                      <template #prepend>
                        <v-icon size="18">mdi-information</v-icon>
                      </template>
                      <span class="text-caption">
                        {{ t('technicians.hints.passwordRequirements') }}
                      </span>
                    </v-alert>
                  </div>
                </v-expand-transition>
              </v-card>
            </div>
          </template>
        </v-form>
      </v-card-text>

      <v-divider />

      <!-- Stopka -->
      <v-card-actions class="form-footer">
        <v-btn
          variant="text"
          @click="closeDialog"
        >
          {{ t('common.cancel') }}
        </v-btn>
        <v-spacer />
        <v-btn
          v-if="!isEditing"
          variant="tonal"
          color="grey"
          @click="handleResetForm"
        >
          <v-icon start>mdi-refresh</v-icon>
          {{ t('common.clear') }}
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :loading="state.isSaving"
          @click="handleFormSubmit"
        >
          <v-icon start>{{ isEditing ? 'mdi-content-save' : 'mdi-account-plus' }}</v-icon>
          {{ isEditing ? t('common.save') : t('technicians.actions.add') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useTechniciansStore } from '@/stores/technicians';
import type { Technician, TechnicianPayload } from '@/types';

// Props & Emits
const props = defineProps<{
  modelValue: boolean;
  editingTechnician: Technician | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string): void;
}>();

// Composables
const { t } = useI18n();
const techniciansStore = useTechniciansStore();
const display = useDisplay();

// Responsive
const isMobile = computed(() => display.smAndDown.value);

// Form ref
const formRef = ref<{ validate: () => Promise<{ valid: boolean }>; reset: () => void } | null>(null);

// State
const state = ref({
  isSaving: false,
  error: '',
});

const showPassword = ref(false);

// Initial form data
const getInitialFormData = (): TechnicianPayload => ({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  role: 'technician',
  is_active: true,
  create_user_account: true,
  username: '',
  password: '',
});

// Form data
const formData = ref<TechnicianPayload>(getInitialFormData());

// Computed
const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isEditing = computed(() => props.editingTechnician !== null);

const formTitle = computed(() =>
  isEditing.value ? t('technicians.forms.editTitle') : t('technicians.forms.addTitle')
);

const roleOptions = computed(() => [
  { title: t('technicians.roles.admin'), value: 'admin' },
  { title: t('technicians.roles.technician'), value: 'technician' },
]);

// Validation rules
const rules = {
  required: (v: string | number | null | undefined) => {
    if (typeof v === 'number') return v !== 0 || t('validation.required');
    return !!v || t('validation.required');
  },
  email: (v: string) => {
    if (!v) return true;
    return /.+@.+\..+/.test(v) || t('validation.email');
  },
  minLength: (v: string) => {
    if (!v) return true;
    return v.length >= 8 || t('validation.minLength', { min: 8 });
  },
};

// Methods
function populateFormFromTechnician(technician: Technician) {
  formData.value = {
    first_name: technician.first_name,
    last_name: technician.last_name,
    email: technician.email,
    phone_number: technician.phone_number,
    role: technician.role,
    is_active: technician.is_active,
    create_user_account: false,
    username: '',
    password: '',
  };
}

function handleResetForm() {
  formData.value = getInitialFormData();
  state.value.error = '';
  showPassword.value = false;
}

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  // Walidacja formularza
  const validation = await formRef.value?.validate();
  if (!validation?.valid) {
    return;
  }

  state.value.isSaving = true;
  state.value.error = '';

  try {
    // Przygotowanie payload
    const payload: TechnicianPayload = { ...formData.value };

    // Usuwamy pola konta użytkownika jeśli nie tworzymy konta
    if (!payload.create_user_account) {
      delete payload.username;
      delete payload.password;
      delete payload.create_user_account;
    }

    if (isEditing.value && props.editingTechnician) {
      await techniciansStore.updateTechnician(props.editingTechnician.id, payload);
    } else {
      await techniciansStore.addTechnician(payload);
    }

    const message = isEditing.value
      ? t('technicians.messages.updateSuccess')
      : t('technicians.messages.addSuccess');

    emit('save-success', message);
    closeDialog();
    techniciansStore.fetchTechnicians(true);
  } catch (error) {
    console.error('Błąd zapisu serwisanta:', error);
    state.value.error = error instanceof Error ? error.message : t('common.errors.unknown');
  } finally {
    state.value.isSaving = false;
  }
}

// Watchers
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.editingTechnician) {
      populateFormFromTechnician(props.editingTechnician);
    } else {
      handleResetForm();
    }
  }
});

watch(() => props.editingTechnician, (newTechnician) => {
  if (newTechnician && props.modelValue) {
    populateFormFromTechnician(newTechnician);
  }
}, { immediate: true });

// Auto-generate username from email
watch(() => formData.value.email, (newEmail) => {
  if (!isEditing.value && formData.value.create_user_account && newEmail) {
    // Sugeruj username na podstawie emaila
    const suggestedUsername = newEmail.split('@')[0];
    if (!formData.value.username) {
      formData.value.username = suggestedUsername;
    }
  }
});
</script>

<style scoped>
.technician-form-card {
  overflow: hidden;
}

/* Header */
.form-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.08) 0%,
    rgba(var(--v-theme-primary), 0.02) 100%
  );
}

/* Content */
.form-content {
  padding: 24px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

/* Section */
.form-section {
  margin-bottom: 8px;
}

.section-title {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(var(--v-theme-on-surface), 0.7);
  margin-bottom: 16px;
}

/* Footer */
.form-footer {
  padding: 16px 24px;
  background: rgb(var(--v-theme-surface));
}

/* Status card */
.status-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-card.status-active {
  border-color: rgb(var(--v-theme-success));
  background: rgba(var(--v-theme-success), 0.04);
}

/* Account card */
.account-card {
  border-radius: 12px;
  transition: all 0.3s ease;
}

.account-card.account-active {
  border-color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.04);
}

/* Form fields */
:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}

/* Scrollbar */
.form-content::-webkit-scrollbar {
  width: 6px;
}

.form-content::-webkit-scrollbar-track {
  background: transparent;
}

.form-content::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 3px;
}

.form-content::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.3);
}

/* Mobile */
@media (max-width: 600px) {
  .form-header {
    padding: 16px;
  }

  .form-content {
    padding: 16px;
    max-height: calc(100vh - 200px);
  }

  .form-footer {
    padding: 12px 16px;
    flex-wrap: wrap;
    gap: 8px;
  }

  .form-footer .v-btn {
    flex: 1;
    min-width: 120px;
  }

  .status-card,
  .account-card {
    padding: 12px !important;
  }
}

/* Animations */
.v-expand-transition-enter-active,
.v-expand-transition-leave-active {
  transition: all 0.3s ease;
}
</style>
