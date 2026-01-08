<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="550" class="text-center pa-6">
      <div v-if="isLoading">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4 text-body-1">{{ $t('payment.success.verifying') }}</p>
      </div>

      <div v-else-if="error">
        <v-icon size="64" color="error" class="mb-4">mdi-close-circle-outline</v-icon>
        <v-card-title class="text-h5 text-error">{{ $t('common.errors.unknown') }}</v-card-title>
        <v-card-text class="text-body-1">{{ error }}</v-card-text>
        <v-card-actions class="justify-center">
          <v-btn color="primary" :to="{ name: 'home' }">{{ $t('payment.success.backToDashboard') }}</v-btn>
        </v-card-actions>
      </div>

      <div v-else-if="activationCode">
        <v-icon size="64" color="success" class="mb-4">mdi-check-decagram</v-icon>
        <v-card-title class="text-h5 text-success">{{ $t('payment.success.title') }}</v-card-title>

        <v-card-text class="text-body-1">
          {{ $t('payment.success.message') }}
        </v-card-text>

        <div class="my-5">
          <v-chip
            size="x-large"
            color="primary"
            label
            class="font-weight-bold text-h6 px-6"
          >
            {{ activationCode }}
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
            {{ $t('payment.success.emailSent.title') }}
          </v-alert-title>
          <div class="text-body-2 mt-1">
            {{ $t('payment.success.emailSent.message', { email: emailSentTo }) }}
          </div>
          <div class="text-caption text-medium-emphasis mt-2">
            {{ $t('payment.success.emailSent.hint') }}
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
            {{ $t('payment.success.goToActivation') }}
          </v-btn>
        </v-card-actions>
      </div>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { handlePaymentSuccess } from '@/api/payments';

const { t } = useI18n();
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
    console.error('Failed to copy code:', err);
  }
};

onMounted(async () => {
  const sessionId = route.query.session_id as string;
  if (!sessionId) {
    error.value = t('payment.success.noSessionId');
    isLoading.value = false;
    return;
  }

  try {
    const response = await handlePaymentSuccess(sessionId);
    if (response.code) {
      activationCode.value = response.code;
      emailSentTo.value = response.email_sent_to || null;
    } else {
      error.value = response.error || t('payment.success.fetchError');
    }
  } catch (err) {
    error.value = t('payment.success.serverError');
  } finally {
    isLoading.value = false;
  }
});
</script>
