<template>
  <v-container fluid>
    <v-row class="align-center mb-4">
      <v-col>
        <h1 class="text-h4">Klienci</h1>
      </v-col>
      <v-col class="text-right">
        <v-btn color="primary" @click="openAddModal">
          <v-icon start>mdi-plus</v-icon>
          Dodaj klienta
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-alert v-if="clientsStore.error" type="error" class="ma-4">
        {{ clientsStore.error }}
      </v-alert>
      <ClientDataTable
        :clients="clientsStore.clients"
        :loading="clientsStore.isLoading"
        @edit="openEditModal"
        @delete="openDeleteConfirm"
      />
    </v-card>

    <ClientFormModal
      v-model="isFormModalOpen"
      :editing-client="selectedClient"
      @save-success="showSnackbar"
    />

    <v-dialog v-model="isConfirmOpen" max-width="400" persistent>
      <v-card>
        <v-card-title class="text-h5">Potwierdź usunięcie</v-card-title>
        <v-card-text>
          Czy na pewno chcesz usunąć klienta "{{ selectedClient?.name }}"? Ta operacja jest nieodwracalna.
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="isConfirmOpen = false">Anuluj</v-btn>
          <v-btn color="error" @click="handleDelete">Usuń</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useClientsStore } from '@/stores/clients'
import type { Client } from '@/types'
import ClientDataTable from '@/components/clients/ClientDataTable.vue'
import ClientFormModal from '@/components/clients/ClientFormModal.vue'

const clientsStore = useClientsStore()

const isFormModalOpen = ref(false)
const isConfirmOpen = ref(false)
const selectedClient = ref<Client | null>(null)
const snackbar = reactive({ show: false, text: '', color: 'success' })

onMounted(() => {
  clientsStore.fetchClients()
})

const openAddModal = () => {
  selectedClient.value = null
  isFormModalOpen.value = true
}

const openEditModal = (client: Client) => {
  selectedClient.value = { ...client } // Kopiujemy, aby uniknąć reaktywności
  isFormModalOpen.value = true
}

const openDeleteConfirm = (client: Client) => {
  selectedClient.value = client
  isConfirmOpen.value = true
}

const handleDelete = async () => {
  if (selectedClient.value) {
    await clientsStore.deleteClient(selectedClient.value.id)
    showSnackbar(`Klient ${selectedClient.value.name} został usunięty.`, 'info')
  }
  isConfirmOpen.value = false
}

const showSnackbar = (text: string, color = 'success') => {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}
</script>
