<template>
  <v-card rounded="lg" class="settings-card">
    <!-- Header -->
    <div class="card-header">
      <div class="d-flex align-center justify-space-between">
        <div class="d-flex align-center">
          <v-avatar color="primary" size="40" variant="tonal" class="mr-3">
            <v-icon size="20">mdi-office-building</v-icon>
          </v-avatar>
          <div>
            <h3 class="text-h6 font-weight-bold mb-0">
              {{ t('settings.company.title') }}
            </h3>
            <p class="text-caption text-medium-emphasis mb-0">
              {{ isAdmin ? t('settings.company.subtitleAdmin') : t('settings.company.subtitleUser') }}
            </p>
          </div>
        </div>
        <v-chip
          :color="isAdmin ? 'success' : 'grey'"
          size="small"
          variant="tonal"
        >
          <v-icon start size="14">
            {{ isAdmin ? 'mdi-shield-crown' : 'mdi-eye' }}
          </v-icon>
          {{ isAdmin ? t('settings.roles.admin') : t('settings.roles.viewer') }}
        </v-chip>
      </div>
    </div>

    <v-divider />

    <!-- Content -->
    <v-card-text class="pa-6">
      <v-form ref="formRef" @submit.prevent="handleSave">
        <div class="form-field-group">
          <label class="field-label">
            <v-icon size="16" class="mr-1">mdi-domain</v-icon>
            {{ t('settings.company.nameLabel') }}
          </label>
          <v-text-field
            v-model="localName"
            :placeholder="t('settings.company.namePlaceholder')"
            variant="outlined"
            density="comfortable"
            :readonly="!isAdmin"
            :disabled="!isAdmin"
            :rules="isAdmin ? [rules.required] : []"
            :bg-color="!isAdmin ? 'grey-lighten-4' : undefined"
          >
            <template #prepend-inner>
              <v-icon color="primary" size="20">mdi-office-building-marker</v-icon>
            </template>
            <template v-if="!isAdmin" #append-inner>
              <v-tooltip location="top">
                <template #activator="{ props }">
                  <v-icon v-bind="props" size="18" color="grey">mdi-lock</v-icon>
                </template>
                {{ t('settings.company.readonlyHint') }}
              </v-tooltip>
            </template>
          </v-text-field>
        </div>

        <!-- Admin-only info -->
        <v-alert
          v-if="!isAdmin"
          type="info"
          variant="tonal"
          density="compact"
          class="mt-4"
        >
          <template #prepend>
            <v-icon size="18">mdi-information</v-icon>
          </template>
          <span class="text-caption">
            {{ t('settings.company.adminOnlyInfo') }}
          </span>
        </v-alert>

        <!-- Save button (admin only) -->
        <div v-if="isAdmin" class="mt-6 d-flex justify-end">
          <v-btn
            type="submit"
            color="primary"
            variant="flat"
            :loading="isSaving"
            :disabled="!hasChanges || isSaving"
          >
            <v-icon start>mdi-content-save</v-icon>
            {{ t('common.save') }}
          </v-btn>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';

interface Company {
  id?: string;
  name?: string;
}

// Props & Emits
const props = defineProps<{
  companyData: Partial<Company>;
  isAdmin: boolean;
  isSaving: boolean;
}>();

const emit = defineEmits<{
  (e: 'save', name: string): void;
  (e: 'update:company-data', data: Partial<Company>): void;
}>();

// Composables
const { t } = useI18n();

// Refs
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);
const localName = ref(props.companyData.name || '');

// Computed
const hasChanges = computed(() => localName.value !== props.companyData.name);

// Validation rules
const rules = {
  required: (v: string) => !!v?.trim() || t('validation.required'),
};

// Methods
async function handleSave() {
  if (!props.isAdmin) return;

  const validation = await formRef.value?.validate();
  if (!validation?.valid) return;

  emit('save', localName.value);
}

// Watch for external changes
watch(() => props.companyData.name, (newName) => {
  if (newName !== undefined) {
    localName.value = newName;
  }
});
</script>

<style scoped>
.settings-card {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  transition: all 0.3s ease;
}

.settings-card:hover {
  border-color: rgba(var(--v-theme-primary), 0.2);
}

.card-header {
  padding: 20px 24px;
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-primary), 0.04) 0%,
    rgba(var(--v-theme-primary), 0.01) 100%
  );
}

.form-field-group {
  margin-bottom: 8px;
}

.field-label {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-bottom: 8px;
}

:deep(.v-field) {
  border-radius: 10px;
}

:deep(.v-field__prepend-inner) {
  padding-right: 8px;
}
</style>
