<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card max-width="500" width="100%">
      <v-card-title class="text-center">Potwierdzanie zmiany adresu e-mail</v-card-title>
      <v-card-text class="text-center">
        <div v-if="isLoading" class="py-10">
          <v-progress-circular indeterminate size="64" />
          <p class="mt-4">Przetwarzanie...</p>
        </div>
        <v-alert v-if="message" :type="isSuccess ? 'success' : 'error'">
          {{ message }}
        </v-alert>
      </v-card-text>
      <v-card-actions v-if="!isLoading">
        <v-spacer />
        <v-btn color="primary" to="/login">Przejdź do logowania</v-btn>
        <v-spacer />
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const isLoading = ref(true);
const message = ref<string | null>(null);
const isSuccess = ref(false);
const authStore = useAuthStore();

onMounted(async () => {
  const token = route.query.token as string;

  if (!token) {
    message.value = 'Brak tokenu potwierdzającego w linku.';
    isLoading.value = false;
    return;
  }

  try {
    const response = await api.post('/users/change-email-confirm/', { token });
    message.value = response.data.detail;
    isSuccess.value = true;

    if (authStore.isAuthenticated) {
      await authStore.refreshUserData();
    }
  } catch (error: any) {
    message.value = error.response?.data?.error || 'Wystąpił nieoczekiwany błąd.';
    isSuccess.value = false;
  } finally {
    isLoading.value = false;
  }
});
</script>
