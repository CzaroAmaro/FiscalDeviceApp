import { createI18n } from 'vue-i18n'
import { en, pl } from 'vuetify/locale'

import enMessages from './en.json'
import plMessages from './pl.json'

type Lang = 'pl' | 'en'
const STORAGE_KEY = 'user-locale'

const getSavedLanguage = (): Lang => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'pl' || saved === 'en') return saved

    const browserLang = navigator.language?.substring(0, 2)
    return browserLang === 'en' ? 'en' : 'pl'
  } catch {
    return 'pl'
  }
}

export const i18n = createI18n({
  legacy: false,
  locale: getSavedLanguage(),
  fallbackLocale: 'en',
  messages: {
    pl: { ...plMessages, $vuetify: pl },
    en: { ...enMessages, $vuetify: en },
  },
})
