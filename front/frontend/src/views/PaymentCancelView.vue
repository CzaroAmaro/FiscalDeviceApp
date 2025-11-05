<template>
  <v-container class="fill-height d-flex justify-center align-center">
    <v-card width="450" class="text-center pa-5">
      <v-icon size="64" color="warning" class="mb-4">mdi-alert-circle-outline</v-icon>
      <v-card-title class="text-h5">
        Płatność została anulowana
      </v-card-title>
      <v-card-text>
        Twoja transakcja nie została ukończona. Możesz spróbować ponownie w dowolnym momencie.
      </v-card-text>
      <v-card-actions class="justify-center">
        <v-btn color="primary" :to="{ name: 'home' }">
          Wróć do strony głównej
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
</script>
