import { defineStore } from 'pinia';

import api from '@/api';
import type { Technician } from '@/types';

type TechnicianPayload = {
  user: number;
  phone_number: string;
  is_active: boolean;
};

export const useTechniciansStore = defineStore('technicians', {
  state: () => ({
    technicians: [] as Technician[],
    isLoading: false,
    error: null as string | null,
  }),

  getters: {
    technicianCount: (state) => state.technicians.length,
  },

  actions: {
    async fetchTechnicians(force = false) {
      if (this.technicians.length > 0 && !force) return;
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get<Technician[]>('/technicians/');
        this.technicians = response.data;
      } catch (error) {
        console.error('Błąd pobierania serwisantów:', error);
        this.error = 'Nie udało się pobrać listy serwisantów.';
      } finally {
        this.isLoading = false;
      }
    },

    async addTechnician(payload: TechnicianPayload): Promise<Technician> {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.post<Technician>('/technicians/', payload);
        this.technicians.push(response.data);
        return response.data;
      } catch (error) {
        console.error('Błąd dodawania serwisanta:', error);
        this.error = 'Błąd serwera podczas dodawania serwisanta.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async updateTechnician(id: number, payload: TechnicianPayload): Promise<Technician> {
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.put<Technician>(`/technicians/${id}/`, payload);
        const index = this.technicians.findIndex(t => t.id === id);
        if (index !== -1) {
          this.technicians[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error(`Błąd aktualizacji serwisanta o ID ${id}:`, error);
        this.error = 'Błąd serwera podczas aktualizacji serwisanta.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },

    async deleteTechnician(id: number): Promise<void> {
      this.isLoading = true;
      this.error = null;
      try {
        await api.delete(`/technicians/${id}/`);
        this.technicians = this.technicians.filter(t => t.id !== id);
      } catch (error) {
        console.error(`Błąd usuwania serwisanta o ID ${id}:`, error);
        this.error = 'Błąd serwera podczas usuwania serwisanta.';
        throw error;
      } finally {
        this.isLoading = false;
      }
    },
  },
});
