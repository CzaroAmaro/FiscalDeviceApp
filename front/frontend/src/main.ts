import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import api from '@/api'
import {useAuthStore} from "@/stores/auth.ts";

import { createI18n } from 'vue-i18n'
import plMessages from './i18n/pl.json'
import enMessages from './i18n/en.json'

import 'vuetify/styles'
import {createVuetify} from "vuetify";
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import {mdi} from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'
import {en, pl} from "vuetify/locale";
import {createVueI18nAdapter} from "vuetify/locale/adapters/vue-i18n";
import {useI18n} from "vue-i18n"

const i18n = createI18n({
  legacy: false,
  locale: 'pl',
  fallbackLocale: 'en',
  messages: {
    pl: {
      ...plMessages,
      $vuetify: pl,
    },
    en: {
      ...enMessages,
      $vuetify: en,
    },
  },
})

const vuetify = createVuetify({
    components,
    directives,
  locale: {
    adapter: createVueI18nAdapter({ i18n, useI18n }),
  },
    icons: {
        defaultSet: 'mdi',
        sets: {
            mdi,
        },
    },
})

const token = localStorage.getItem('accessToken')
if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

const authStore = useAuthStore()
authStore.initialize()

app.mount('#app')
