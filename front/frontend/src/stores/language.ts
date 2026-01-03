import { defineStore } from 'pinia'
import { ref } from 'vue'

import { i18n } from '@/i18n'

export type Language = 'pl' | 'en'

const STORAGE_KEY = 'user-locale'
const SUPPORTED_LANGUAGES: Language[] = ['pl', 'en']

export const useLanguageStore = defineStore('language', () => {
  const currentLanguage = ref<Language>(i18n.global.locale.value as Language)

  function setLanguage(lang: Language) {
    if (!SUPPORTED_LANGUAGES.includes(lang)) return

    currentLanguage.value = lang
    i18n.global.locale.value = lang

    localStorage.setItem(STORAGE_KEY, lang)
    document.documentElement.lang = lang
  }

  function initLanguage() {
    const saved = localStorage.getItem(STORAGE_KEY) as Language | null
    if (saved && SUPPORTED_LANGUAGES.includes(saved)) {
      setLanguage(saved)
      return
    }

    const browserLang = navigator.language.substring(0, 2) as Language
    setLanguage(SUPPORTED_LANGUAGES.includes(browserLang) ? browserLang : 'pl')
  }

  return {
    currentLanguage,
    setLanguage,
    initLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
  }
})
