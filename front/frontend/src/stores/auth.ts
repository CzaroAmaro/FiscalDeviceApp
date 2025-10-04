import { defineStore } from 'pinia'
import api from '@/api'
import router from '@/router'

interface AuthState {
  accessToken: string | null
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

    logout() {
      this.accessToken = null
      localStorage.removeItem('accessToken')
      delete api.defaults.headers.common['Authorization']

      // Redirect to login and then reload to ensure a clean state
      router.push({ name: 'login' })
    },
  }
})
