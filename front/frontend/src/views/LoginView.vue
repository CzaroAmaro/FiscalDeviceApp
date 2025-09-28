<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="400" class="pa-5">
      <v-card-title class="text-h5 text-center mb-4">
        Zaloguj się
      </v-card-title>
      <v-card-text>
        <v-form @submit.prevent="handleLogin">
          <v-text-field
            v-model="username"
            label="Nazwa użytkownika"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            required
            :disabled="isLoading"
          ></v-text-field>

          <v-text-field
            v-model="password"
            label="Hasło"
            prepend-inner-icon="mdi-lock"
            variant="outlined"
            type="password"
            required
            class="mt-3"
            :disabled="isLoading"
          ></v-text-field>

          <v-btn
            type="submit"
            color="primary"
            block
            class="mt-4"
            :loading="isLoading"
            :disabled="isLoading"
          >
            Zaloguj
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth' // Importujemy nasz authStore

// Pobieramy instancję store'a
const authStore = useAuthStore()

// Reaktywne zmienne do przechowywania danych z formularza
const username = ref('')
const password = ref('')
const isLoading = ref(false) // Dodajemy stan ładowania

const handleLogin = async () => {
  if (!username.value || !password.value) {
    alert('Proszę wypełnić oba pola.')
    return
  }

  isLoading.value = true // Ustawiamy stan ładowania
  try {
    // Wywołujemy akcję 'login' z naszego store'a, przekazując dane
    await authStore.login({
      username: username.value,
      password: password.value,
    })
    // Reszta logiki (przekierowanie) jest już obsłużona wewnątrz akcji 'login'
  } catch (error) {
    // Błąd jest już obsługiwany w store, ale możemy tu dodać dodatkową logikę
    console.error("Wystąpił błąd w komponencie LoginView", error)
  } finally {
    isLoading.value = false // Wyłączamy stan ładowania niezależnie od wyniku
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>
