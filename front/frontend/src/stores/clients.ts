import { defineStore } from 'pinia'

import api from '@/api'
import type { Client } from '@/types'

type ClientPayload = Omit<Client, 'id' | 'created_at'>;

interface ClientsState {
  clients: Client[]
  isLoading: boolean
  error: string | null
}

export const useClientsStore = defineStore('clients', {
  state: (): ClientsState => ({
    clients: [],
    isLoading: false,
    error: null,
  }),
  getters: {
    clientCount: (state) => state.clients.length,
    totalClients: (state): number => {
      return state.clients.length;
    },
  },
  actions: {
    async fetchClients() {
      if (this.clients.length > 0 && !this.isLoading) return;
      this.isLoading = true
      this.error = null
      try {
        const response = await api.get<Client[]>('/clients/')
        this.clients = response.data
      } catch (err) {
        this.error = 'Nie udało się załadować listy klientów.'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },

    async addClient(clientData: ClientPayload) {
      try {
        const response = await api.post<Client>('/clients/', clientData)
        this.clients.unshift(response.data)
        return response.data
      } catch (error) {
        console.error('Błąd dodawania klienta:', error)
        throw error
      }
    },

    async updateClient(clientId: number, clientData: ClientPayload) {
      try {
        const response = await api.put<Client>(`/clients/${clientId}/`, clientData)
        const index = this.clients.findIndex(c => c.id === clientId)
        if (index !== -1) {
          this.clients[index] = response.data // Zaktualizuj w liście bez przeładowania
        }
      } catch (error) {
        console.error('Błąd aktualizacji klienta:', error)
        throw error
      }
    },

    async deleteClient(clientId: number) {
      try {
        await api.delete(`/clients/${clientId}/`)
        this.clients = this.clients.filter(c => c.id !== clientId) // Usuń z listy bez przeładowania
      } catch (error) {
        console.error('Błąd usuwania klienta:', error)
        throw error
      }
    },
  },
})
