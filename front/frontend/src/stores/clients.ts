import { defineStore } from 'pinia';

import api from '@/api';
import type { Client, ClientLocation,ClientPayload } from '@/types';

interface ClientsState {
  clients: Client[];
  clientLocations: ClientLocation[];
  isLoading: boolean;
  isLoadingLocations: boolean;
  error: string | null;
}

export const useClientsStore = defineStore('clients', {
  state: (): ClientsState => ({
    clients: [],
    clientLocations: [],
    isLoading: false,
    isLoadingLocations: false,
    error: null,
  }),

  getters: {
    clientCount: (state) => state.clients.length,
    clientsWithLocation: (state) =>
      state.clients.filter((c) => c.latitude && c.longitude),
  },
  actions: {
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
        this.clients = this.clients.filter((c) => c.id !== clientId);
      } catch (error) {
        console.error('Błąd usuwania klienta:', error);
        throw error;
      }
    },
    async fetchClientLocations(force = false) {
      if (this.clientLocations.length > 0 && !force) return;

      this.isLoadingLocations = true;
      this.error = null;
      try {
        const response = await api.get<ClientLocation[]>('/clients/locations/');
        this.clientLocations = response.data;
      } catch (err) {
        this.error = 'Nie udało się załadować lokalizacji klientów.';
        console.error(err);
      } finally {
        this.isLoadingLocations = false;
      }
    },
  },
});
