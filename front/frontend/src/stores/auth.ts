import { defineStore } from 'pinia';

import api from '@/api';
import router from '@/router';
import type { RegisterCredentials } from '@/types';

interface AuthState {
  accessToken: string | null;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('accessToken') || null,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },
  actions: {
    initialize() {
      if (this.accessToken) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
      }
    },

    async login(credentials: { username: string; password: string }) {
      this.error = null;
      try {
        const response = await api.post('/login/', credentials);
        const token = response.data.access;

        this.accessToken = token;
        localStorage.setItem('accessToken', token);
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        await router.push({ name: 'home' });
      } catch (err: any) {
        // DOBRA PRAKTYKA: Zamiast alert(), ustawiamy błąd w stanie,
        // aby komponent mógł go wyświetlić w ładniejszy sposób (np. w komponencie VAlert)
        this.error = 'Nieprawidłowa nazwa użytkownika lub hasło.';
        console.error('Błąd logowania:', err);
        throw this.error; // Rzuć błąd dalej, aby komponent wiedział, że operacja się nie powiodła
      }
    },

    async register(credentials: RegisterCredentials) {
      this.error = null;
      try {
        await api.post('/register/', credentials);
        // Po udanej rejestracji, można przekierować na stronę logowania z komunikatem
        await router.push({ name: 'login', query: { registered: 'true' } });
      } catch (err: any) {
        // DOBRA PRAKTYKA: Przechwytujemy błędy walidacji z backendu
        const errors = err.response?.data;
        if (errors) {
          this.error = Object.values(errors).flat().join(' ');
        } else {
          this.error = 'Wystąpił nieoczekiwany błąd podczas rejestracji.';
        }
        console.error('Błąd podczas rejestracji:', err);
        throw this.error;
      }
    },

    logout() {
      this.accessToken = null;
      localStorage.removeItem('accessToken');
      delete api.defaults.headers.common['Authorization'];

      // DOBRA PRAKTYKA: Użycie window.location zapewnia "twarde" przeładowanie
      // i wyczyszczenie stanu wszystkich store'ów, co zapobiega wyciekom danych.
      window.location.href = '/login';
    },
  },
});
