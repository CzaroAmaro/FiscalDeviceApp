<template>
  <v-select
    v-model="language"
    :items="supportedLanguages"
    item-title="label"
    item-value="value"
    hide-details
    variant="outlined"
    density="compact"
    flat
    @update:model-value="changeLanguage"
  />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';

const { locale } = useI18n();

const language = ref(locale.value);

const supportedLanguages = computed(() => [
  { label: 'Polski', value: 'pl' },
  { label: 'English', value: 'en' },
]);

function changeLanguage(newLocale: 'pl' | 'en') {
  locale.value = newLocale;
  localStorage.setItem('user-locale', newLocale);
}
</script>
