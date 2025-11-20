import { defineStore } from 'pinia';

import api from '@/api';
import type { ServiceTicket, ServiceTicketPayload, TicketResolutionPayload } from '@/types'

interface TicketsState {
  tickets: ServiceTicket[];
  isLoading: boolean;
  error: string | null;
  movingTicketId: number | null;
  lastUpdate: number | null;
}

export const useTicketsStore = defineStore('tickets', {
  state: (): TicketsState => ({
    tickets: [],
    isLoading: false,
    error: null,
    movingTicketId: null,
    lastUpdate: null,
  }),

  getters: {
    openTicketsCount: (state) => state.tickets.filter(t => t.status === 'open' || t.status === 'in_progress').length,
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
    async updateTicketStatus(ticketId: number, status: 'open' | 'in_progress' | 'closed') {
      if (this.movingTicketId === ticketId) {
        console.warn(`Ticket ${ticketId} jest już w trakcie przenoszenia`);
        return;
      }

      this.movingTicketId = ticketId;

      try {
        const response = await api.patch<ServiceTicket>(`/tickets/${ticketId}/`, { status });
        const index = this.tickets.findIndex(t => t.id === ticketId);
        if (index !== -1) {
          this.tickets[index] = { ...this.tickets[index], ...response.data };
        }
        this.lastUpdate = Date.now();
        return response.data;
      } catch (error) {
        console.error(`Błąd aktualizacji statusu zgłoszenia ${ticketId}:`, error);
        await this.fetchTickets(true);
        throw error;
      } finally {
        this.movingTicketId = null;
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
    async resolveTicket(ticketId: number, payload: TicketResolutionPayload) {
      this.isLoading = true;
      try {
        const response = await api.post<ServiceTicket>(`/tickets/${ticketId}/resolve/`, payload);
        // Znajdź i zaktualizuj zgłoszenie w liście
        const index = this.tickets.findIndex(t => t.id === ticketId);
        if (index !== -1) {
          this.tickets[index] = response.data;
        }
        this.error = null;
      } catch (error: any) {
        console.error('Błąd zamykania zgłoszenia:', error);
        this.error = error.response?.data?.detail || 'Nie udało się zakończyć zgłoszenia.';
        throw new Error(this.error);
      } finally {
        this.isLoading = false;
      }
    },
  },
});
