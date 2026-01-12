<template>
  <v-container class="fill-height">
    <v-row justify="center" align="center">
      <v-col cols="12" sm="8" md="6">
        <v-card class="text-center pa-6">
          <v-icon size="80" color="warning" class="mb-4">
            mdi-lock-alert
          </v-icon>
          <v-card-title class="text-h5">
            Brak uprawnień
          </v-card-title>
          <v-card-text class="text-body-1">
            Nie masz uprawnień do wyświetlenia tej strony.
            Skontaktuj się z administratorem firmy, jeśli uważasz, że to błąd.
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn color="primary" :to="{ name: 'home' }">
              Wróć do strony głównej
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
</script>
