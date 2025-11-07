<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="450" class="pa-5">
      <v-card-title class="text-h5 text-center mb-4">Aktywuj swoje konto</v-card-title>
      <v-card-subtitle class="text-center mb-4">
        Wprowadź kod aktywacyjny otrzymany po zakupie.
      </v-card-subtitle>
      <v-card-text>
        <v-form @submit.prevent="handleRedeem">
          <v-alert v-if="error" type="error" density="compact" class="mb-4">
            {{ error }}
          </v-alert>

          <v-text-field
            v-model="code"
            label="Kod aktywacyjny"
            prepend-inner-icon="mdi-key-variant"
            variant="outlined"
            required
          ></v-text-field>

          <v-btn type="submit" color="primary" block class="mt-4" :loading="isLoading">
            Aktywuj
          </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { redeemActivationCode } from '@/api/payments';
import { useAuthStore } from '@/stores/auth'

const router = useRouter();
const code = ref('');
const isLoading = ref(false);
const error = ref<string | null>(null);
const authStore = useAuthStore();

const handleRedeem = async () => {
  if (!code.value) {
    error.value = 'Pole kodu nie może być puste.';
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    await redeemActivationCode(code.value);

    await authStore.refreshUserStatus();

    await router.push({ name: 'home' });
  } catch (e: any) {
    error.value = e.response?.data?.error || 'Wystąpił błąd.';
  } finally {
    isLoading.value = false;
  }
};
</script>
