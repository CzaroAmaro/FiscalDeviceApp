import { defineStore } from 'pinia';

import api from '@/api';
import type { ServiceTicket } from '@/types';

type ServiceTicketPayload = Omit<ServiceTicket, 'id' | 'ticket_number' | 'created_at' | 'completed_at' | 'client_name' | 'device_info' | 'technician_name'>;

export const useTicketsStore = defineStore('tickets', {
  state: () => ({
    tickets: [] as ServiceTicket[],
    isLoading: false,
    error: null as string | null,
  }),
  actions: {
    async fetchTickets() {
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
    // W przyszłości dodasz tu akcje addTicket, updateTicket, deleteTicket...
  },
});
