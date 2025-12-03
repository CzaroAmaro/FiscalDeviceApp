<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="450" class="pa-5">
      <v-card-title class="text-h5 text-center mb-4">
        Utwórz nowe konto
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleRegister">
          <v-alert v-if="errors.detail" type="error" density="compact" class="mb-4">
            {{ errors.detail }}
          </v-alert>

          <v-text-field
            v-model="formData.username"
            label="Nazwa użytkownika"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            required
            :error-messages="errors.username"
          ></v-text-field>

          <v-text-field
            v-model="formData.email"
            label="Adres e-mail"
            prepend-inner-icon="mdi-email"
            variant="outlined"
            required
            class="mt-3"
            :error-messages="errors.email"
          ></v-text-field>

          <v-text-field
            v-model="formData.password"
            label="Hasło"
            prepend-inner-icon="mdi-lock"
            variant="outlined"
            type="password"
            required
            class="mt-3"
            :error-messages="errors.password"
          ></v-text-field>

          <v-text-field
            v-model="formData.passwordConfirm"
            label="Potwierdź hasło"
            prepend-inner-icon="mdi-lock-check"
            variant="outlined"
            type="password"
            required
            class="mt-3"
            :error-messages="errors.passwordConfirm"
          ></v-text-field>


          <v-btn
            type="submit"
            color="primary"
            block
            class="mt-4"
            :loading="isLoading"
            :disabled="isLoading"
          >
            Zarejestruj
          </v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center">
        <span class="text-body-2">Masz już konto?</span>
        <v-btn :to="{ name: 'login' }" variant="text" color="primary" size="small">Zaloguj się</v-btn>
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
import { reactive, ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme'; // <-- NOWY IMPORT
import LanguageSelect from '@/components/languageSelect/LanguageSelect.vue'; // <-- NOWY IMPORT

const authStore = useAuthStore();
const themeStore = useThemeStore(); // <-- INICJALIZACJA STORE'A

const formData = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
});

const errors = reactive<Record<string, any>>({});
const isLoading = ref(false);

const handleRegister = async () => {
  Object.keys(errors).forEach(key => delete errors[key]);

  if (formData.password !== formData.passwordConfirm) {
    errors.passwordConfirm = 'Hasła nie są zgodne.';
    return;
  }

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
      errors.detail = "Wystąpił nieoczekiwany błąd. Spróbuj ponownie.";
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
</style>
