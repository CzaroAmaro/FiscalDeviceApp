import { defineStore } from 'pinia';

import api from '@/api';
import type { Client, ClientPayload } from '@/types';

interface ClientsState {
  clients: Client[];
  isLoading: boolean;
  error: string | null;
}

export const useClientsStore = defineStore('clients', {
  state: (): ClientsState => ({
    clients: [],
    isLoading: false,
    error: null,
  }),

  getters: {
    clientCount: (state) => state.clients.length,
  },
  actions: {
    // DOBRA PRAKTYKA: Dodajemy parametr 'force' do przeładowania danych
    async fetchClients(force = false) {
      if (this.clients.length > 0 && !force) return;

      this.isLoading = true;
      this.error = null;
      try {
        const response = await api.get<Client[]>('/clients/');
        this.clients = response.data;
      } catch (err) {
        this.error = 'Nie udało się załadować listy klientów.';
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },

    async addClient(clientData: ClientPayload) {
      try {
        const response = await api.post<Client>('/clients/', clientData);
        // Optymistyczne dodanie do stanu dla natychmiastowego efektu w UI
        this.clients.unshift(response.data);
        return response.data;
      } catch (error) {
        console.error('Błąd dodawania klienta:', error);
        throw error;
      }
    },

    async updateClient(clientId: number, clientData: ClientPayload) {
      try {
        const response = await api.put<Client>(`/clients/${clientId}/`, clientData);
        const index = this.clients.findIndex((c) => c.id === clientId);
        if (index !== -1) {
          // Optymistyczna aktualizacja stanu
          this.clients[index] = response.data;
        }
        return response.data;
      } catch (error) {
        console.error('Błąd aktualizacji klienta:', error);
        throw error;
      }
    },

    async deleteClient(clientId: number) {
      try {
        await api.delete(`/clients/${clientId}/`);
        // Optymistyczne usunięcie ze stanu
        this.clients = this.clients.filter((c) => c.id !== clientId);
      } catch (error) {
        console.error('Błąd usuwania klienta:', error);
        throw error;
      }
    },
  },
});
