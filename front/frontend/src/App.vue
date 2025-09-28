<template>
  <v-app>
    <v-layout>
      <!-- Jeśli strona NIE jest publiczna, wyświetl domyślny layout -->
      <DefaultLayout v-if="!isPublicRoute" />

      <!-- W przeciwnym razie (dla stron publicznych jak /login)
           po prostu renderuj widok bez dodatkowego layoutu -->
      <RouterView v-else />
    </v-layout>
  </v-app>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'

const route = useRoute()

const isPublicRoute = computed(() => route.meta.isPublic)
</script>
