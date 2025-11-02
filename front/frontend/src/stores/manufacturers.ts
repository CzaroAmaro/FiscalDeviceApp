import { defineStore } from 'pinia';

import api from '@/api';
import type { Manufacturer } from '@/types';

type ManufacturerPayload = Pick<Manufacturer, 'name'>;

export const useManufacturersStore = defineStore('manufacturers', {
  state: () => ({
    manufacturers: [] as Manufacturer[],
    isLoading: false,
    error: null as string | null,
  }),
  getters: {
    manufacturerCount: (state) => state.manufacturers.length,
  },

  actions: {
    /**
     * Pobiera listę producentów.
     * @param force - Jeśli true, pobierze dane z serwera nawet jeśli są już w stanie.
     */
    async fetchManufacturers(force = false) {
      if (this.manufacturers.length > 0 && !force) return;
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get<Manufacturer[]>('/manufacturers/');
        this.manufacturers = response.data;
      } catch (error) {
        console.error('Błąd pobierania listy producentów:', error);
        this.error = 'Nie udało się pobrać listy producentów.';
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Dodaje nowego producenta.
     */
    async addManufacturer(payload: ManufacturerPayload): Promise<Manufacturer> {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.post<Manufacturer>('/manufacturers/', payload);
        // Dodajemy do lokalnego stanu, aby uniknąć ponownego fetch
        this.manufacturers.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Błąd dodawania producenta:', error);
        this.error = 'Błąd serwera podczas dodawania producenta.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Aktualizuje istniejącego producenta.
     */
    async updateManufacturer(id: number, payload: ManufacturerPayload): Promise<Manufacturer> {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.put<Manufacturer>(`/manufacturers/${id}/`, payload);
        const index = this.manufacturers.findIndex(m => m.id === id);
        if (index !== -1) {
          this.manufacturers[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error(`Błąd aktualizacji producenta o ID ${id}:`, error);
        this.error = 'Błąd serwera podczas aktualizacji producenta.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Usuwa producenta.
     */
    async deleteManufacturer(id: number): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        await api.delete(`/manufacturers/${id}/`);
        // Usuwamy z lokalnego stanu
        this.manufacturers = this.manufacturers.filter(m => m.id !== id);
      } catch (error) {
        console.error(`Błąd usuwania producenta o ID ${id}:`, error);
        this.error = 'Błąd serwera podczas usuwania producenta.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
