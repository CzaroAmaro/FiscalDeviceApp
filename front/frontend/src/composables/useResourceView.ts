import type { Ref } from 'vue'
import { computed,ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { useSnackbarStore } from '@/stores/snackbar';

interface ResourceViewOptions<T> {
  resourceName: string;
  items: Readonly<Ref<T[]>>;
  isLoading: Readonly<Ref<boolean>>;
  fetchItems: (force?: boolean) => Promise<void>;
  deleteItem: (id: number) => Promise<void>;
}

type ResourceItem = { id: number; name?: string; model_name?: string; serial_number?: string };

export function useResourceView<T extends ResourceItem>(
  options: ResourceViewOptions<T>
) {
  const { t } = useI18n();
  const snackbarStore = useSnackbarStore();

  const selectedItems = ref<T[]>([]) as Ref<T[]>;
  const itemToEdit = ref<T | null>(null);
  const isFormOpen = ref(false);
  const isConfirmOpen = ref(false);
  const isDeleting = ref(false);

  const { items, isLoading, fetchItems, deleteItem } = options;

  const confirmMessage = computed(() => {
    if (selectedItems.value.length === 1) {
      const item = selectedItems.value[0];
      const itemName = item.name || (item.model_name && item.serial_number && `${item.model_name} (SN: ${item.serial_number})`) || `ID: ${item.id}`;
      return t(`resources.${options.resourceName}.deleteConfirm`, { name: itemName });
    }
    return t(`resources.${options.resourceName}.deleteConfirmMulti`, { count: selectedItems.value.length });
  });

  function handleToolbarAction(actionId: string) {
    if (actionId === 'add') {
      itemToEdit.value = null;
      isFormOpen.value = true;
    } else if (actionId === 'edit' && selectedItems.value.length === 1) {
      itemToEdit.value = selectedItems.value[0];
      isFormOpen.value = true;
    } else if (actionId === 'delete' && selectedItems.value.length > 0) {
      isConfirmOpen.value = true;
    }
  }

  function handleFormSave(message: string) {
    selectedItems.value = [];
    snackbarStore.showSuccess(message);
    isFormOpen.value = false;
    itemToEdit.value = null;
  }

  async function handleDeleteConfirm() {
    isDeleting.value = true;
    try {
      await Promise.all(selectedItems.value.map(item => deleteItem(item.id)));

      const message = selectedItems.value.length === 1
        ? t(`resources.${options.resourceName}.deleteSuccessSingle`)
        : t(`resources.${options.resourceName}.deleteSuccessMulti`, { count: selectedItems.value.length });

      snackbarStore.showInfo(message);
      selectedItems.value = [];
    } catch (error) {
      console.error(`Błąd podczas usuwania zasobu '${options.resourceName}':`, error);
      snackbarStore.showError(t('errors.deleteFailed', 'Wystąpił błąd podczas usuwania.'));
    } finally {
      isDeleting.value = false;
      isConfirmOpen.value = false;
    }
  }

  return {
    selectedItems,
    itemToEdit,
    isFormOpen,
    isConfirmOpen,
    isDeleting,
    items,
    isLoading,
    confirmMessage,
    handleToolbarAction,
    handleFormSave,
    handleDeleteConfirm,
    fetchItems,
  };
}
