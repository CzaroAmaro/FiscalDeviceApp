
<template>
  <v-navigation-drawer
    v-model="drawer"
    color="grey-darken-3"
    permanent
    :rail="isRail"
  >
    <!-- Twoje istniejące menu idealnie tu pasuje -->
    <MainMenu />
  </v-navigation-drawer>

  <v-app-bar color="primary">
    <v-app-bar-nav-icon @click="toggleDrawer"></v-app-bar-nav-icon>

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
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useDisplay } from 'vuetify';
import { useI18n } from 'vue-i18n';
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

import MainMenu from '@/components/MainMenu.vue';
import UserMenu from '@/components/user/UserMenu.vue';

const { t } = useI18n();
const authStore = useAuthStore();

const { mobile } = useDisplay();

const drawer = ref(true);

const isRail = ref(false);

const toggleDrawer = () => {
  if (mobile.value) {
    drawer.value = !drawer.value;
  } else {
    isRail.value = !isRail.value;
  }
};

const handleLogout = () => {
  authStore.logout();
};
</script>
