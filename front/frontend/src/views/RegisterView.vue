<template>
  <v-container class="fill-height d-flex justify-center align-center auth-container">
    <img src="@/assets/logo-fiscal.png" alt="Fiscal Service App Logo" class="auth-logo" />
    <v-card width="500" class="pa-5">
      <v-card-title class="text-h5 text-center mb-4">
        {{ t('register.title') }}
      </v-card-title>
      <v-card-text>
        <v-form ref="formRef" v-model="isFormValid" @submit.prevent="handleRegister">
          <v-alert v-if="errors.detail" type="error" density="compact" class="mb-4">
            {{ errors.detail }}
          </v-alert>

          <v-text-field
            v-model="formData.username"
            :label="t('register.username')"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            :rules="usernameRules"
            :error-messages="errors.username"
            counter="30"
            @update:model-value="clearFieldError('username')"
          ></v-text-field>

          <v-text-field
            v-model="formData.email"
            :label="t('register.email')"
            prepend-inner-icon="mdi-email"
            variant="outlined"
            :rules="emailRules"
            class="mt-3"
            :error-messages="errors.email"
            @update:model-value="clearFieldError('email')"
          ></v-text-field>

          <v-text-field
            v-model="formData.password"
            :label="t('register.password')"
            prepend-inner-icon="mdi-lock"
            :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
            variant="outlined"
            :type="showPassword ? 'text' : 'password'"
            :rules="passwordRules"
            class="mt-3"
            :error-messages="errors.password"
            @click:append-inner="showPassword = !showPassword"
            @update:model-value="clearFieldError('password')"
          ></v-text-field>

          <v-expand-transition>
            <div v-if="formData.password" class="mb-3">
              <div class="d-flex align-center justify-space-between mb-1">
                <span class="text-caption">{{ t('register.passwordRequirements') }}</span>
                <v-chip
                  :color="passwordStrength.color"
                  size="x-small"
                  label
                >
                  {{ passwordStrength.label }}
                </v-chip>
              </div>
              <v-progress-linear
                :model-value="passwordStrength.percentage"
                :color="passwordStrength.color"
                height="4"
                rounded
              ></v-progress-linear>

              <div class="mt-2">
                <v-row dense>
                  <v-col v-for="req in passwordRequirements" :key="req.key" cols="6">
                    <div class="d-flex align-center">
                      <v-icon
                        :color="req.met ? 'success' : 'grey'"
                        size="16"
                        class="mr-1"
                      >
                        {{ req.met ? 'mdi-check-circle' : 'mdi-circle-outline' }}
                      </v-icon>
                      <span
                        class="text-caption"
                        :class="req.met ? 'text-success' : 'text-grey'"
                      >
                        {{ req.label }}
                      </span>
                    </div>
                  </v-col>
                </v-row>
              </div>
            </div>
          </v-expand-transition>

          <v-text-field
            v-model="formData.passwordConfirm"
            :label="t('register.passwordConfirm')"
            prepend-inner-icon="mdi-lock-check"
            :append-inner-icon="showPasswordConfirm ? 'mdi-eye-off' : 'mdi-eye'"
            variant="outlined"
            :type="showPasswordConfirm ? 'text' : 'password'"
            :rules="passwordConfirmRules"
            class="mt-3"
            :error-messages="errors.passwordConfirm"
            @click:append-inner="showPasswordConfirm = !showPasswordConfirm"
            @update:model-value="clearFieldError('passwordConfirm')"
          ></v-text-field>

          <v-btn
            type="submit"
            color="primary"
            block
            class="mt-4"
            :loading="isLoading"
            :disabled="isLoading || !isFormValid"
          >
            {{ t('register.submit') }}
          </v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center">
        <span class="text-body-2">{{ t('register.hasAccount') }}</span>
        <v-btn :to="{ name: 'login' }" variant="text" color="primary" size="small">
          {{ t('register.login') }}
        </v-btn>
      </v-card-actions>

      <v-divider class="my-3"></v-divider>

      <v-card-text class="pa-0">
        <v-row align="center" justify="center" class="text-caption">
          <v-col cols="auto">
            <div class="d-flex align-center">
              <v-icon start>mdi-weather-night</v-icon>
              <v-switch
                v-model="themeStore.isDark"
                color="primary"
                hide-details
                inset
                @update:model-value="themeStore.toggleTheme"
              ></v-switch>
              <v-icon end>mdi-white-balance-sunny</v-icon>
            </div>
          </v-col>
          <v-col cols="auto">
            <LanguageSelect />
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import type { VForm } from 'vuetify/components';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import LanguageSelect from '@/components/languageSelect/LanguageSelect.vue';
import { createValidationRules, calculatePasswordStrength } from '@/utils/validationRules';

