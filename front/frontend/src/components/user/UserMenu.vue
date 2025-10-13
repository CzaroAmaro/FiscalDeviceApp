<template>
  <v-card min-width="250" elevation="2">
    <v-list density="compact">
      <v-list-item lines="two" class="px-4 pt-2 pb-3">
        <template v-slot:prepend>
          <v-avatar color="primary" icon="mdi-account-circle"></v-avatar>
        </template>
        <v-list-item-title class="font-weight-bold">
          Jan Kowalski
        </v-list-item-title>
        <v-list-item-subtitle>
          jan.kowalski@example.com
        </v-list-item-subtitle>
      </v-list-item>

      <v-divider></v-divider>

      <v-list-group value="Preferences">
        <template v-slot:activator="{ props }">
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

        <v-list-item
          :title="t('userMenu.theme')"
          prepend-icon="mdi-theme-light-dark"
          value="theme"
          disabled
        ></v-list-item>
      </v-list-group>

      <v-divider/>

      <v-list-item
        :title="t('userMenu.logout')"
        prepend-icon="mdi-logout"
        @click="onLogout"
        class="text-error"
      ></v-list-item>
    </v-list>
  </v-card>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import LanguageSelect from "@/components/languageSelect/LanguageSelect.vue";

const { t } = useI18n();

const emit = defineEmits<{ (e: 'logout'): void }>();

const onLogout = () => {
  emit('logout');
};
</script>
