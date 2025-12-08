import { defineStore } from 'pinia';
import { ref } from 'vue';

import api from '@/api';
import { getDevicesForSelect } from '@/api/devices.ts'
import type { DevicePayload,FiscalDevice } from '@/types';

interface DevicesState {
  devices: FiscalDevice[];
  isLoading: boolean;
  error: string | null;
  filteredForSelect: DeviceForSelect[];
  isLoadingForSelect: boolean;
}

interface DeviceForSelect {
  id: number;
  display_name: string;
}

export const useDevicesStore = defineStore('devices', {
  state: (): DevicesState => ({
    devices: [],
    isLoading: false,
    error: null,
    filteredForSelect: [],
    isLoadingForSelect: false,
  }),

  getters: {
    deviceCount: (state) => state.devices.length,
  },

  actions: {
    /**
     * Pobiera listę urządzeń z API.
     * @param {boolean} force - Jeśli true, wymusza ponowne pobranie danych, ignorując pamięć podręczną.
     */
    async fetchDevices(force = false) {
      if (this.devices.length > 0 && !force) {
        return;
      }

      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get<FiscalDevice[]>('/devices/');
        this.devices = response.data;
      } catch (err) {
        console.error('Błąd podczas pobierania urządzeń:', err);
        this.error = 'Nie udało się załadować danych urządzeń. Spróbuj ponownie później.';
      } finally {
        this.isLoading = false;
      }
    },

    async fetchFilteredForSelect(filters: { clients?: number[], brands?: number[] } = {}) {
      if (!filters.clients?.length && !filters.brands?.length) {
        this.filteredForSelect = [];
        return;
      }

      this.isLoadingForSelect = true;
      this.error = null;
      try {
        const devices = await getDevicesForSelect(filters);
        // zawsze mapujemy po tablicy (domyślnie []), żeby uniknąć błędów
        this.filteredForSelect = (devices || []).map(d => ({
          id: d.id,
          display_name: `${d.owner?.name || '—'} - ${d.model_name || '—'} (${d.unique_number || '—'})`
        }));
      } catch (error) {
        console.error('Błąd pobierania filtrowanych urządzeń dla selecta:', error);
        this.error = 'Nie udało się załadować listy urządzeń.';
        this.filteredForSelect = []; // zapewnienie, że zawsze jest tablica
      } finally {
        this.isLoadingForSelect = false;
      }
    },

    /**
     * Dodaje nowe urządzenie fiskalne.
     * @param {DevicePayload} deviceData - Dane nowego urządzenia.
     */
    async addDevice(deviceData: DevicePayload) {
      try {
        const response = await api.post<FiscalDevice>('/devices/', deviceData);
        this.devices.unshift(response.data);
        return response.data;
      } catch (error) {
        console.error('Błąd dodawania urządzenia:', error);
        throw error;
      }
    },

    /**
     * Aktualizuje istniejące urządzenie fiskalne.
     * @param {number} deviceId - ID aktualizowanego urządzenia.
     * @param {DevicePayload} deviceData - Nowe dane urządzenia.
     */
    async updateDevice(deviceId: number, deviceData: DevicePayload) {
      try {
        const response = await api.put<FiscalDevice>(`/devices/${deviceId}/`, deviceData);
        const index = this.devices.findIndex(d => d.id === deviceId);
        if (index !== -1) {
          this.devices[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error('Błąd aktualizacji urządzenia:', error);
        throw error;
      }
    },

    updateDeviceInList(updatedDevice: FiscalDevice) {
      const index = this.devices.findIndex(d => d.id === updatedDevice.id);
      if (index !== -1) {
        this.devices[index] = updatedDevice;
      }
    },

    /**
     * Usuwa urządzenie fiskalne.
     * @param {number} deviceId - ID usuwanego urządzenia.
     */
    async deleteDevice(deviceId: number) {
      try {
        await api.delete(`/devices/${deviceId}/`);
        this.devices = this.devices.filter(d => d.id !== deviceId);
      } catch (error) {
        console.error('Błąd usuwania urządzenia:', error);
        throw error;
      }
    },
  },
});
