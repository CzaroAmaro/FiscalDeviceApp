<template>
  <v-navigation-drawer v-model="drawer" color="grey-darken-3">
    <v-list>
      <v-list-item
        prepend-icon="mdi-view-dashboard"
        title="Dashboard"
        value="dashboard"
        :to="{ name: 'home' }"
        link
      ></v-list-item>
      <v-list-item
        prepend-icon="mdi-printer-pos"
        title="Urządzenia"
        value="devices"
        :to="{ name: 'devices' }"
        link
      ></v-list-item>
    </v-list>
  </v-navigation-drawer>

  <v-app-bar color="primary">
    <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
    <v-toolbar-title>Manager Urządzeń Fiskalnych</v-toolbar-title>

    <!-- DODANY PRZYCISK WYLOGOWANIA -->
    <v-spacer></v-spacer>
    <v-btn icon @click="handleLogout">
      <v-icon>mdi-logout</v-icon>
      <v-tooltip activator="parent" location="bottom">Wyloguj</v-tooltip>
    </v-btn>
    <!-- KONIEC DODANEGO PRZYCISKU -->

  </v-app-bar>

  <v-main>
    <v-container fluid>
      <RouterView />
    </v-container>
  </v-main>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // Importujemy authStore

const authStore = useAuthStore()
const drawer = ref(true)

const handleLogout = () => {
  authStore.logout() // Wywołujemy akcję wylogowania
}
</script>
