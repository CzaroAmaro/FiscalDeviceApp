<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <h1>Ustawienia</h1>

        <div v-if="isLoading" class="text-center pa-10">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p class="mt-4">Ładowanie danych...</p>
        </div>

        <v-alert v-else-if="error" type="error" class="mt-4">
          {{ error }}
        </v-alert>

        <div v-else>
          <!-- Company settings - only for admins -->
          <v-card v-if="isAdmin" class="mt-6">
            <v-card-title>Ustawienia Firmy</v-card-title>
            <v-card-text>
              <v-form @submit.prevent="saveCompanySettings">
                <v-text-field
                  v-model="companyData.name"
                  label="Nazwa firmy"
                  variant="outlined"
                  :rules="[rules.required]"
                ></v-text-field>
                <v-btn
                  type="submit"
                  color="primary"
                  :loading="isSavingCompany"
                  :disabled="isSavingCompany"
                >
                  Zapisz zmiany w firmie
                </v-btn>
              </v-form>
            </v-card-text>
          </v-card>

          <!-- Read-only company info for non-admins -->
          <v-card v-else class="mt-6">
            <v-card-title>Informacje o firmie</v-card-title>
            <v-card-text>
              <v-text-field
                v-model="companyData.name"
                label="Nazwa firmy"
                variant="outlined"
                readonly
                disabled
              ></v-text-field>
              <v-alert type="info" density="compact" variant="tonal">
                Tylko administrator może edytować dane firmy.
              </v-alert>
            </v-card-text>
          </v-card>

          <EditProfileForm class="mt-6" />
          <ChangeEmailForm class="mt-6" />
        </div>
      </v-col>
    </v-row>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import api from '@/api';
import { useAuthStore } from '@/stores/auth';
import ChangeEmailForm from '@/components/ChangeEmailForm.vue';
import EditProfileForm from '@/components/EditProfileForm.vue';

interface Company {
  id: string;
  name: string;
}

const authStore = useAuthStore();
const isAdmin = computed(() => authStore.isAdmin);

const isLoading = ref(true);
const isSavingCompany = ref(false);
const error = ref<string | null>(null);

const companyData = reactive<Partial<Company>>({
  name: '',
});

const rules = {
  required: (value: string) => !!value || 'To pole jest wymagane.',
};

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
});

onMounted(async () => {
  try {
    const response = await api.get<Company>('/company/me/');
    Object.assign(companyData, response.data);
  } catch (err) {
    error.value = 'Nie udało się pobrać danych firmy. Upewnij się, że Twoje konto jest aktywne.';
    console.error(err);
  } finally {
    isLoading.value = false;
  }
});

const saveCompanySettings = async () => {
  if (!isAdmin.value) {
    showSnackbar('Brak uprawnień do edycji danych firmy.', 'error');
    return;
  }

  if (!companyData.name) {
    showSnackbar('Nazwa firmy nie może być pusta.', 'error');
    return;
  }

  isSavingCompany.value = true;
  try {
    await api.patch('/company/me/', { name: companyData.name });
    showSnackbar('Dane firmy zostały zaktualizowane!', 'success');
  } catch (err) {
    showSnackbar('Wystąpił błąd podczas zapisywania danych.', 'error');
    console.error(err);
  } finally {
    isSavingCompany.value = false;
  }
};

const showSnackbar = (text: string, color: 'success' | 'error' = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
};
</script>
