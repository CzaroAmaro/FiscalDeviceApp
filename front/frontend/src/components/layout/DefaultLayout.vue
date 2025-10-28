<template>
  <v-navigation-drawer
    v-model="drawer"
    color="grey-darken-3"
    permanent
    :rail="isRail"
  >
    <!-- Nowy, modularny nagłówek menu -->
    <MainMenuHeader v-model:rail="isRail" />

    <!-- Nowy, modularny kontener na elementy menu -->
    <MenuItems :items="translatedMenuItems" :rail="isRail" />
  </v-navigation-drawer>

  <v-app-bar color="primary">

    <v-toolbar-title>{{ t('app.title') }}</v-toolbar-title>

    <v-spacer></v-spacer>

    <!-- Menu użytkownika bez zmian -->
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
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { getMenuItems } from '@/config/menuItems';

// Import nowych, modularnych komponentów menu
import MainMenuHeader from '@/components/menu/MainMenuHeader.vue';
import MenuItems from '@/components/menu/MainMenuItems.vue';
import UserMenu from '@/components/user/UserMenu.vue';

const { t } = useI18n();
const authStore = useAuthStore();

// Stan zwinięcia menu jest zarządzany centralnie w layoucie
const isRail = ref(localStorage.getItem('menu-railed') === 'true');

// Stan otwarcia szuflady (istotny głównie na mobile)
const drawer = ref(true);

const translatedMenuItems = computed(() => getMenuItems(t));

const handleLogout = () => {
  authStore.logout();
};

</script>
