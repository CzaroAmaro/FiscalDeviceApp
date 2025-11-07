<template>
  <v-card min-width="250" elevation="2">
    <v-list density="compact">
      <v-list-item lines="two" class="px-4 pt-2 pb-3">
        <template #prepend>
          <v-avatar color="primary" icon="mdi-account-circle"></v-avatar>
        </template>
        <v-list-item-title class="font-weight-bold">
          {{ displayName }}
        </v-list-item-title>
        <v-list-item-subtitle>
          {{ userEmail }}
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider></v-divider>

      <v-list-item
        v-if="!authStore.isActivated"
        prepend-icon="mdi-credit-card-outline"
        title="Kup licencję"
        subtitle="Odblokuj pełny dostęp"
        class="text-primary"
        :loading="isPurchasing"
        :disabled="isPurchasing"
        @click="startPurchase"
      ></v-list-item>

      <v-divider></v-divider>

      <v-list-group value="Preferences">
        <template #activator="{ props }">
          <v-list-item
            v-bind="props"
            :title="t('userMenu.preferences')"
            prepend-icon="mdi-cog-outline"
            @click.stop
          ></v-list-item>
        </template>

        <v-list-item @click.stop>
          <v-list-item-title class="text-caption text-medium-emphasis mb-1">
            {{ t('userMenu.language') }}
          </v-list-item-title>
          <LanguageSelect />
        </v-list-item>

        <v-list-item @click.stop>
          <v-switch
            v-model="isDarkMode"
            :label="t('userMenu.theme')"
            color="primary"
            inset
            hide-details
            @change="themeStore.toggleTheme"
          ></v-switch>
        </v-list-item>
      </v-list-group>

      <v-divider/>
      <v-list-item
        prepend-icon="mdi-cog-outline"
        title="Ustawienia"
        :to="{ name: 'settings' }"
      ></v-list-item>

      <v-list-item
        prepend-icon="mdi-credit-card-outline"
        title="Kup licencję"
        @click="startPurchase"
      ></v-list-item>
      <v-divider/>

      <v-list-item
        :title="t('userMenu.logout')"
        prepend-icon="mdi-logout"
        class="text-error"
        @click="onLogout"
      ></v-list-item>
    </v-list>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import LanguageSelect from "@/components/languageSelect/LanguageSelect.vue"
import { useThemeStore } from '@/stores/theme'
import { createCheckoutSession } from '@/api/payments.ts'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'
import { usePaymentStore } from '@/stores/payment'


const emit = defineEmits<{ (e: 'logout'): void }>()

const { t } = useI18n()
const themeStore = useThemeStore()
const paymentStore = usePaymentStore();

const authStore = useAuthStore();
const companyStore = useCompanyStore();

const displayName = computed(() => {
  if (authStore.isActivated) {
    // Jeśli konto jest aktywne, pokaż nazwę firmy
    return companyStore.companyName;
  }
  // Jeśli nie, pokaż nazwę użytkownika
  return authStore.user?.username || 'Użytkownik';
});

const userEmail = computed(() => {
  return authStore.user?.email || 'Brak e-maila';
});


const isPurchasing = ref(false);
const startPurchase = async () => {
  isPurchasing.value = true;
  try {
    const response = await createCheckoutSession();
    if (response.url) {
      window.location.href = response.url;
    } else {
      console.error("Błąd: Nie otrzymano adresu URL od Stripe.", response.error);
    }
  } catch (error) {
    console.error("Nie udało się zainicjować płatności:", error);
  } finally {
    isPurchasing.value = false;
  }
}

const isDarkMode = computed({
  get: () => themeStore.currentThemeName === 'dark',
  set: () => themeStore.toggleTheme(),
})

const onLogout = () => {
  emit('logout')
}

onMounted(() => {
  if (authStore.isActivated) {
    companyStore.fetchCompanyName();
  }
});
</script>
