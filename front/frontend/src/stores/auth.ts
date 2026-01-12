import { defineStore } from 'pinia';

import api from '@/api';
import router from '@/router';
import type { RegisterCredentials, UserProfile  } from '@/types';

interface AuthState {
  accessToken: string | null;
  user: UserProfile | null;
  error: string | null;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('accessToken') || null,
    user: null,
    error: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isActivated: (state) => !!state.user?.technician_profile,
    isAdmin: (state) => state.user?.technician_profile?.is_admin || false,
  },
  actions: {
    setUser(user: UserProfile) {
      this.user = user;
    },
    async fetchUser() {
      if (!this.accessToken) return;
      try {
        const response = await api.get<UserProfile>('/users/me/');
        this.user = response.data;
        console.log('Pobrano profil użytkownika:', this.user);
      } catch (error) {
        console.error("Nie udało się pobrać profilu użytkownika.", error);
      }
    },
    async refreshUserData() {
      console.log('Odświeżanie danych użytkownika...');
      await this.fetchUser();
    },

    async initialize() {
      if (this.accessToken) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
        await this.fetchUser();
      }
    },

    async login(credentials: { username: string; password: string }) {
      this.error = null;
      try {
        const response = await api.post('/token/', credentials);
        const token = response.data.access;

        this.accessToken = token;
        localStorage.setItem('accessToken', token);
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`
        await this.fetchUser();

        await router.push({ name: 'home' });
      } catch (err: any) {
        this.error = 'Nieprawidłowa nazwa użytkownika lub hasło.';
        console.error('Błąd logowania:', err);
        throw this.error;
      }
    },

    async refreshUserStatus() {
      console.log('Odświeżanie statusu użytkownika...');
      await this.fetchUser();
    },

    async register(credentials: RegisterCredentials) {
      this.error = null;
      try {
        await api.post('/register/', credentials);
        await router.push({ name: 'login', query: { registered: 'true' } });
      } catch (err: any) {
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
      this.user= null;
      localStorage.removeItem('accessToken');
      delete api.defaults.headers.common['Authorization'];
      window.location.href = '/login';
    },
    updateUser(userData: UserProfile) {
      this.user = userData;
    },
  },
});
