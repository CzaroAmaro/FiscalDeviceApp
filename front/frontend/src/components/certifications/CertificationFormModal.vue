<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="600px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="certification-form-card" rounded="lg">
      <div class="form-header">
        <div class="d-flex align-center">
          <v-avatar
            :color="isEditing ? 'primary' : 'success'"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">
              {{ isEditing ? 'mdi-pencil' : 'mdi-certificate' }}
            </v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ formTitle }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ isEditing ? t('certifications.forms.editSubtitle') : t('certifications.forms.addSubtitle') }}
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

      <v-card-text class="form-content">
        <v-form ref="formRef" @submit.prevent="handleFormSubmit">
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

          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-account-link</v-icon>
              {{ t('certifications.sections.assignment') }}
            </h3>

            <v-row dense>
              <v-col cols="12">
                <v-select
                  v-model="formData.technician"
                  :items="techniciansStore.technicians"
                  item-title="full_name"
                  item-value="id"
                  :label="t('certifications.forms.technicianLabel')"
                  :placeholder="t('certifications.placeholders.technician')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                  :loading="techniciansStore.isLoading"
                  :disabled="isEditing"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-account</v-icon>
                  </template>
                  <template #item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar color="primary" size="32" variant="tonal">
                          <span class="text-caption font-weight-bold">
                            {{ getInitials(item.raw.full_name) }}
                          </span>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                  <template #selection="{ item }">
                    <div class="d-flex align-center">
                      <v-avatar color="primary" size="24" variant="tonal" class="mr-2">
                        <span class="text-caption font-weight-bold" style="font-size: 10px;">
                          {{ getInitials(item.raw.full_name) }}
                        </span>
                      </v-avatar>
                      {{ item.raw.full_name }}
                    </div>
                  </template>
                </v-select>
              </v-col>

              <v-col cols="12">
                <v-select
                  v-model="formData.manufacturer"
                  :items="manufacturersStore.manufacturers"
                  item-title="name"
                  item-value="id"
                  :label="t('certifications.forms.manufacturerLabel')"
                  :placeholder="t('certifications.placeholders.manufacturer')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                  :loading="manufacturersStore.isLoading"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-factory</v-icon>
                  </template>
                  <template #item="{ props: itemProps }">
                    <v-list-item v-bind="itemProps">
                      <template #prepend>
                        <v-avatar color="secondary" size="32" variant="tonal">
                          <v-icon size="16">mdi-certificate</v-icon>
                        </v-avatar>
                      </template>
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-card-account-details</v-icon>
              {{ t('certifications.sections.certificateData') }}
            </h3>

            <v-row dense>
              <v-col cols="12">
                <v-text-field
                  v-model="formData.certificate_number"
                  :label="t('certifications.forms.certificateNumberLabel')"
                  :placeholder="t('certifications.placeholders.certificateNumber')"
                  :rules="[rules.required]"
                  variant="outlined"
                  density="comfortable"
                >
                  <template #prepend-inner>
                    <v-icon color="primary" size="20">mdi-identifier</v-icon>
                  </template>
                </v-text-field>
              </v-col>
            </v-row>
          </div>

          <v-divider class="my-6" />

          <div class="form-section">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-calendar-range</v-icon>
              {{ t('certifications.sections.validity') }}
            </h3>

            <v-row dense>
              <v-col cols="12" sm="6">
                <DatePicker
                  v-model="formData.issue_date"
                  :label="t('certifications.forms.issueDateLabel')"
                  :rules="[rules.required]"
                  prepend-inner-icon="mdi-calendar-start"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <DatePicker
                  v-model="formData.expiry_date"
                  :label="t('certifications.forms.expiryDateLabel')"
                  :rules="[rules.required, rules.afterIssueDate]"
                  prepend-inner-icon="mdi-calendar-end"
                  :min="formData.issue_date || undefined"
                />
              </v-col>
            </v-row>

            <v-alert
              v-if="validityInfo"
              :type="validityInfo.type"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              <template #prepend>
                <v-icon>{{ validityInfo.icon }}</v-icon>
              </template>
              {{ validityInfo.text }}
            </v-alert>

            <div v-if="formData.issue_date" class="mt-4">
              <span class="text-caption text-medium-emphasis d-block mb-2">
                {{ t('certifications.quickValidityLabel') }}
              </span>
              <div class="d-flex flex-wrap ga-2">
                <v-chip
                  v-for="period in validityPeriods"
                  :key="period.months"
                  size="small"
                  :color="isSelectedPeriod(period.months) ? 'primary' : undefined"
                  :variant="isSelectedPeriod(period.months) ? 'flat' : 'outlined'"
                  @click="setValidityPeriod(period.months)"
                >
                  {{ period.label }}
                </v-chip>
              </div>
            </div>
          </div>
        </v-form>
      </v-card-text>

      <v-divider />

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
          @click="resetForm"
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
          <v-icon start>{{ isEditing ? 'mdi-content-save' : 'mdi-plus' }}</v-icon>
          {{ isEditing ? t('common.save') : t('certifications.actions.add') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useDisplay } from 'vuetify';
import { useCertificationsStore, ApiValidationError } from '@/stores/certifications';
import { useTechniciansStore } from '@/stores/technicians';
import { useManufacturersStore } from '@/stores/manufacturers';
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

const fieldErrors = ref<Record<string, string>>({});

const { t } = useI18n();
const certificationsStore = useCertificationsStore();
const techniciansStore = useTechniciansStore();
const manufacturersStore = useManufacturersStore();

const display = useDisplay();
const isMobile = computed(() => display.smAndDown.value);

const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);

