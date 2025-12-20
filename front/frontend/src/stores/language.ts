import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'

export type Language = 'pl' | 'en'

const STORAGE_KEY = 'user-locale'
const SUPPORTED_LANGUAGES: Language[] = ['pl', 'en']

export const useLanguageStore = defineStore('language', () => {
  const { locale } = useI18n()

  const currentLanguage = ref<Language>(locale.value as Language)

  function setLanguage(lang: Language) {
    if (!SUPPORTED_LANGUAGES.includes(lang)) {
      console.warn(`Unsupported language: ${lang}`)
      return
    }
    currentLanguage.value = lang
    locale.value = lang
    localStorage.setItem(STORAGE_KEY, lang)

    document.documentElement.lang = lang
  }

  function initLanguage() {
    const saved = localStorage.getItem(STORAGE_KEY) as Language | null

    if (saved && SUPPORTED_LANGUAGES.includes(saved)) {
      setLanguage(saved)
    } else {
      const browserLang = navigator.language.substring(0, 2) as Language
      const detectedLang = SUPPORTED_LANGUAGES.includes(browserLang) ? browserLang : 'pl'
      setLanguage(detectedLang)
    }
  }

  watch(locale, (newLocale) => {
    currentLanguage.value = newLocale as Language
  })

  return {
    currentLanguage,
    setLanguage,
    initLanguage,
    supportedLanguages: SUPPORTED_LANGUAGES,
  }
})
