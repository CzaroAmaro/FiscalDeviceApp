<template>
  <v-card rounded="lg" class="settings-card">
    <!-- Header -->
    <div class="card-header">
      <div class="d-flex align-center">
        <v-avatar color="success" size="40" variant="tonal" class="mr-3">
          <v-icon size="20">mdi-account-edit</v-icon>
        </v-avatar>
        <div>
          <h3 class="text-h6 font-weight-bold mb-0">
            {{ t('settings.profile.title') }}
          </h3>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ t('settings.profile.subtitle') }}
          </p>
        </div>
      </div>
    </div>

    <v-divider />

    <!-- Content -->
    <v-card-text class="pa-6">
      <!-- Current user info -->
      <div class="user-info-banner mb-6">
        <div class="d-flex align-center">
          <v-avatar color="primary" size="56" variant="tonal" class="mr-4">
            <span class="text-h6 font-weight-bold">
              {{ userInitials }}
            </span>
          </v-avatar>
          <div>
            <span class="text-body-1 font-weight-bold d-block">
              {{ fullName || t('settings.profile.noName') }}
            </span>
            <span class="text-caption text-medium-emphasis">
              {{ authStore.user?.email }}
            </span>
            <div class="mt-1">
              <v-chip size="x-small" color="primary" variant="tonal">
                {{ authStore.user?.username }}
              </v-chip>
            </div>
          </div>
        </div>
      </div>

      <v-form ref="formRef" @submit.prevent="saveProfile">
        <v-row dense>
          <v-col cols="12" sm="6">
            <div class="form-field-group">
              <label class="field-label">
                <v-icon size="16" class="mr-1">mdi-account</v-icon>
                {{ t('settings.profile.firstName') }}
              </label>
              <v-text-field
                v-model="form.first_name"
                :placeholder="t('settings.profile.firstNamePlaceholder')"
                variant="outlined"
                density="comfortable"
              >
                <template #prepend-inner>
                  <v-icon color="primary" size="20">mdi-account-outline</v-icon>
                </template>
              </v-text-field>
            </div>
          </v-col>
          <v-col cols="12" sm="6">
            <div class="form-field-group">
              <label class="field-label">
                <v-icon size="16" class="mr-1">mdi-account</v-icon>
                {{ t('settings.profile.lastName') }}
              </label>
              <v-text-field
                v-model="form.last_name"
                :placeholder="t('settings.profile.lastNamePlaceholder')"
                variant="outlined"
                density="comfortable"
              >
                <template #prepend-inner>
                  <v-icon color="primary" size="20">mdi-account-outline</v-icon>
                </template>
              </v-text-field>
            </div>
          </v-col>
        </v-row>

        <!-- Preview -->
        <v-expand-transition>
          <div v-if="hasChanges" class="preview-section mt-4">
            <v-alert type="info" variant="tonal" density="compact">
              <template #prepend>
                <v-icon size="18">mdi-eye</v-icon>
              </template>
              <div class="d-flex align-center">
                <span class="text-caption mr-2">{{ t('settings.profile.preview') }}:</span>
                <span class="font-weight-medium">
                  {{ form.first_name }} {{ form.last_name }}
                </span>
              </div>
            </v-alert>
          </div>
        </v-expand-transition>

        <!-- Actions -->
        <div class="mt-6 d-flex justify-end ga-2">
          <v-btn
            v-if="hasChanges"
            variant="text"
            @click="resetForm"
          >
            {{ t('common.cancel') }}
          </v-btn>
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

    <!-- Snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="3000"
      location="bottom right"
    >
      <div class="d-flex align-center">
        <v-icon class="mr-2">
          {{ snackbar.color === 'success' ? 'mdi-check-circle' : 'mdi-alert-circle' }}
        </v-icon>
        {{ snackbar.text }}
      </div>
    </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import api from '@/api';
import { useAuthStore } from '@/stores/auth.ts';

// Composables
const { t } = useI18n();
const authStore = useAuthStore();

// Refs
const formRef = ref<{ validate: () => Promise<{ valid: boolean }> } | null>(null);
const isSaving = ref(false);

const form = reactive({
  first_name: '',
  last_name: '',
});

const originalForm = reactive({
  first_name: '',
  last_name: '',
});

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success' as 'success' | 'error',
});

// Computed
const fullName = computed(() => {
  const firstName = form.first_name || authStore.user?.first_name || '';
  const lastName = form.last_name || authStore.user?.last_name || '';
  return `${firstName} ${lastName}`.trim();
});

const userInitials = computed(() => {
  const firstName = form.first_name || authStore.user?.first_name || '';
  const lastName = form.last_name || authStore.user?.last_name || '';

  if (!firstName && !lastName) return '?';

  return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
});

const hasChanges = computed(() => {
  return form.first_name !== originalForm.first_name ||
    form.last_name !== originalForm.last_name;
});

// Methods
function loadUserData() {
  if (authStore.user) {
    form.first_name = authStore.user.first_name || '';
    form.last_name = authStore.user.last_name || '';
    originalForm.first_name = form.first_name;
    originalForm.last_name = form.last_name;
  }
}

function resetForm() {
  form.first_name = originalForm.first_name;
  form.last_name = originalForm.last_name;
}

async function saveProfile() {
  isSaving.value = true;

  try {
    const response = await api.patch('/users/profile/', {
      first_name: form.first_name,
      last_name: form.last_name,
    });

    authStore.updateUser(response.data);

    originalForm.first_name = form.first_name;
    originalForm.last_name = form.last_name;

    snackbar.text = t('settings.profile.saveSuccess');
    snackbar.color = 'success';
    snackbar.show = true;
  } catch (err) {
    snackbar.text = t('settings.errors.saveFailed');
    snackbar.color = 'error';
    snackbar.show = true;
    console.error(err);
  } finally {
    isSaving.value = false;
  }
}

// Lifecycle
onMounted(() => {
  loadUserData();
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
    rgba(var(--v-theme-success), 0.04) 0%,
    rgba(var(--v-theme-success), 0.01) 100%
  );
}

.user-info-banner {
  padding: 16px;
  border-radius: 12px;
  background: rgba(var(--v-theme-primary), 0.04);
  border: 1px solid rgba(var(--v-theme-primary), 0.1);
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

.v-expand-transition-enter-active,
.v-expand-transition-leave-active {
  transition: all 0.3s ease;
}
</style>