const state = ref({
  isSaving: false,
  error: '',
});

const getInitialFormData = (): CertificationPayload => ({
  technician: 0,
  manufacturer: 0,
  certificate_number: '',
  issue_date: '',
  expiry_date: '',
});

const formData = ref<CertificationPayload>(getInitialFormData());

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isEditing = computed(() => props.editingCertification !== null);

const formTitle = computed(() => (isEditing.value ? t('certifications.forms.editTitle') : t('certifications.forms.addTitle')));

const validityPeriods = computed(() => [
  { months: 6, label: t('certifications.validityPeriods.6months') },
  { months: 12, label: t('certifications.validityPeriods.1year') },
  { months: 24, label: t('certifications.validityPeriods.2years') },
  { months: 36, label: t('certifications.validityPeriods.3years') },
  { months: 60, label: t('certifications.validityPeriods.5years') },
]);

const validityInfo = computed(() => {
  const issueDate = formData.value?.issue_date;
  const expiryDate = formData.value?.expiry_date;

  if (!issueDate || !expiryDate) return null;

  const issue = new Date(issueDate);
  const expiry = new Date(expiryDate);
  const diffDays = Math.ceil((expiry.getTime() - issue.getTime()) / (1000 * 60 * 60 * 24));

  if (diffDays < 0) {
    return {
      type: 'error' as const,
      icon: 'mdi-alert-circle',
      text: t('certifications.validityInfo.dateError'),
    };
  }

  const months = Math.round(diffDays / 30);
  const years = Math.floor(months / 12);
  const remainingMonths = months % 12;

  // Logika budowania tekstu okresu (np. "1 rok i 3 miesiące") pozostaje dynamiczna
  // ponieważ JSON nie zawiera generycznych kluczy dla lat/miesięcy w sekcji common
  let periodText = '';
  if (years > 0) {
    periodText = `${years} ${years === 1 ? 'rok' : years < 5 ? 'lata' : 'lat'}`;
    if (remainingMonths > 0) {
      periodText += ` i ${remainingMonths} ${remainingMonths === 1 ? 'miesiąc' : remainingMonths < 5 ? 'miesiące' : 'miesięcy'}`;
    }
  } else {
    periodText = `${months} ${months === 1 ? 'miesiąc' : months < 5 ? 'miesiące' : 'miesięcy'}`;
  }

  if (diffDays < 180) {
    return {
      type: 'warning' as const,
      icon: 'mdi-clock-alert',
      text: t('certifications.validityInfo.tooShort', { period: periodText }),
    };
  }

  return {
    type: 'info' as const,
    icon: 'mdi-information',
    text: t('certifications.validityInfo.normal', { period: periodText }),
  };
});

