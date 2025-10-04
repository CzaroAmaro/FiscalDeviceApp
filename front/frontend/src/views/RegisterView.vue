<!-- src/views/RegisterView.vue -->
<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="450" class="pa-5">
      <v-card-title class="text-h5 text-center mb-4">
        Utwórz nowe konto
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleRegister">
          <!-- Generyczny błąd, jeśli wystąpi -->
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
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const formData = reactive({
  username: '',
  email: '',
  password: '',
  passwordConfirm: '',
})

// Używamy `reactive` do przechowywania błędów z backendu.
// Klucze będą odpowiadać nazwom pól (np. 'username', 'email').
const errors = reactive<Record<string, any>>({})
const isLoading = ref(false)

const handleRegister = async () => {
  // Resetowanie błędów przed każdą próbą
  Object.keys(errors).forEach(key => delete errors[key]);

  // Prosta walidacja po stronie klienta
  if (formData.password !== formData.passwordConfirm) {
    errors.passwordConfirm = 'Hasła nie są zgodne.'
    return;
  }

  isLoading.value = true
  try {
    // Wywołujemy akcję ze store'a, przekazując dane bez `passwordConfirm`
    await authStore.register({
      username: formData.username,
      email: formData.email,
      password: formData.password,
    })
    // Przekierowanie jest już w akcji store'a
  } catch (err: any) {
    // Przechwytujemy błąd rzucony przez store
    if (err.response && err.response.data) {
      // Przypisujemy błędy zwrócone przez Django do naszego obiektu `errors`
      // To automatycznie wyświetli je pod odpowiednimi polami formularza
      Object.assign(errors, err.response.data);
    } else {
      errors.detail = "Wystąpił nieoczekiwany błąd. Spróbuj ponownie.";
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>
