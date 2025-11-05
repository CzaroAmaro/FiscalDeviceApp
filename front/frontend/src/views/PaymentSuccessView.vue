<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="500" class="text-center pa-5">
      <div v-if="isLoading">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4">Weryfikowanie płatności i generowanie kodu...</p>
      </div>

      <div v-else-if="error">
        <v-icon size="64" color="error" class="mb-4">mdi-close-circle-outline</v-icon>
        <v-card-title class="text-h5 text-error">Wystąpił błąd</v-card-title>
        <v-card-text>{{ error }}</v-card-text>
        <v-card-actions class="justify-center">
          <v-btn color="primary" :to="{ name: 'home' }">Wróć do strony głównej</v-btn>
        </v-card-actions>
      </div>

      <div v-else-if="activationCode">
        <v-icon size="64" color="success" class="mb-4">mdi-check-decagram</v-icon>
        <v-card-title class="text-h5 text-success">Płatność zakończona sukcesem!</v-card-title>
        <v-card-text>
          Oto Twój unikalny kod aktywacyjny. Skopiuj go i użyj na stronie aktywacji, aby odblokować pełny dostęp do aplikacji.
        </v-card-text>

        <v-chip
          class="my-4"
          size="x-large"
          color="primary"
          label
        >
          {{ activationCode }}
        </v-chip>

        <v-card-actions class="justify-center">
          <v-btn variant="tonal" @click="copyCode">Skopiuj kod</v-btn>
          <v-btn color="primary" :to="{ name: 'redeem-code' }">Przejdź do aktywacji</v-btn>
        </v-card-actions>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { handlePaymentSuccess } from '@/api/payments'; // Upewnij się, że ta ścieżka jest poprawna

const route = useRoute();
const isLoading = ref(true);
const activationCode = ref<string | null>(null);
const error = ref<string | null>(null);

onMounted(async () => {
  const sessionId = route.query.session_id as string;
  if (!sessionId) {
    error.value = 'Brak identyfikatora sesji płatności w adresie URL.';
    isLoading.value = false;
    return;
  }

  try {
    // Wołamy backend, aby "na szybko" pobrać kod.
    // Webhook działa w tle, ale ten endpoint daje natychmiastowy feedback.
    const response = await handlePaymentSuccess(sessionId);
    if (response.code) {
      activationCode.value = response.code;
    } else {
      error.value = response.error || 'Nie udało się pobrać kodu aktywacyjnego. Sprawdź swoje kody na stronie profilu lub skontaktuj się z pomocą.';
    }
  } catch (err) {
    error.value = 'Wystąpił błąd serwera. Spróbuj ponownie za chwilę.';
  } finally {
    isLoading.value = false;
  }
});

const copyCode = async () => {
  if (activationCode.value) {
    try {
      await navigator.clipboard.writeText(activationCode.value);
      // Możesz dodać tu snackbar z informacją "Skopiowano!"
      console.log('Kod skopiowany do schowka!');
    } catch (err) {
      console.error('Nie udało się skopiować kodu: ', err);
    }
  }
};
</script>
