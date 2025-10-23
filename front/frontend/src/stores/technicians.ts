import { defineStore } from 'pinia';

import api from '@/api';
import type { Technician } from '@/types';

export const useTechniciansStore = defineStore('technicians', {
  state: () => ({
    technicians: [] as Technician[],
    isLoading: false,
  }),
  actions: {
    async fetchTechnicians() {
      if (this.technicians.length > 0) return;
      this.isLoading = true;
      try {
        const response = await api.get<Technician[]>('/technicians/');
        this.technicians = response.data;
      } catch (error) {
        console.error('Błąd pobierania serwisantów:', error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
