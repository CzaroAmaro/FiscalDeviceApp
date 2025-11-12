import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import simpleImportSort from 'eslint-plugin-simple-import-sort';
import vue from 'eslint-plugin-vue';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import vueParser from 'vue-eslint-parser';

export default tseslint.config(
  {
    ignores: [
      'dist/**',
      'dist-ssr/**',
      'node_modules/**',
      'coverage/**',
      '**/*.d.ts',
    ],
  },

  js.configs.recommended,

  ...tseslint.configs.recommended,

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
      'vue/multi-word-component-names': 'off',
      'vue/valid-v-slot': ['error', { allowModifiers: true }],
      'vue/define-macros-order': ['error', { 'order': ['defineProps', 'defineEmits'] }],
      'vue/no-mutating-props': 'error',
    }
  },

  prettier,
);
