import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import simpleImportSort from 'eslint-plugin-simple-import-sort';
import vue from 'eslint-plugin-vue';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import vueParser from 'vue-eslint-parser';

// Używamy funkcji pomocniczej tseslint.config(), która poprawnie łączy wszystkie konfiguracje
export default tseslint.config(
  // Blok ignorowanych plików
  {
    ignores: [
      'dist/**',
      'dist-ssr/**',
      'node_modules/**',
      'coverage/**',
      '**/*.d.ts',
    ],
  },

  // Podstawowe reguły dla JS
  js.configs.recommended,

  // Konfiguracja dla TypeScript (teraz przekazywana jako argument)
  ...tseslint.configs.recommended,

  // Konfiguracja dla Vue.js
  // KLUCZOWA ZMIANA: Musimy ją rozpakować do głównej tablicy
  ...vue.configs['flat/recommended'],

  // Nasz niestandardowy blok reguł dla plików .ts i .js
  {
    files: ['**/*.{js,mjs,cjs,ts,mts,cts}'],
    plugins: {
      'simple-import-sort': simpleImportSort,
      'vue': vue,
    },
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
      },
    },
    rules: {
      'eqeqeq': ['error', 'always'],
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'simple-import-sort/imports': 'warn',
      'simple-import-sort/exports': 'warn',
    },
  },

  // Nasz niestandardowy blok reguł TYLKO dla plików .vue
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vueParser,
      parserOptions: {
        parser: tseslint.parser,
        sourceType: 'module',
      },
      globals: {
        ...globals.browser,
      },
    },
    rules: {
      // Reguły, które mają sens tylko w plikach .vue
      'vue/multi-word-component-names': 'off',
      'vue/valid-v-slot': ['error', { allowModifiers: true }],
      'vue/define-macros-order': ['error', { 'order': ['defineProps', 'defineEmits'] }],
      'vue/no-mutating-props': 'error',
    }
  },

  // Konfiguracja Prettiera - musi być na samym końcu
  prettier,
);
