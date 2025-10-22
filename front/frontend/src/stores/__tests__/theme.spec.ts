import { createPinia,setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useTheme } from 'vuetify'

import { useThemeStore } from '../theme'

vi.mock('vuetify', () => ({
  useTheme: vi.fn().mockReturnValue({
    global: {
      name: { value: 'light' },
      current: { value: { dark: false } },
    },
  }),
}));

describe('Theme Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  });

  it('should toggle theme from light to dark', () => {
    // Arrange
    const themeStore = useThemeStore()
    const vuetifyTheme = useTheme()

    // Act
    themeStore.toggleTheme()

    // Assert
    expect(vuetifyTheme.global.name.value).toBe('dark')
  });

  it('should set a specific theme', () => {
    // Arrange
    const themeStore = useThemeStore()
    const vuetifyTheme = useTheme()

    // Act
    themeStore.setTheme('dark')

    // Assert
    expect(vuetifyTheme.global.name.value).toBe('dark')

    // Act 2
    themeStore.setTheme('light')

    // Assert 2
    expect(vuetifyTheme.global.name.value).toBe('light')
  })
})
