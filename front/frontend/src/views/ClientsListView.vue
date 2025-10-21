<template>
  <v-container fluid>
    <TableToolbar
      :title="t('clients.title')"
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
        <v-card-title class="text-h5">{{ t('common.confirmDelete') }}</v-card-title>
        <v-card-text>
          {{ confirmMessage }}
          <br>{{ t('common.confirmDeleteMsg') }}
        </v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text @click="isConfirmOpen = false" :disabled="isDeleting">{{ t('common.cancel') }}</v-btn>
          <v-btn color="error" @click="handleDeleteConfirm" :loading="isDeleting">{{ t('common.delete') }}</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import { useClientsStore } from '@/stores/clients'
import type { Client } from '@/types'
import { clientHeaders } from '@/config/tables/clientHeaders'

import DataTable from "@/components/DataTable.vue"
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue'
import ClientFormModal from '@/components/clients/ClientFormModal.vue'

const clientsStore = useClientsStore()
const { t } = useI18n()

// Reactive state
const selectedClients = ref<Client[]>([])
const isFormModalOpen = ref(false)
const clientToEdit = ref<Client | null>(null)
const isConfirmOpen = ref(false)
const isDeleting = ref(false)
const snackbar = reactive({ show: false, text: '', color: 'success' })

// Toolbar actions
const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('clients.toolbar.add'), icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: t('clients.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: t('clients.toolbar.delete'), icon: 'mdi-delete', color: 'error', variant: 'outlined', requiresSelection: 'multiple' },
])

// ✅ Computed zamiast watch
const confirmMessage = computed(() =>
  selectedClients.value.length === 1
    ? t('clients.deleteConfirm', { name: selectedClients.value[0].name })
    : t('clients.deleteConfirmMulti', { count: selectedClients.value.length })
)

// ✅ Funkcja obsługująca akcje toolbaru
function handleToolbarAction(actionId: string) {
  clientToEdit.value = actionId === 'edit' && selectedClients.value.length === 1
    ? selectedClients.value[0]
    : null

  isFormModalOpen.value = actionId === 'add' || actionId === 'edit'
  isConfirmOpen.value = actionId === 'delete'
}


watchEffect(() => !isFormModalOpen.value && (clientToEdit.value = null))

function onSaveSuccess(message: string) {
  selectedClients.value = []
  showSnackbar(message)
}

async function handleDeleteConfirm() {
  isDeleting.value = true
  try {
    await Promise.all(selectedClients.value.map(client => clientsStore.deleteClient(client.id)))

    const message = selectedClients.value.length === 1
      ? `Klient "${selectedClients.value[0].name}" został usunięty.`
      : `${selectedClients.value.length} klientów zostało usuniętych.`

    showSnackbar(message, 'info')
    selectedClients.value = []
  } catch {
    showSnackbar('Wystąpił błąd podczas usuwania.', 'error')
  } finally {
    isDeleting.value = false
    isConfirmOpen.value = false
  }
}

function showSnackbar(text: string, color = 'success') {
  snackbar.text = text
  snackbar.color = color
  snackbar.show = true
}

onMounted(() => clientsStore.fetchClients())
</script>
