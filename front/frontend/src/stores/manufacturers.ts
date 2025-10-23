import { defineStore } from 'pinia';

import api from '@/api';
import type { Manufacturer } from '@/types';

export const useManufacturersStore = defineStore('manufacturers', {
  state: () => ({
    manufacturers: [] as Manufacturer[],
    isLoading: false,
  }),
  actions: {
    /**
     * Pobiera listę wszystkich producentów (słownik).
     */
    async fetchManufacturers() {
      if (this.manufacturers.length > 0) return;
      this.isLoading = true;
      try {
        const response = await api.get<Manufacturer[]>('/manufacturers/');
        this.manufacturers = response.data;
      } catch (error) {
        console.error('Błąd pobierania listy producentów:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
