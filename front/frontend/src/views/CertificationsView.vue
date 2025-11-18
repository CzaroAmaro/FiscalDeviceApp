<template>
  <v-container fluid>
    <TableToolbar
      title="Certyfikaty"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />
    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="certificationHeaders"
        :items="items"
        :loading="isLoading"
      >
        <template #item.actions="{ item }">
          <div class="d-flex justify-end">
            <v-tooltip text="Edytuj">
              <template #activator="{ props }">
                <v-btn v-bind="props" icon="mdi-pencil-outline" variant="text" size="small" @click="handleEdit(item)" />
              </template>
            </v-tooltip>
            <v-tooltip text="Usuń">
              <template #activator="{ props }">
                <v-btn v-bind="props" icon="mdi-delete-outline" variant="text" size="small" color="error" @click="handleDeleteRequest(item)" />
              </template>
            </v-tooltip>
          </div>
        </template>
      </DataTable>
    </v-card>

    <CertificationFormModal
      v-model="isFormOpen"
      :editing-certification="itemToEdit"
      @save-success="handleFormSave"
    />

    <v-dialog v-model="isConfirmOpen" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5">Potwierdź usunięcie</v-card-title>
        <v-card-text>{{ confirmMessage }}<br>Tej operacji nie można cofnąć.</v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text :disabled="isDeleting" @click="isConfirmOpen = false">Anuluj</v-btn>
          <v-btn color="error" :loading="isDeleting" @click="handleDeleteConfirm">Usuń</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { storeToRefs } from 'pinia';
import { useCertificationsStore } from '@/stores/certifications';
import { useResourceView } from '@/composables/useResourceView';
import { getCertificationHeaders } from '@/config/tables/certificationHeaders';
import type { Certification } from '@/types';
import DataTable from '@/components/DataTable.vue';
import TableToolbar, { type ToolbarAction } from '@/components/TableToolbar.vue';
import CertificationFormModal from '@/components/certifications/CertificationFormModal.vue';

const { t } = useI18n();
const certificationsStore = useCertificationsStore();
const { certifications, isLoading } = storeToRefs(certificationsStore);

const {
  selectedItems,
  itemToEdit,
  isFormOpen,
  isConfirmOpen,
  isDeleting,
  items,
  confirmMessage,
  handleToolbarAction,
  handleFormSave,
  handleDeleteConfirm,
  handleEdit,
  handleDeleteRequest,
  fetchItems,
} = useResourceView<Certification>({
  resourceName: 'certyfikat',
  items: certifications,
  isLoading: isLoading,
  fetchItems: certificationsStore.fetchCertifications,
  deleteItem: certificationsStore.deleteCertification,
});

const certificationHeaders = computed(() => getCertificationHeaders(t));
const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: 'Dodaj certyfikat', icon: 'mdi-plus', requiresSelection: 'none' },
  { id: 'edit', label: 'Edytuj', icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'delete', label: 'Usuń', icon: 'mdi-delete', requiresSelection: 'multiple' },
]);

onMounted(() => fetchItems());
</script>
