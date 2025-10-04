<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="400" class="pa-5">
      <v-card-title class="text-h5 text-center mb-4">
        Zaloguj się
      </v-card-title>
      <v-card-text>
        <v-form ref="form" @submit.prevent="handleLogin">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">
            {{ error }}
          </v-alert>

          <v-text-field
            v-model="username"
            label="Nazwa użytkownika"
            prepend-inner-icon="mdi-account"
            variant="outlined"
            :rules="[rules.required]"
            :disabled="isLoading"
          ></v-text-field>

          <v-text-field
            v-model="password"
            label="Hasło"
            prepend-inner-icon="mdi-lock"
            variant="outlined"
            type="password"
            :rules="[rules.required]"
            class="mt-3"
            :disabled="isLoading"
          ></v-text-field>

          <v-btn type="submit" color="primary" block class="mt-4" :loading="isLoading">
            Zaloguj
          </v-btn>
        </v-form>
      </v-card-text>
      <v-card-actions class="justify-center mt-2">
        <span class="text-body-2">Nie masz konta?</span>
        <v-btn :to="{ name: 'register' }" variant="text" color="primary" size="small">
          Zarejestruj się
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import type { VForm } from 'vuetify/components'

const authStore = useAuthStore()
const form = ref<VForm | null>(null)
const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref<string | null>(null)

const rules = {
  required: (value: string) => !!value || 'Pole jest wymagane.',
}

const handleLogin = async () => {
  const { valid } = await form.value!.validate()
  if (!valid) return

  isLoading.value = true
  error.value = null
  try {
    await authStore.login({
      username: username.value,
      password: password.value,
    })
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Nieprawidłowe dane logowania.'
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
