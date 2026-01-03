import { createI18n } from 'vue-i18n'
import { en, pl } from 'vuetify/locale'

import enMessages from './en.json'
import plMessages from './pl.json'

export const i18n = createI18n({
  legacy: false,
  locale: 'pl',
  fallbackLocale: 'en',
  messages: {
    pl: { ...plMessages, $vuetify: pl },
    en: { ...enMessages, $vuetify: en },
  },
})
