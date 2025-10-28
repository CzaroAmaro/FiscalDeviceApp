import { defineStore } from 'pinia';

import api from '@/api';
import type { ServiceTicket, ServiceTicketPayload } from '@/types';

interface TicketsState {
  tickets: ServiceTicket[];
  isLoading: boolean;
  error: string | null;
}

export const useTicketsStore = defineStore('tickets', {
  state: (): TicketsState => ({
    tickets: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    inProgressCount: (state) => state.tickets.filter(t => t.status === 'W toku').length,
  },

  actions: {
    async fetchTickets(force = false) {
      if (this.tickets.length > 0 && !force) return;
      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get<ServiceTicket[]>('/tickets/');
        this.tickets = response.data;
      } catch (err) {
        this.error = 'Nie udało się załadować listy zgłoszeń.';
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    // NOWOŚĆ: Implementacja CRUD dla zgłoszeń
    async addTicket(payload: ServiceTicketPayload) {
      try {
        const response = await api.post<ServiceTicket>('/tickets/', payload);
        this.tickets.unshift(response.data);
        return response.data;
      } catch (error) {
        console.error('Błąd dodawania zgłoszenia:', error);
        throw error;
      }
    },

    async updateTicket(ticketId: number, payload: ServiceTicketPayload) {
      try {
        const response = await api.put<ServiceTicket>(`/tickets/${ticketId}/`, payload);
        const index = this.tickets.findIndex((t) => t.id === ticketId);
        if (index !== -1) {
          this.tickets[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error('Błąd aktualizacji zgłoszenia:', error);
        throw error;
      }
    },

    async deleteTicket(ticketId: number) {
      try {
        await api.delete(`/tickets/${ticketId}/`);
        this.tickets = this.tickets.filter((t) => t.id !== ticketId);
      } catch (error) {
        console.error('Błąd usuwania zgłoszenia:', error);
        throw error;
      }
    },
  },
});
