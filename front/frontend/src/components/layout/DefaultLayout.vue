<template>
  <v-navigation-drawer v-model="drawer" color="grey-darken-3">
    <MainMenu />
  </v-navigation-drawer>

  <v-app-bar color="primary">
    <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
    <v-toolbar-title>Manager Urządzeń Fiskalnych</v-toolbar-title>

    <v-menu location="bottom end" transition="slide-y-transition">
      <!-- 1. Aktywator: to co widać, zanim menu się otworzy -->
      <template v-slot:activator="{ props }">
        <v-btn v-bind="props" icon>
          <v-avatar color="white" size="36">
            <v-icon color="primary">mdi-account-circle</v-icon>
          </v-avatar>
          <v-tooltip activator="parent" location="bottom">Menu użytkownika</v-tooltip>
        </v-btn>
      </template>

      <UserMenu @logout="handleLogout" />
    </v-menu>

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
import { useAuthStore } from '@/stores/auth'

import UserMenu from '@/components/user/UserMenu.vue'
import MainMenu from '@/components/MainMenu.vue'

const authStore = useAuthStore()
const drawer = ref(true)

const handleLogout = () => {
  authStore.logout()
}
</script>
