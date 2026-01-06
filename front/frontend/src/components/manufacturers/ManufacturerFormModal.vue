<template>
  <v-dialog
    v-model="isDialogOpen"
    max-width="500px"
    persistent
    :fullscreen="isMobile"
  >
    <v-card class="manufacturer-form-card" rounded="lg">
      <div class="form-header">
        <div class="d-flex align-center">
          <v-avatar
            :color="isEditing ? 'primary' : 'success'"
            size="48"
            class="mr-4"
          >
            <v-icon size="24" color="white">
              {{ isEditing ? 'mdi-factory' : 'mdi-domain-plus' }}
            </v-icon>
          </v-avatar>
          <div>
            <h2 class="text-h5 font-weight-bold mb-1">
              {{ formTitle }}
            </h2>
            <p class="text-body-2 text-medium-emphasis mb-0">
              {{ isEditing ? t('manufacturers.forms.editSubtitle') : t('manufacturers.forms.addSubtitle') }}
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
              <v-icon start size="18" color="primary">mdi-information</v-icon>
              {{ t('manufacturers.sections.basicInfo') }}
            </h3>

            <v-text-field
              v-model="formData.name"
              :label="t('manufacturers.forms.nameLabel')"
              :placeholder="t('manufacturers.placeholders.name')"
              :rules="[rules.required]"
              variant="outlined"
              density="comfortable"
              autofocus
              counter
              maxlength="100"
            >
              <template #prepend-inner>
                <v-icon color="primary" size="20">mdi-domain</v-icon>
              </template>
            </v-text-field>

            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mt-4"
            >
              <template #prepend>
                <v-icon size="18">mdi-lightbulb</v-icon>
              </template>
              <span class="text-caption">
                {{ t('manufacturers.hints.nameInfo') }}
              </span>
            </v-alert>
          </div>

          <div v-if="formData.name" class="preview-section mt-6">
            <h3 class="section-title">
              <v-icon start size="18" color="primary">mdi-eye</v-icon>
              {{ t('common.preview') }}
            </h3>

            <v-card variant="outlined" class="preview-card pa-4">
              <div class="d-flex align-center">
                <v-avatar color="secondary" size="48" variant="tonal" class="mr-4">
                  <span class="text-h6 font-weight-bold">
                    {{ getInitials(formData.name) }}
                  </span>
                </v-avatar>
                <div>
                  <span class="text-body-1 font-weight-medium">
                    {{ formData.name }}
                  </span>
                  <p class="text-caption text-medium-emphasis mb-0">
                    {{ t('manufacturers.preview.willAppear') }}
                  </p>
                </div>
              </div>
            </v-card>
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
          @click="handleResetForm"
        >
          <v-icon start>mdi-refresh</v-icon>
          {{ t('common.clear') }}
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          :loading="state.isSaving"
          :disabled="!formData.name"
          @click="handleFormSubmit"
        >
          <v-icon start>{{ isEditing ? 'mdi-content-save' : 'mdi-plus' }}</v-icon>
          {{ isEditing ? t('common.save') : t('manufacturers.actions.add') }}
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { useManufacturersStore } from '@/stores/manufacturers';
import { extractApiError } from '@/utils/apiErrors';
import type { Manufacturer } from '@/types';

type ManufacturerPayload = Pick<Manufacturer, 'name'>;

const props = defineProps<{
  modelValue: boolean;
  editingManufacturer: Manufacturer | null;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save-success', message: string, newManufacturer?: Manufacturer): void;
}>();

const { t } = useI18n();
const manufacturersStore = useManufacturersStore();
const display = useDisplay();

const isMobile = computed(() => display.smAndDown.value);

const formRef = ref<{ validate: () => Promise<{ valid: boolean }>; reset: () => void } | null>(null);

const state = ref({
  isSaving: false,
  error: '',
});

const getInitialFormData = (): ManufacturerPayload => ({
  name: '',
});

const formData = ref<ManufacturerPayload>(getInitialFormData());

const isDialogOpen = computed({
  get: () => props.modelValue,
  set: (val: boolean) => emit('update:modelValue', val),
});

const isEditing = computed(() => props.editingManufacturer !== null);

const formTitle = computed(() =>
  isEditing.value
    ? t('manufacturers.forms.editTitle')
    : t('manufacturers.forms.addTitle')
);

const rules = {
  required: (v: string | null | undefined) => !!v?.trim() || t('validation.required'),
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

function populateFormFromManufacturer(manufacturer: Manufacturer) {
  formData.value = {
    name: manufacturer.name,
  };
}

function handleResetForm() {
  formData.value = getInitialFormData();
  state.value.error = '';
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

  try {
    let savedManufacturer: Manufacturer | undefined;

    if (isEditing.value && props.editingManufacturer) {
      await manufacturersStore.updateManufacturer(
        props.editingManufacturer.id,
        formData.value
      );
    } else {
      savedManufacturer = await manufacturersStore.addManufacturer(formData.value);
    }

    const message = isEditing.value
      ? t('manufacturers.forms.editSuccess')
      : t('manufacturers.forms.addSuccess');

    emit('save-success', message, savedManufacturer);
    closeDialog();
    manufacturersStore.fetchManufacturers(true);
  } catch (error) {
    console.error('Błąd zapisu producenta:', error);
    state.value.error = extractApiError(error, t('common.errors.unknown'));
  } finally {
    state.value.isSaving = false;
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    if (props.editingManufacturer) {
      populateFormFromManufacturer(props.editingManufacturer);
    } else {
      handleResetForm();
    }
  }
});

watch(() => props.editingManufacturer, (newManufacturer) => {
  if (newManufacturer && props.modelValue) {
    populateFormFromManufacturer(newManufacturer);
  }
}, { immediate: true });
</script>

<style scoped>
.manufacturer-form-card {
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
}

.form-section,
.preview-section {
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

.preview-card {
  border-radius: 12px;
  background: rgba(var(--v-theme-primary), 0.02);
  border-color: rgba(var(--v-theme-primary), 0.2);
}

:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}

@media (max-width: 600px) {
  .form-header {
    padding: 16px;
  }

  .form-content {
    padding: 16px;
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
