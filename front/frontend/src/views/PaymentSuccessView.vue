<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="550" class="text-center pa-6">
      <div v-if="isLoading">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4 text-body-1">Weryfikowanie płatności i generowanie kodu...</p>
      </div>

      <div v-else-if="error">
        <v-icon size="64" color="error" class="mb-4">mdi-close-circle-outline</v-icon>
        <v-card-title class="text-h5 text-error">Wystąpił błąd</v-card-title>
        <v-card-text class="text-body-1">{{ error }}</v-card-text>
        <v-card-actions class="justify-center">
          <v-btn color="primary" :to="{ name: 'home' }">Wróć do strony głównej</v-btn>
        </v-card-actions>
      </div>

      <div v-else-if="activationCode">
        <v-icon size="64" color="success" class="mb-4">mdi-check-decagram</v-icon>
        <v-card-title class="text-h5 text-success">Płatność zakończona sukcesem!</v-card-title>

        <v-card-text class="text-body-1">
          Oto Twój unikalny kod aktywacyjny. Skopiuj go i użyj na stronie aktywacji,
          aby odblokować pełny dostęp do aplikacji.
        </v-card-text>

        <div class="my-5">
          <v-chip
            size="x-large"
            color="primary"
            label
            class="font-weight-bold text-h6 px-6"
          >
            {{ activationCode }}
            <template #append>
              <v-btn
                icon
                size="small"
                variant="text"
                color="white"
                class="ml-2"
                @click="copyCode"
              >
                <v-icon>{{ copied ? 'mdi-check' : 'mdi-content-copy' }}</v-icon>
                <v-tooltip activator="parent" location="top">
                  {{ copied ? 'Skopiowano!' : 'Kopiuj kod' }}
                </v-tooltip>
              </v-btn>
            </template>
          </v-chip>
        </div>

        <v-alert
          v-if="emailSentTo"
          type="info"
          variant="tonal"
          class="text-left mb-4"
          icon="mdi-email-check-outline"
        >
          <v-alert-title class="text-subtitle-1 font-weight-medium">
            Wiadomość email została wysłana
          </v-alert-title>
          <div class="text-body-2 mt-1">
            Kod aktywacyjny został również wysłany na adres:
            <strong>{{ emailSentTo }}</strong>
          </div>
          <div class="text-caption text-medium-emphasis mt-2">
            Sprawdź również folder spam, jeśli wiadomość nie dotarła.
          </div>
        </v-alert>

        <!-- Przycisk przejścia do aktywacji -->
        <v-card-actions class="justify-center pt-2">
          <v-btn
            color="primary"
            size="large"
            :to="{ name: 'redeem-code' }"
            prepend-icon="mdi-key-variant"
          >
            Przejdź do aktywacji
          </v-btn>
        </v-card-actions>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { handlePaymentSuccess } from '@/api/payments';

const route = useRoute();
const isLoading = ref(true);
const activationCode = ref<string | null>(null);
const emailSentTo = ref<string | null>(null);
const error = ref<string | null>(null);
const copied = ref(false);

const copyCode = async () => {
  if (!activationCode.value) return;

  try {
    await navigator.clipboard.writeText(activationCode.value);
    copied.value = true;
    setTimeout(() => {
      copied.value = false;
    }, 2000);
  } catch (err) {
    console.error('Nie udało się skopiować kodu:', err);
  }
};

onMounted(async () => {
  const sessionId = route.query.session_id as string;
  if (!sessionId) {
    error.value = 'Brak identyfikatora sesji płatności w adresie URL.';
    isLoading.value = false;
    return;
  }

  try {
    const response = await handlePaymentSuccess(sessionId);
    if (response.code) {
      activationCode.value = response.code;
      emailSentTo.value = response.email_sent_to || null;
    } else {
      error.value = response.error || 'Nie udało się pobrać kodu aktywacyjnego. Sprawdź swoje kody na stronie profilu lub skontaktuj się z pomocą.';
    }
  } catch (err) {
    error.value = 'Wystąpił błąd serwera. Spróbuj ponownie za chwilę.';
  } finally {
    isLoading.value = false;
  }
});
</script>
