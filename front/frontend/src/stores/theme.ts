import { defineStore } from 'pinia'
import { useTheme } from 'vuetify'

type ThemeName = 'light' | 'dark';

export const useThemeStore = defineStore('theme', () => {
  const vuetifyTheme = useTheme();

  /**
   * Zmienia globalny motyw aplikacji i zapisuje wybór.
   * @param theme - Nazwa motywu ('light' lub 'dark')
   */
  function setTheme(theme: ThemeName) {
    vuetifyTheme.global.name.value = theme;
    localStorage.setItem('user-theme', theme);
  }

  /**
   * Przełącza między motywem jasnym a ciemnym.
   */
  function toggleTheme() {
    const newTheme = vuetifyTheme.global.current.value.dark ? 'light' : 'dark';
    setTheme(newTheme);
  }

  return {
    setTheme,
    toggleTheme,
    isDark: vuetifyTheme.global.current.value.dark,
    currentThemeName: vuetifyTheme.global.name,
  }
})
