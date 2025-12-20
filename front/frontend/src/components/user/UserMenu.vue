<template>
  <v-card min-width="280" elevation="3" rounded="lg">
    <v-list density="compact" class="py-0">
      <v-list-item lines="two" class="px-4 py-3">
        <template #prepend>
          <v-avatar color="primary" size="42">
            <v-icon icon="mdi-account-circle" size="24"></v-icon>
          </v-avatar>
        </template>
        <v-list-item-title class="font-weight-bold">
          {{ displayName }}
        </v-list-item-title>
        <v-list-item-subtitle class="text-caption">
          {{ userEmail }}
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider />

      <v-list-item class="px-4 py-2" @click.stop>
        <template #prepend>
          <v-icon
            :icon="authStore.isActivated ? 'mdi-shield-check' : 'mdi-shield-alert'"
            :color="authStore.isActivated ? 'success' : 'warning'"
            size="20"
          />
        </template>
        <v-list-item-title class="text-body-2">
          {{ authStore.isActivated ? t('userMenu.license.active') : t('userMenu.license.demo') }}
        </v-list-item-title>
        <template #append>
          <v-btn
            v-if="!authStore.isActivated"
            size="x-small"
            color="primary"
            variant="tonal"
            :loading="isPurchasing"
            @click.stop="startPurchase"
          >
            {{ t('userMenu.license.activate') }}
          </v-btn>
          <v-icon v-else icon="mdi-check" color="success" size="18" />
        </template>
      </v-list-item>

      <v-divider />

      <div class="px-4 py-3" @click.stop>
        <div class="text-caption text-medium-emphasis mb-3 font-weight-medium">
          {{ t('userMenu.preferences') }}
        </div>

        <div class="d-flex align-center justify-space-between mb-3">
          <div class="d-flex align-center">
            <v-icon
              :icon="themeStore.isDark ? 'mdi-weather-night' : 'mdi-white-balance-sunny'"
              size="20"
              class="mr-3"
              :color="themeStore.isDark ? 'blue-lighten-2' : 'orange'"
            />
            <span class="text-body-2">{{ t('userMenu.theme') }}</span>
          </div>
          <v-btn-toggle
            :model-value="themeStore.currentThemeName"
            mandatory
            density="compact"
            rounded="pill"
            color="primary"
            class="theme-toggle"
            @update:model-value="handleThemeChange"
          >
            <v-btn size="small" value="light" min-width="40">
              <v-icon size="18">mdi-white-balance-sunny</v-icon>
            </v-btn>
            <v-btn size="small" value="dark" min-width="40">
              <v-icon size="18">mdi-weather-night</v-icon>
            </v-btn>
          </v-btn-toggle>
        </div>

        <div class="d-flex align-center justify-space-between">
          <div class="d-flex align-center">
            <v-icon icon="mdi-translate" size="20" class="mr-3" />
            <span class="text-body-2">{{ t('userMenu.language') }}</span>
          </div>
          <v-btn-toggle
            :model-value="languageStore.currentLanguage"
            mandatory
            density="compact"
            rounded="pill"
            color="primary"
            class="language-toggle"
            @update:model-value="handleLanguageChange"
          >
            <v-btn size="small" value="pl" min-width="44">
              PL
            </v-btn>
            <v-btn size="small" value="en" min-width="44">
              EN
            </v-btn>
          </v-btn-toggle>
        </div>
      </div>

      <v-divider />

      <v-list-item
        prepend-icon="mdi-cog-outline"
        :title="t('userMenu.settings')"
        :to="{ name: 'settings' }"
        class="menu-item"
      />

      <v-divider />

      <v-list-item
        prepend-icon="mdi-logout"
        :title="t('userMenu.logout')"
        class="menu-item text-error"
        @click="onLogout"
      />
    </v-list>
  </v-card>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '@/stores/theme'
import { useLanguageStore, type Language } from '@/stores/language'
import { createCheckoutSession } from '@/api/payments'
import { useAuthStore } from '@/stores/auth'
import { useCompanyStore } from '@/stores/company'

const emit = defineEmits<{ (e: 'logout'): void }>()

const { t } = useI18n()
const themeStore = useThemeStore()
const languageStore = useLanguageStore()
const authStore = useAuthStore()
const companyStore = useCompanyStore()

const displayName = computed(() => {
  if (authStore.isActivated) {
    return companyStore.companyName
  }
  return authStore.user?.username || t('userMenu.defaultUser')
})

const userEmail = computed(() => {
  return authStore.user?.email || t('userMenu.noEmail')
})

const handleThemeChange = (value: 'light' | 'dark') => {
  themeStore.setTheme(value)
}

const handleLanguageChange = (value: Language) => {
  languageStore.setLanguage(value)
}

const isPurchasing = ref(false)

const startPurchase = async () => {
  isPurchasing.value = true
  try {
    const response = await createCheckoutSession()
    if (response.url) {
      window.location.href = response.url
    } else {
      console.error(t('userMenu.errors.noStripeUrl'), response.error)
    }
  } catch (error) {
    console.error(t('userMenu.errors.paymentFailed'), error)
  } finally {
    isPurchasing.value = false
  }
}

const onLogout = () => {
  emit('logout')
}

onMounted(() => {
  if (authStore.isActivated) {
    companyStore.fetchCompanyName()
  }
})
</script>

<style scoped>
.theme-toggle,
.language-toggle {
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}

.theme-toggle :deep(.v-btn),
.language-toggle :deep(.v-btn) {
  font-weight: 500;
}

.menu-item {
  min-height: 44px;
}

.menu-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.08);
}
</style>
