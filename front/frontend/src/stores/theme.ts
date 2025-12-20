import { defineStore } from 'pinia'
import { computed } from 'vue'
import { useTheme } from 'vuetify'

type ThemeName = 'light' | 'dark'

const STORAGE_KEY = 'user-theme'

export const useThemeStore = defineStore('theme', () => {
  const vuetifyTheme = useTheme()

  const isDark = computed(() => vuetifyTheme.global.current.value.dark)

  const currentThemeName = computed(() => vuetifyTheme.global.name.value as ThemeName)

  function setTheme(theme: ThemeName) {
    vuetifyTheme.global.name.value = theme
    localStorage.setItem(STORAGE_KEY, theme)
  }
  function toggleTheme() {
    const newTheme: ThemeName = isDark.value ? 'light' : 'dark'
    setTheme(newTheme)
  }

  function initTheme() {
    const saved = localStorage.getItem(STORAGE_KEY) as ThemeName | null
    if (saved && (saved === 'light' || saved === 'dark')) {
      setTheme(saved)
    }
  }

  return {
    isDark,
    currentThemeName,
    setTheme,
    toggleTheme,
    initTheme,
  }
})
