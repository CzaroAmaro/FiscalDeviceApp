import { defineStore } from 'pinia'
import api from '@/api'
import router from '@/router'

interface AuthState {
  accessToken: string | null
  // W przyszłości możemy tu trzymać dane użytkownika
  // user: object | null
}

export const useAuthStore = defineStore('auth', {
  // 1. STATE: Dane, które przechowujemy
  state: (): AuthState => ({
    // Przy starcie aplikacji, próbujemy odczytać token z localStorage.
    // Dzięki temu logowanie przetrwa odświeżenie strony.
    accessToken: localStorage.getItem('accessToken') || null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    async login(credentials: { username: string; password: string }) {
      try {
        const response = await api.post('/login/', credentials)


        const token = response.data.access

        this.accessToken = token

        localStorage.setItem('accessToken', token)

        api.defaults.headers.common['Authorization'] = `Bearer ${token}`

        router.push({ name: 'home' })

      } catch (error) {
        console.error('Błąd logowania:', error)
        alert('Nieprawidłowa nazwa użytkownika lub hasło.');
      }
    },

    logout() {
      this.accessToken = null

      localStorage.removeItem('accessToken')

      delete api.defaults.headers.common['Authorization']

      router.push({ name: 'login' }).then(() => {
        location.reload();
      });
    },
  },
})
