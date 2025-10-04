import { defineStore } from 'pinia'
import api from '@/api' // lub '@/services/api'
import type { FiscalDevice } from '@/types' // Za chwilę tam przeniesiemy interfejs

interface DevicesState {
  devices: FiscalDevice[]
  isLoading: boolean
  error: string | null
}

export const useDevicesStore = defineStore('devices', {
  state: (): DevicesState => ({
    devices: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    // Możemy tu tworzyć przydatne gettery, np. zliczające urządzenia
    deviceCount: (state) => state.devices.length,
    totalDevices: (state): number => {
      return state.devices.length;
    },
  },

  actions: {
    async fetchDevices() {
      this.isLoading = true
      this.error = null
      try {
        const response = await api.get<FiscalDevice[]>('/devices/')
        this.devices = response.data
      } catch (err) {
        console.error('Błąd podczas pobierania urządzeń:', err)
        this.error = 'Nie udało się załadować danych. Spróbuj ponownie później.'
        this.devices = []
      } finally {
        this.isLoading = false
      }
    },

    // W przyszłości możesz tu dodać inne akcje
    // async addDevice(deviceData) { ... }
    // async deleteDevice(deviceId) { ... }
  },
})
