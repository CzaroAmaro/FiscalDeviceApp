<template>
  <v-card flat>
    <v-card-title>Zmiana adresu e-mail</v-card-title>
    <v-card-subtitle>Po wysłaniu prośby, na nowy adres zostanie wysłany link potwierdzający.</v-card-subtitle>

    <v-card-text>
      <v-alert v-if="successMessage" type="success" class="mb-4" density="compact">
        {{ successMessage }}
      </v-alert>
      <v-alert v-if="errorMessage" type="error" class="mb-4" density="compact">
        {{ errorMessage }}
      </v-alert>

      <v-form ref="formRef" @submit.prevent="requestChange">
        <v-text-field
          v-model="newEmail"
          label="Nowy adres e-mail"
          type="email"
          :rules="[rules.required, rules.email]"
        />
        <v-text-field
          v-model="password"
          label="Aktualne hasło"
          type="password"
          :rules="[rules.required]"
          class="mt-2"
          hint="Wymagane do potwierdzenia tożsamości"
          persistent-hint
        />
      </v-form>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn color="primary" :loading="isLoading" @click="requestChange">
        Wyślij prośbę o zmianę
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import api from '@/api';

const formRef = ref<any>(null);
const newEmail = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMessage = ref<string | null>(null);
const successMessage = ref<string | null>(null);

const rules = {
  required: (v: string) => !!v || 'Pole jest wymagane',
  email: (v: string) => /.+@.+\..+/.test(v) || 'Nieprawidłowy format e-mail',
};

async function requestChange() {
  const { valid } = await formRef.value?.validate();
  if (!valid) return;

  isLoading.value = true;
  errorMessage.value = null;
  successMessage.value = null;

  try {
    const response = await api.post('/users/change-email/', {
      new_email: newEmail.value,
      password: password.value,
    });
    successMessage.value = response.data.detail;
    formRef.value?.reset();
  } catch (error: any) {
    errorMessage.value = error.response?.data?.error || error.response?.data?.new_email?.[0] || 'Wystąpił nieoczekiwany błąd.';
  } finally {
    isLoading.value = false;
  }
}
</script>
