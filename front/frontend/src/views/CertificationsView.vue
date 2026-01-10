<template>
  <v-container fluid>
    <TableToolbar
      :title="t('certifications.title')"
      :selected-count="selectedItems.length"
      :actions="toolbarActions"
      @action="handleToolbarAction"
    />

    <div class="mb-4 flex items-center gap-3">
      <v-text-field
        v-model="searchQuery"
        density="compact"
        variant="solo"
        hide-details
        prepend-inner-icon="mdi-magnify"
        :placeholder="t('certifications.search.placeholder')"
        clearable
        style="max-width: 300px"
        @click:clear="onClearSearch"
      />
    </div>

    <v-card>
      <DataTable
        v-model="selectedItems"
        :headers="certificationHeaders"
        :items="filteredItems"
        :loading="isLoading"
        :items-per-page="25"
      >
        <template #item.expiry_date="{ item }">
          <div class="d-flex align-center">
            <span>{{ formatDate(item.expiry_date) }}</span>
            <v-chip
              v-if="isExpired(item.expiry_date)"
              color="error"
              size="x-small"
              variant="flat"
              class="ml-2"
            >
              {{ t('certifications.status.expired') }}
            </v-chip>
            <v-chip
              v-else-if="isExpiringSoon(item.expiry_date)"
              color="warning"
              size="x-small"
              variant="flat"
              class="ml-2"
            >
              {{ t('certifications.status.expiring') }}
            </v-chip>
          </div>
        </template>
      </DataTable>
    </v-card>

    <CertificationFormModal
      v-model="isFormOpen"
      :editing-certification="itemToEdit"
      @save-success="handleFormSave"
    />

    <CertificationDetailsDrawer
      v-model="isDetailsDrawerOpen"
      :certification="itemToView"
      @edit="handleEditFromDrawer"
      @renew="handleRenewFromDrawer"
      @delete="handleDeleteFromDrawer"
    />

    <v-dialog v-model="isConfirmOpen" max-width="500" persistent>
      <v-card>
        <v-card-title class="text-h5">{{ t('common.confirmDelete') }}</v-card-title>
        <v-card-text>{{ t('common.confirmDeleteMsg') }}</v-card-text>
        <v-card-actions>
          <v-spacer/>
          <v-btn text :disabled="isDeleting" @click="isConfirmOpen = false">{{ t('common.cancel') }}</v-btn>
          <v-btn color="error" :loading="isDeleting" @click="handleDeleteConfirm">{{ t('common.delete') }}</v-btn>
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
import CertificationDetailsDrawer from '@/components/certifications/CertificationDetailsDrawer.vue';

const { t } = useI18n();
const certificationsStore = useCertificationsStore();
const { certifications, isLoading } = storeToRefs(certificationsStore);

const isDetailsDrawerOpen = ref(false);
const itemToView = ref<Certification | null>(null);

const {
  selectedItems,
  itemToEdit,
  isFormOpen,
  isConfirmOpen,
  isDeleting,
  items,
  handleToolbarAction,
  handleFormSave,
  handleDeleteConfirm,
  handleDeleteRequest,
  fetchItems,
} = useResourceView<Certification>({
  resourceName: 'certyfikat',
  items: certifications,
  isLoading: isLoading,
  fetchItems: certificationsStore.fetchCertifications,
  deleteItem: certificationsStore.deleteCertification,
  customActions: {
    view_details: (selected) => {
      if (selected.length !== 1) return;
      itemToView.value = selected[0];
      isDetailsDrawerOpen.value = true;
    },
  },
});

const certificationHeaders = computed(() => getCertificationHeaders(t));

const toolbarActions = computed<ToolbarAction[]>(() => [
  { id: 'add', label: t('certifications.toolbar.add'), icon: 'mdi-plus', color: 'success', requiresSelection: 'none' },
  { id: 'edit', label: t('certifications.toolbar.edit'), icon: 'mdi-pencil', requiresSelection: 'single' },
  { id: 'view_details', label: t('certifications.toolbar.viewDetails'), icon: 'mdi-eye', requiresSelection: 'single' },
  { id: 'delete', label: t('certifications.toolbar.delete'), icon: 'mdi-delete', color: 'error', requiresSelection: 'multiple' },
]);

const searchQuery = ref('');

const filteredItems = computed(() => {
  const q = (searchQuery.value || '').toString().trim().toLowerCase();
  const all = items.value || [];
  if (!q) return all;
  return all.filter((c: Certification) => {
    const name = (c.technician_name || '').toString().toLowerCase();
    const number = (c.certificate_number || '').toString().toLowerCase();
    const manufacturer = (c.manufacturer_name || '').toString().toLowerCase();
    return name.includes(q) || number.includes(q) || manufacturer.includes(q);
  });
});

function onClearSearch() {
  searchQuery.value = '';
}

function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('pl-PL');
}

function isExpired(expiryDate: string): boolean {
  return new Date(expiryDate) < new Date();
}

function isExpiringSoon(expiryDate: string): boolean {
  if (isExpired(expiryDate)) return false;
  const expiry = new Date(expiryDate);
  const today = new Date();
  const diffDays = Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  return diffDays <= 30;
}

function handleEditFromDrawer(certification: Certification) {
  isDetailsDrawerOpen.value = false;
  itemToEdit.value = certification;
  isFormOpen.value = true;
}

function handleRenewFromDrawer(certification: Certification) {
  isDetailsDrawerOpen.value = false;
  itemToEdit.value = {
    ...certification,
    issue_date: new Date().toISOString().split('T')[0],
    expiry_date: new Date(new Date().setFullYear(new Date().getFullYear() + 1)).toISOString().split('T')[0],
  };
  isFormOpen.value = true;
}

function handleDeleteFromDrawer(certification: Certification) {
  isDetailsDrawerOpen.value = false;
  handleDeleteRequest(certification);
}

onMounted(() => fetchItems());
</script>
