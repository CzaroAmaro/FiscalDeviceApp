<template>
  <v-app>
    <v-layout>
      <MainMenu v-model:mini="isMenuMini" :items="menuItems" />

      <v-app-bar color="primary">
        <v-toolbar-title>{{ t('app.title') }}</v-toolbar-title>
        <v-spacer></v-spacer>
        <v-menu location="bottom end" transition="slide-y-transition">
          <template #activator="{ props }">
            <v-btn v-bind="props" icon>
              <v-avatar color="white" size="36">
                <v-icon color="primary">mdi-account-circle</v-icon>
              </v-avatar>
              <v-tooltip activator="parent" location="bottom">{{ t('toolbar.userMenu') }}</v-tooltip>
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
    </v-layout>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'; // ref i computed są potrzebne
import { useI18n } from 'vue-i18n';
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

import MainMenu from '@/components/menu/MainMenu.vue';
import UserMenu from '@/components/user/UserMenu.vue';

import { getMenuItems } from '@/config/menuItems';

const { t } = useI18n();
const authStore = useAuthStore();

// Prostsza definicja stanu menu, bez zapisu do localStorage
const isMenuMini = ref(false); // Domyślnie menu jest rozwinięte

// Pobieramy menu z zewnętrznego pliku, tak jak chciałeś.
// Ta właściwość będzie automatycznie przeliczona, gdy zmieni się język.
const menuItems = computed(() => getMenuItems(t));

const handleLogout = () => {
  authStore.logout();
};
</script>
