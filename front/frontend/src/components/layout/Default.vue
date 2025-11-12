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
        <v-container v-if="showActivationBanner" fluid class="pa-0">
          <v-alert type="warning" variant="tonal" prominent tile class="ma-0">
            <div class="d-flex align-center justify-space-between flex-wrap">
              <div>
                <h3 class="mb-1">Twoje konto nie jest aktywne</h3>
                <p>Aby uzyskać pełny dostęp do wszystkich funkcji aplikacji, kup lub aktywuj swoją licencję.</p>
              </div>
              <v-btn
                color="warning"
                variant="flat"
                :loading="paymentStore.isPurchasing"
                :disabled="paymentStore.isPurchasing"
                @click="paymentStore.startPurchase"
              >
                Kup teraz
              </v-btn>
              <v-btn
                color="warning"
                variant="flat"
                :to="{ name: 'redeem-code' }"
              >
                Aktywuj teraz
              </v-btn>
            </div>
          </v-alert>
        </v-container>
        <v-container fluid>
          <RouterView />
        </v-container>
      </v-main>
    </v-layout>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { RouterView } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { usePaymentStore } from '@/stores/payment';

import MainMenu from '@/components/menu/MainMenu.vue';
import UserMenu from '@/components/user/UserMenu.vue';

import { getMenuItems } from '@/config/menuItems';

const { t } = useI18n();
const authStore = useAuthStore();
const paymentStore = usePaymentStore();

const showActivationBanner = computed(() => {
  return authStore.isAuthenticated && !authStore.isActivated;
})

const isMenuMini = ref(false);

const menuItems = computed(() => getMenuItems(t));

const handleLogout = () => {
  authStore.logout();
};
</script>
