import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'
import 'leaflet/dist/leaflet.css'

import * as L from 'leaflet'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import { useI18n } from 'vue-i18n'
import { createVuetify, type ThemeDefinition } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import { createVueI18nAdapter } from 'vuetify/locale/adapters/vue-i18n'

import { i18n } from '@/i18n'
import { useAuthStore } from '@/stores/auth'
import { useLanguageStore } from '@/stores/language'

import App from './App.vue'
import router from './router'

window.L = L

const getSavedTheme = (): 'light' | 'dark' => {
  const saved = localStorage.getItem('user-theme')
  if (saved === 'light' || saved === 'dark') return saved
  if (window.matchMedia?.('(prefers-color-scheme: dark)').matches) return 'dark'
  return 'light'
}

const savedTheme = getSavedTheme()

const lightTheme: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#E8EAF6',
    surface: '#FFFFFF',
    'surface-bright': '#FFFFFF',
    'surface-light': '#F5F5F5',
    'surface-variant': '#E0E0E0',
    'on-surface': '#212121',
    'on-background': '#212121',
    primary: '#1976D2',
    'primary-darken-1': '#1565C0',
    secondary: '#546E7A',
    'secondary-darken-1': '#455A64',
    error: '#D32F2F',
    info: '#1976D2',
    success: '#388E3C',
    warning: '#F57C00',
  },
}

const darkTheme: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#121212',
    surface: '#1E1E1E',
    'surface-bright': '#2D2D2D',
    'surface-light': '#383838',
    'surface-variant': '#424242',
    'on-surface': '#EEEEEE',
    'on-background': '#EEEEEE',
    primary: '#2196F3',
    'primary-darken-1': '#1E88E5',
    secondary: '#03DAC6',
    'secondary-darken-1': '#00BFA5',
    error: '#CF6679',
    info: '#2196F3',
    success: '#4CAF50',
    warning: '#FB8C00',
  },
}

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
    defaultTheme: savedTheme,
    themes: {
      light: lightTheme,
      dark: darkTheme,
    },
  },
  defaults: {
    VCard: { elevation: 2 },
  },
})

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

const authStore = useAuthStore()
authStore.initialize()

app.use(i18n)

const languageStore = useLanguageStore()
languageStore.initLanguage()

app.use(router)
app.use(vuetify)

app.mount('#app')
