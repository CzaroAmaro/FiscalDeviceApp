<template>
  <v-card rounded="lg" class="settings-card">
    <div class="card-header card-header--email">
      <div class="d-flex align-center">
        <v-avatar color="warning" size="40" variant="tonal" class="mr-3">
          <v-icon size="20">mdi-email-edit</v-icon>
        </v-avatar>
        <div>
          <h3 class="text-h6 font-weight-bold mb-0">
            {{ t('settings.email.title') }}
          </h3>
          <p class="text-caption text-medium-emphasis mb-0">
            {{ t('settings.email.subtitle') }}
          </p>
        </div>
      </div>
    </div>

    <v-divider />

    <v-card-text class="pa-6">
      <div class="current-email-banner mb-6">
        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-avatar color="primary" size="40" variant="tonal" class="mr-3">
              <v-icon size="20">mdi-email-check</v-icon>
            </v-avatar>
            <div>
              <span class="text-caption text-medium-emphasis d-block">
                {{ t('settings.email.currentEmail') }}
              </span>
              <span class="text-body-1 font-weight-medium">
                {{ authStore.user?.email || '-' }}
              </span>
            </div>
          </div>
          <v-chip size="small" color="success" variant="tonal">
            <v-icon start size="14">mdi-check-circle</v-icon>
            {{ t('settings.email.verified') }}
          </v-chip>
        </div>
      </div>

      <v-alert
        v-if="successMessage"
        type="success"
        variant="tonal"
        density="compact"
        class="mb-6"
        closable
        @click:close="successMessage = null"
      >
        <template #prepend>
          <v-icon>mdi-check-circle</v-icon>
        </template>
        {{ successMessage }}
      </v-alert>

      <v-alert
        v-if="errorMessage"
        type="error"
        variant="tonal"
        density="compact"
        class="mb-6"
        closable
        @click:close="errorMessage = null"
      >
        <template #prepend>
          <v-icon>mdi-alert-circle</v-icon>
        </template>
        {{ errorMessage }}
      </v-alert>

      <v-form ref="formRef" @submit.prevent="requestChange">
        <v-row dense>
          <v-col cols="12">
            <div class="form-field-group">
              <label class="field-label">
                <v-icon size="16" class="mr-1">mdi-email-plus</v-icon>
                {{ t('settings.email.newEmailLabel') }}
              </label>
              <v-text-field
                v-model="newEmail"
                type="email"
                :placeholder="t('settings.email.newEmailPlaceholder')"
                :rules="[rules.required, rules.email, rules.different]"
                variant="outlined"
                density="comfortable"
              >
                <template #prepend-inner>
                  <v-icon color="primary" size="20">mdi-email-outline</v-icon>
                </template>
              </v-text-field>
            </div>
          </v-col>

          <v-col cols="12">
            <div class="form-field-group">
              <label class="field-label">
                <v-icon size="16" class="mr-1">mdi-lock</v-icon>
                {{ t('settings.email.passwordLabel') }}
              </label>
              <v-text-field
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                :placeholder="t('settings.email.passwordPlaceholder')"
                :rules="[rules.required]"
                variant="outlined"
                density="comfortable"
                :hint="t('settings.email.passwordHint')"
                persistent-hint
              >
                <template #prepend-inner>
                  <v-icon color="primary" size="20">mdi-lock-outline</v-icon>
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
            </div>
          </v-col>
        </v-row>

        <v-alert
          type="info"
          variant="tonal"
          density="compact"
          class="mt-4"
        >
          <template #prepend>
            <v-icon size="18">mdi-information</v-icon>
          </template>
          <span class="text-caption">
            {{ t('settings.email.processInfo') }}
          </span>
        </v-alert>

        <div class="mt-6 d-flex justify-end">
          <v-btn
            type="submit"
            color="warning"
            variant="flat"
            :loading="isLoading"
            :disabled="!isFormValid || isLoading"
          >
            <v-icon start>mdi-send</v-icon>
            {{ t('settings.email.sendRequest') }}
          </v-btn>
        </div>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import api from '@/api';
import { useAuthStore } from '@/stores/auth.ts';

const { t } = useI18n();
const authStore = useAuthStore();

const formRef = ref<{ validate: () => Promise<{ valid: boolean }>; reset: () => void } | null>(null);
const newEmail = ref('');
const password = ref('');
const showPassword = ref(false);
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

const isFormValid = computed(() => {
  return newEmail.value.trim() !== '' &&
    password.value.trim() !== '' &&
    newEmail.value !== authStore.user?.email;
});

const rules = {
  required: (v: string) => !!v?.trim() || t('validation.required'),
  email: (v: string) => /.+@.+\..+/.test(v) || t('validation.email'),
  different: (v: string) => v !== authStore.user?.email || t('settings.email.mustBeDifferent'),
};

async function requestChange() {
  const validation = await formRef.value?.validate();
  if (!validation?.valid) return;

  isLoading.value = true;
  errorMessage.value = null;
  successMessage.value = null;

  try {
    const response = await api.post('/users/change-email/', {
      new_email: newEmail.value,
      password: password.value,
    });

    successMessage.value = response.data.detail || t('settings.email.requestSuccess');

    newEmail.value = '';
    password.value = '';
    formRef.value?.reset();
  } catch (error: unknown) {
    const err = error as { response?: { data?: { error?: string; new_email?: string[] } } };
    errorMessage.value = err.response?.data?.error ||
      err.response?.data?.new_email?.[0] ||
      t('settings.errors.unknown');
  } finally {
    isLoading.value = false;
  }
}
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

.card-header--email {
  background: linear-gradient(
    135deg,
    rgba(var(--v-theme-warning), 0.06) 0%,
    rgba(var(--v-theme-warning), 0.02) 100%
  );
}

.current-email-banner {
  padding: 16px;
  border-radius: 12px;
  background: rgba(var(--v-theme-success), 0.04);
  border: 1px solid rgba(var(--v-theme-success), 0.1);
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
