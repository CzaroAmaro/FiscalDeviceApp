import 'vuetify/styles';
import '@mdi/font/css/materialdesignicons.css';
import "leaflet/dist/leaflet.css";

import * as L from "leaflet";
import { createPinia } from 'pinia';
import { createApp } from 'vue';
import { createI18n, useI18n } from 'vue-i18n';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import { mdi } from 'vuetify/iconsets/mdi';
import { en, pl } from 'vuetify/locale';
import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n';

import { useAuthStore } from '@/stores/auth';

import App from './App.vue';
import enMessages from './i18n/en.json';
import plMessages from './i18n/pl.json';
import router from './router';

window.L = L;

const i18n = createI18n({
  legacy: false,
  locale: 'pl',
  fallbackLocale: 'en',
  messages: {
    pl: { ...plMessages, $vuetify: pl },
    en: { ...enMessages, $vuetify: en },
  },
});

const vuetify = createVuetify({
  components,
  directives,
  locale: {
    adapter: createVueI18nAdapter({ i18n, useI18n }),
  },
  icons: {
    defaultSet: 'mdi',
    sets: { mdi },
  },
  theme: {
    defaultTheme: localStorage.getItem('user-theme') || 'light',
  },
});

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);

const authStore = useAuthStore();
authStore.initialize();

app.use(router);
app.use(vuetify);
app.use(i18n);

app.mount('#app');

