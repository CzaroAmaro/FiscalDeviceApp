import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  test: {
    globals: true,
    environment: 'happy-dom',
    setupFiles: ['tests/setup.ts'],
    css: true, // Włącz przetwarzanie CSS
    server: {
      deps: {
        // Ta opcja mówi Vitest, aby nie próbował rozwiązywać zależności
        // wewnątrz Vuetify, co rozwiązuje problem z CSS.
        inline: ['vuetify'],
      },
    },
  },
})
