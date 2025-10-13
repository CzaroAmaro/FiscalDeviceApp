<template>
  <v-container fluid>
    <TableToolbar
      title="Klienci"
      :selected-count="selectedClients.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <v-card>
      <DataTable
        v-model="selectedClients"
        :headers="clientHeaders"
        :items="clientsStore.clients"
        :loading="clientsStore.isLoading"
      />
    </v-card>

    <ClientFormModal
      v-model="isFormModalOpen"
      :editing-client="clientToEdit"
      @save-success="onSaveSuccess"
    />

    <v-dialog v-model="isConfirmOpen" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5">Potwierdź usunięcie</v-card-title>
        <v-card-text>
          <span v-if="selectedClients.length === 1">
            Czy na pewno chcesz usunąć klienta <strong>"{{ selectedClients[0].name }}"</strong>?
          </span>
          <span v-else>
            Czy na pewno chcesz usunąć <strong>{{ selectedClients.length }}</strong> zaznaczonych klientów?
          </span>
          <br>Ta operacja jest nieodwracalna.
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="isConfirmOpen = false" :disabled="isDeleting">Anuluj</v-btn>
          <v-btn color="error" @click="handleDeleteConfirm" :loading="isDeleting">Usuń</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed, watch } from 'vue';
import { useClientsStore } from '@/stores/clients';
import type { Client } from '@/types';
import { clientHeaders } from '@/config/tables/clientHeaders';

import DataTable from "@/components/DataTable.vue";
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import ClientFormModal from '@/components/clients/ClientFormModal.vue';

const clientsStore = useClientsStore();

const selectedClients = ref<Client[]>([]);
const isFormModalOpen = ref(false);
const clientToEdit = ref<Client | null>(null);
const isConfirmOpen = ref(false);
const isDeleting = ref(false);
const snackbar = reactive({ show: false, text: '', color: 'success' });

onMounted(() => {
  clientsStore.fetchClients();
});

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: 'Dodaj', icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: 'Edytuj', icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: 'Usuń', icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
]);

function handleToolbarAction(actionId: string) {
  switch (actionId) {
    case 'add':
      clientToEdit.value = null;
      isFormModalOpen.value = true;
      break;
    case 'edit':
      if (selectedClients.value.length === 1) {
        clientToEdit.value = selectedClients.value[0];
        isFormModalOpen.value = true;
      }
      break;
    case 'delete':
      isConfirmOpen.value = true;
      break;
  }
}

function onSaveSuccess(message: string) {
  selectedClients.value = [];
  showSnackbar(message);
}

watch(isFormModalOpen, (isOpen) => {
  if (!isOpen) {
    clientToEdit.value = null;
  }
});

async function handleDeleteConfirm() {
  isDeleting.value = true;
  try {
    const deletePromises = selectedClients.value.map(client => clientsStore.deleteClient(client.id));
    await Promise.all(deletePromises);

    const message = selectedClients.value.length === 1
      ? `Klient "${selectedClients.value[0].name}" został usunięty.`
      : `${selectedClients.value.length} klientów zostało usuniętych.`;

    showSnackbar(message, 'info');
    selectedClients.value = [];
  } catch {
    showSnackbar('Wystąpił błąd podczas usuwania.', 'error');
  } finally {
    isDeleting.value = false;
    isConfirmOpen.value = false;
  }
}

function showSnackbar(text: string, color = 'success') {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
}
</script>
