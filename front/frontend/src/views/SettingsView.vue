<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <h1>Ustawienia</h1>

        <!-- Ładowanie danych -->
        <div v-if="isLoading" class="text-center pa-10">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <p class="mt-4">Ładowanie danych...</p>
        </div>

        <!-- Błąd ładowania -->
        <v-alert v-else-if="error" type="error" class="mt-4">
          {{ error }}
        </v-alert>

        <!-- Formularze -->
        <div v-else>
          <!-- Karta z ustawieniami firmy -->
          <v-card class="mt-6">
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

          <!-- Karta z ustawieniami konta (placeholder) -->
          <v-card class="mt-6">
            <v-card-title>Ustawienia Konta</v-card-title>
            <v-card-text>
              <v-form>
                <v-text-field
                  label="Adres e-mail"
                  variant="outlined"
                  disabled
                  :model-value="currentUserEmail"
                  hint="Zmiana e-maila będzie dostępna wkrótce"
                  persistent-hint
                ></v-text-field>
                <!-- Tutaj w przyszłości dodasz formularz zmiany hasła itp. -->
              </v-form>
            </v-card-text>
          </v-card>
        </div>
      </v-col>
    </v-row>

    <!-- Snackbar do powiadomień -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '@/api'; // Importujemy nasz skonfigurowany klient axios
import { useAuthStore } from '@/stores/auth'; // Aby pobrać dane o użytkowniku

// Typ dla danych firmy
interface Company {
  id: string;
  name: string;
}

// Stan komponentu
const isLoading = ref(true);
const isSavingCompany = ref(false);
const error = ref<string | null>(null);

const companyData = reactive<Partial<Company>>({
  name: '',
});

// Proste reguły walidacji
const rules = {
  required: (value: string) => !!value || 'To pole jest wymagane.',
};

// Snackbar do powiadomień
const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
});

// Pobieranie danych przy ładowaniu komponentu
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

// Zapisywanie ustawień firmy
const saveCompanySettings = async () => {
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

// Funkcja do pokazywania snackbara
const showSnackbar = (text: string, color: 'success' | 'error' = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
};

// Placeholder dla danych użytkownika
// W przyszłości pobierzesz te dane np. z authStore
const authStore = useAuthStore();
const currentUserEmail = ref(authStore.user?.email || 'email@example.com'); // Zmień na prawdziwe dane

</script>
