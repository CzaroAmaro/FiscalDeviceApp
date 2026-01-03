import { defineStore } from 'pinia';

import api from '@/api';

interface CompanyState {
  name: string | null;
  isLoading: boolean;
}

export const useCompanyStore = defineStore('company', {
  state: (): CompanyState => ({
    name: null,
    isLoading: false,
  }),

  getters: {
    companyName: (state) => state.name || 'Brak nazwy firmy',
  },

  actions: {
    async fetchCompanyName() {
      if (this.name) return;

      this.isLoading = true;
      try {
        const response = await api.get('/company/me/');
        this.name = response.data.name;
      } catch (error) {
        console.error("Nie udało się pobrać danych firmy:", error);
      } finally {
        this.isLoading = false;
      }
    },
    setCompanyName(name: string) {
      this.name = name;
    },
    clearCompanyData() {
      this.name = null;
    }
  },
});
