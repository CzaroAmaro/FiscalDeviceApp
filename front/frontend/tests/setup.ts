// tests/setup.ts
import { config } from '@vue/test-utils';
import { vi } from 'vitest';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

// Tworzymy globalną instancję Vuetify dla wszystkich testów
const vuetify = createVuetify({
  components,
  directives,
});

// Ustawiamy, aby każdy montowany komponent miał dostęp do Vuetify
config.global.plugins = [vuetify];

// Globalny mock dla i18n, żeby nie musieć go mockować w każdym pliku
config.global.mocks = {
  t: (key: string) => key, // Prosty mock, który zwraca klucz
};

// Możesz tu dodać inne globalne mocki, np. dla routera
vi.mock('vue-router', () => ({
  useRoute: vi.fn(),
  useRouter: vi.fn(() => ({
    push: () => {},
  })),
}));