const { t } = useI18n();
const authStore = useAuthStore();
const themeStore = useThemeStore();

const rules = createValidationRules(t);

const formRef = ref<VForm | null>(null);
const isFormValid = ref(false);
const isLoading = ref(false);
const showPassword = ref(false);
const showPasswordConfirm = ref(false);

const formData = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
});

const errors = reactive<Record<string, any>>({});

const usernameRules = computed(() => [
  rules.username.required,
  rules.username.minLength,
  rules.username.maxLength,
  rules.username.format,
  rules.username.noStartWithNumber,
]);

const emailRules = computed(() => [
  rules.email.required,
  rules.email.format,
  rules.email.maxLength,
]);

const passwordRules = computed(() => [
  rules.password.required,
  rules.password.minLength,
  rules.password.maxLength,
  rules.password.hasUppercase,
  rules.password.hasLowercase,
  rules.password.hasNumber,
  rules.password.hasSpecialChar,
  rules.password.noSpaces,
  rules.password.notCommon,
]);

const passwordConfirmRules = computed(() => [
  rules.passwordConfirm.required,
  rules.passwordConfirm.matches(formData.password),
]);

const passwordStrength = computed(() => {
  return calculatePasswordStrength(formData.password, t);
});

const passwordRequirements = computed(() => [
  {
    key: 'minLength',
    label: t('register.requirements.minLength'),
    met: formData.password.length >= 8,
  },
  {
    key: 'uppercase',
    label: t('register.requirements.uppercase'),
    met: /[A-Z]/.test(formData.password),
  },
  {
    key: 'lowercase',
    label: t('register.requirements.lowercase'),
    met: /[a-z]/.test(formData.password),
  },
  {
    key: 'number',
    label: t('register.requirements.number'),
    met: /\d/.test(formData.password),
  },
  {
    key: 'special',
    label: t('register.requirements.special'),
    met: /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/`~]/.test(formData.password),
  },
]);

const clearFieldError = (field: string) => {
  if (errors[field]) {
    delete errors[field];
  }
};


const handleRegister = async () => {
  Object.keys(errors).forEach(key => delete errors[key]);

  const { valid } = await formRef.value!.validate();
  if (!valid) return;

  isLoading.value = true;
  try {
    await authStore.register({
      username: formData.username,
      email: formData.email,
      password: formData.password,
    });
  } catch (err: any) {
    if (err.response && err.response.data) {
      Object.assign(errors, err.response.data);
    } else {
      errors.detail = t('register.error') || 'Wystąpił nieoczekiwany błąd. Spróbuj ponownie.';
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
.auth-logo {
  position: absolute;
  top: 2rem;
  left: 80px;
  max-width: 520px;
  opacity: 0.9;
}
@media (max-width: 1500px) {
  .auth-logo {
    top: 1rem;
    left: 1rem;
    max-width: 380px;
  }
}
@media (max-width: 1185px) {
  .auth-logo {
    top: 1rem;
    left: 1rem;
    max-width: 280px;
  }
}
@media (max-width: 960px) {
  .auth-logo {
    top: 1rem;
    left: 1rem;
    max-width: 150px;
  }
}
</style>
