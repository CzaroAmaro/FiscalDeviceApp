import { defineStore } from 'pinia';

import api from '@/api';
// WAŻNE: Importujemy oba typy - do odczytu (FiscalDevice) i zapisu (DevicePayload)
import type { DevicePayload,FiscalDevice } from '@/types';

// Definicja stanu pozostaje bez zmian
interface DevicesState {
  devices: FiscalDevice[];
  isLoading: boolean;
  error: string | null;
}

export const useDevicesStore = defineStore('devices', {
  state: (): DevicesState => ({
    devices: [],
    isLoading: false,
    error: null,
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
      // DOBRA PRAKTYKA: Unikaj ponownego pobierania danych, jeśli już są w stanie.
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
        // Usunięto `this.devices = []`, aby nie czyścić starych danych w przypadku błędu sieci.
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Dodaje nowe urządzenie fiskalne.
     * @param {DevicePayload} deviceData - Dane nowego urządzenia.
     */
    async addDevice(deviceData: DevicePayload) {
      try {
        // Używamy `FiscalDevice` jako typu odpowiedzi, bo serwer zwróci pełny obiekt.
        const response = await api.post<FiscalDevice>('/devices/', deviceData);
        // Optymistyczne dodanie do stanu dla natychmiastowego efektu w UI.
        this.devices.unshift(response.data);
        return response.data;
      } catch (error) {
        console.error('Błąd dodawania urządzenia:', error);
        // Rzucamy błąd dalej, aby komponent mógł na niego zareagować (np. pokazać powiadomienie).
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
          // Optymistyczna aktualizacja stanu.
          this.devices[index] = response.data;
        }
        // Zwracamy zaktualizowany obiekt, co może być przydatne w komponencie.
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
        // Optymistyczne usunięcie ze stanu.
        this.devices = this.devices.filter(d => d.id !== deviceId);
      } catch (error) {
        console.error('Błąd usuwania urządzenia:', error);
        throw error;
      }
    },
  },
});