const rules = {
  required: (v: string | number | null | undefined) => {
    if (typeof v === 'number') return v !== 0 || t('validation.required');
    return !!v || t('validation.required');
  },
  afterIssueDate: (v: string) => {
    const issueDate = formData.value?.issue_date;
    if (!v || !issueDate) return true;
    return new Date(v) > new Date(issueDate) || t('certifications.validityInfo.dateError');
  },
};

function getInitials(name: string): string {
  if (!name) return '?';
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

function setValidityPeriod(months: number) {
  const issueDate = formData.value?.issue_date;
  if (!issueDate) return;

  const issue = new Date(issueDate);
  const expiryDate = new Date(issue);
  expiryDate.setMonth(expiryDate.getMonth() + months);

  formData.value.expiry_date = expiryDate.toISOString().split('T')[0];
}

function isSelectedPeriod(months: number): boolean {
  const issueDate = formData.value?.issue_date;
  const expiryDate = formData.value?.expiry_date;

  if (!issueDate || !expiryDate) return false;

  const issue = new Date(issueDate);
  const expiry = new Date(expiryDate);
  const diffMonths = Math.round((expiry.getTime() - issue.getTime()) / (1000 * 60 * 60 * 24 * 30));

  return Math.abs(diffMonths - months) < 1;
}

function resetForm() {
  formData.value = getInitialFormData();
  state.value.error = '';
  formRef.value?.validate?.();
}

function populateFormFromCertification(cert: Certification) {
  formData.value = {
    technician: cert.technician,
    manufacturer: cert.manufacturer,
    certificate_number: cert.certificate_number,
    issue_date: cert.issue_date,
    expiry_date: cert.expiry_date,
  };
}

function closeDialog() {
  emit('update:modelValue', false);
}

async function handleFormSubmit() {
  const validation = await formRef.value?.validate();
  if (!validation?.valid) {
    return;
  }

  state.value.isSaving = true;
  state.value.error = '';
  fieldErrors.value = {};

  try {
    if (isEditing.value && props.editingCertification) {
      await certificationsStore.updateCertification(
        props.editingCertification.id,
        formData.value
      );
    } else {
      await certificationsStore.addCertification(formData.value);
    }

    const message = isEditing.value
      ? t('certifications.forms.editSuccess')
      : t('certifications.forms.addSuccess');
    emit('save-success', message);
    closeDialog();
    certificationsStore.fetchCertifications(true);
  } catch (error) {
    console.error('Błąd zapisu:', error);

    if (error instanceof ApiValidationError) {
      const errors = error.fieldErrors;

      if (errors.non_field_errors) {
        state.value.error = t('certifications.errors.duplicateCertification');
      } else {
        Object.entries(errors).forEach(([field, messages]) => {
          fieldErrors.value[field] = Array.isArray(messages)
            ? messages[0]
            : String(messages);
        });

        state.value.error = t('certifications.errors.validationFailed');
      }
    } else {
      state.value.error = error instanceof Error
        ? error.message
        : t('common.errors.unknown');
    }
  } finally {
    state.value.isSaving = false;
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.editingCertification) {
      populateFormFromCertification(props.editingCertification);
    } else {
      resetForm();
    }
  }
});

watch(() => props.editingCertification, (newCert) => {
  if (newCert && props.modelValue) {
    populateFormFromCertification(newCert);
  }
}, { immediate: true });

onMounted(() => {
  techniciansStore.fetchTechnicians();
  manufacturersStore.fetchManufacturers();
});
</script>

<style scoped>
.certification-form-card {
  overflow: hidden;
}

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

.form-content {
  padding: 24px;
  max-height: calc(100vh - 300px);
  overflow-y: auto;
}

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

.form-footer {
  padding: 16px 24px;
  background: rgb(var(--v-theme-surface));
}

:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}

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
}
</style>
