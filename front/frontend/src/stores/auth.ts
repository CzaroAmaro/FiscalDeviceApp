import { defineStore } from 'pinia'

import api from '@/api'
import router from '@/router'

interface AuthState {
  accessToken: string | null
}

interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    accessToken: localStorage.getItem('accessToken') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    // Action to initialize the store and set the auth header on app load
    initialize() {
      if (this.accessToken) {
        api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
      }
    },

    async login(credentials: { username: string; password: string }) {
      try {
        const response = await api.post('/login/', credentials)
        const token = response.data.access

        this.accessToken = token
        localStorage.setItem('accessToken', token)
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        await router.push({ name: 'home' })
      } catch (error) {
        console.error('Błąd logowania:', error)
        alert('Nieprawidłowa nazwa użytkownika lub hasło.')
        throw error
      }
    },
    async register(credentials: RegisterCredentials) {
      try {
        // Wysyłamy żądanie POST do endpointu, który przygotowałeś w Django
        await api.post('/register/', credentials)

        // Po udanej rejestracji, przekierowujemy użytkownika na stronę logowania
        // Można też wyświetlić powiadomienie o sukcesie (np. "Konto utworzone!")
        await router.push({ name: 'login' })
      } catch (error) {
        console.error('Błąd podczas rejestracji:', error)
        // Rzucamy błąd dalej, aby komponent RegisterView.vue
        // mógł go przechwycić i wyświetlić użytkownikowi
        throw error
      }
    },

    logout() {
      this.accessToken = null
      localStorage.removeItem('accessToken')
      delete api.defaults.headers.common['Authorization']

      // Redirect to login and then reload to ensure a clean state
      router.push({ name: 'login' })
    },
  }
})
