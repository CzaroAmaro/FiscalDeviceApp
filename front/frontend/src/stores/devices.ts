import { defineStore } from 'pinia'
import api from '@/api' // lub '@/services/api'
import type { FiscalDevice } from '@/types'

type DevicePayload = Pick<FiscalDevice,
  'model_name' |
  'serial_number' |
  'production_date' |
  'status' |
  'owner'
>
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
    deviceCount: (state) => state.devices.length,
    totalDevices: (state): number => {
      return state.devices.length
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

    async addDevice(deviceData: DevicePayload) {
      try {
        const response = await api.post<FiscalDevice>('/devices/', deviceData)
        this.devices.unshift(response.data)
      } catch (error) {
        console.error('Błąd dodawania urządzenia:', error)
        throw error
      }
    },

    async updateDevice(deviceId: number, deviceData: DevicePayload) {
      try {
        const response = await api.put<FiscalDevice>(`/devices/${deviceId}/`, deviceData)
        const index = this.devices.findIndex(d => d.id === deviceId)
        if (index !== -1) {
          this.devices[index] = response.data
        }
      } catch (error) {
        console.error('Błąd aktualizacji urządzenia:', error)
        throw error
      }
    },

    async deleteDevice(deviceId: number) {
      try {
        await api.delete(`/devices/${deviceId}/`)
        this.devices = this.devices.filter(d => d.id !== deviceId)
      } catch (error) {
        console.error('Błąd usuwania urządzenia:', error)
        throw error
      }
    },
  },
})
