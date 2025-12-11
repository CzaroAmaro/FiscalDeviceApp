<template>
  <v-card>
    <v-card-title>Dane osobowe</v-card-title>
    <v-card-text>
      <v-form ref="formRef" @submit.prevent="saveProfile">
        <v-text-field
          v-model="form.first_name"
          label="Imię"
          variant="outlined"
          class="mb-3"
        ></v-text-field>
        <v-text-field
          v-model="form.last_name"
          label="Nazwisko"
          variant="outlined"
          class="mb-3"
        ></v-text-field>
        <v-btn
          type="submit"
          color="primary"
          :loading="isSaving"
          :disabled="isSaving"
        >
          Zapisz dane
        </v-btn>
      </v-form>
    </v-card-text>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-card>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import api from '@/api';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const isSaving = ref(false);

const form = reactive({
  first_name: '',
  last_name: '',
});

const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
});

onMounted(() => {
  // Załaduj aktualne dane z store'a
  if (authStore.user) {
    form.first_name = authStore.user.first_name || '';
    form.last_name = authStore.user.last_name || '';
  }
});

const saveProfile = async () => {
  isSaving.value = true;
  try {
    const response = await api.patch('/users/profile/', {
      first_name: form.first_name,
      last_name: form.last_name,
    });

    // Zaktualizuj dane użytkownika w store
    authStore.updateUser(response.data);

    snackbar.text = 'Dane zostały zaktualizowane!';
    snackbar.color = 'success';
    snackbar.show = true;
  } catch (err) {
    snackbar.text = 'Wystąpił błąd podczas zapisywania.';
    snackbar.color = 'error';
    snackbar.show = true;
    console.error(err);
  } finally {
    isSaving.value = false;
  }
};
</script>
