import { defineStore } from 'pinia'

import api from '@/api'
import type { FiscalDevice } from '@/types'

type DevicePayload = Pick<FiscalDevice,
  'brand' |
  'model_name' |
  'unique_number' |
  'serial_number' |
  'sale_date' |
  'last_service_date' |
  'operating_instructions' |
  'remarks' |
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
        return response.data;
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
