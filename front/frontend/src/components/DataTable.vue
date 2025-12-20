<template>
  <div class="data-table-wrapper" :style="{ height: tableHeight }">
    <v-data-table
      v-model="internalSelected"
      v-model:items-per-page="internalItemsPerPage"
      v-model:page="internalPage"
      :headers="headers"
      :items="items"
      :loading="loading"
      item-value="id"
      show-select
      return-object
      :loading-text="t('table.loading')"
      :no-data-text="t('table.noData')"
      density="comfortable"
      class="modern-table"
      fixed-header
      hover
    >
      <template #header.data-table-select="{ allSelected, selectAll, someSelected }">
        <v-checkbox-btn
          :model-value="allSelected"
          :indeterminate="someSelected && !allSelected"
          color="primary"
          @update:model-value="selectAll(!allSelected)"
        />
      </template>

      <template #item.data-table-select="{ isSelected, toggleSelect, item }">
        <v-checkbox-btn
          :model-value="isSelected({ value: item })"
          color="primary"
          @update:model-value="toggleSelect({ value: item })"
        />
      </template>

      <template #loading>
        <v-skeleton-loader type="table-row@10" />
      </template>

      <template #no-data>
        <div class="no-data-container">
          <v-icon size="64" color="grey-lighten-1" class="mb-4">
            mdi-database-off-outline
          </v-icon>
          <p class="text-h6 text-grey-darken-1 mb-2">{{ t('table.noData') }}</p>
          <p class="text-body-2 text-grey">
            {{ t('table.tryChangingCriteria') }}
          </p>
        </div>
      </template>

      <template #bottom>
        <div class="table-footer">
          <div class="footer-info text-body-2 text-medium-emphasis">
            <span v-if="internalSelected.length > 0" class="selected-info">
              <v-icon size="16" class="mr-1">mdi-check-circle</v-icon>
              {{ t('table.selected', { count: internalSelected.length }) }}
            </span>
            <span v-else>
              {{ t('table.total', { count: items.length }) }}
            </span>
          </div>

          <div class="footer-pagination">
            <v-btn
              icon
              variant="text"
              size="small"
              :disabled="internalPage === 1"
              @click="internalPage--"
            >
              <v-icon>mdi-chevron-left</v-icon>
            </v-btn>

            <span class="pagination-text text-body-2">
              {{ t('table.pageOf', { current: internalPage, total: pageCount }) }}
            </span>

            <v-btn
              icon
              variant="text"
              size="small"
              :disabled="internalPage >= pageCount"
              @click="internalPage++"
            >
              <v-icon>mdi-chevron-right</v-icon>
            </v-btn>
          </div>

          <div class="footer-per-page">
            <span class="text-body-2 text-medium-emphasis mr-2">{{ t('table.rows') }}:</span>
            <v-select
              v-model="internalItemsPerPage"
              :items="itemsPerPageOptions"
              density="compact"
              variant="outlined"
              hide-details
              class="per-page-select"
            />
          </div>
        </div>
      </template>

      <template v-for="(_, slotName) in filteredSlots" :key="slotName" #[slotName]="scope">
        <slot :name="slotName" v-bind="scope" />
      </template>
    </v-data-table>
  </div>
</template>

<script setup lang="ts" generic="T extends { id: number }">
import { computed, ref, watch, useSlots } from 'vue'
import { useI18n } from 'vue-i18n'
import type { VDataTable } from 'vuetify/components'

type ReadonlyHeaders = InstanceType<typeof VDataTable>['headers']

const props = withDefaults(defineProps<{
  modelValue?: T[]
  headers: ReadonlyHeaders
  items: T[]
  loading: boolean
  itemsPerPage?: number
  height?: string
  itemsPerPageOptions?: number[]
}>(), {
  modelValue: () => [],
  itemsPerPage: 25,
  height: 'calc(100vh - 280px)',
  itemsPerPageOptions: () => [10, 25, 50, 100],
});

const emit = defineEmits<{
  (e: 'update:modelValue', selectedItems: T[]): void
}>();

const { t } = useI18n()

const slots = useSlots();

const internalPage = ref(1);
const internalItemsPerPage = ref(props.itemsPerPage);

const pageCount = computed(() => {
  if (!props.items.length || internalItemsPerPage.value <= 0) return 1;
  return Math.ceil(props.items.length / internalItemsPerPage.value);
});

watch(internalItemsPerPage, () => {
  internalPage.value = 1;
});

watch(pageCount, (newCount) => {
  if (internalPage.value > newCount) {
    internalPage.value = Math.max(1, newCount);
  }
});

watch(() => props.items.length, () => {
  if (internalPage.value > pageCount.value) {
    internalPage.value = 1;
  }
});

const filteredSlots = computed(() => {
  const reserved = ['loading', 'no-data', 'bottom', 'header.data-table-select', 'item.data-table-select'];
  return Object.fromEntries(
    Object.entries(slots).filter(([name]) => !reserved.includes(name))
  );
});

const internalSelected = computed<T[]>({
  get() {
    return props.modelValue ?? [];
  },
  set(value: T[]) {
    emit('update:modelValue', value);
  },
});

const tableHeight = computed(() => props.height);
</script>

<style scoped>
.data-table-wrapper {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 12px;
}

/* ===== GŁÓWNA TABELA ===== */
.modern-table {
  --table-header-bg: rgba(var(--v-theme-primary), 0.08);
  --table-row-hover: rgba(var(--v-theme-primary), 0.04);
  --table-row-selected: rgba(var(--v-theme-primary), 0.12);
  --table-border: rgba(var(--v-border-color), 0.08);

  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
}

/* ===== NAGŁÓWEK ===== */
.modern-table :deep(thead) {
  position: sticky;
  top: 0;
  z-index: 2;
}

.modern-table :deep(thead tr) {
  background: var(--table-header-bg) !important;
}

.modern-table :deep(thead th) {
  font-weight: 600 !important;
  font-size: 0.75rem !important;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgb(var(--v-theme-on-surface)) !important;
  border-bottom: 2px solid rgba(var(--v-theme-primary), 0.3) !important;
  padding: 16px 12px !important;
  white-space: nowrap;
}

.modern-table :deep(thead th .v-data-table-header__content) {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Ikona sortowania */
.modern-table :deep(thead th .v-icon) {
  opacity: 0.5;
  transition: opacity 0.2s ease;
}

.modern-table :deep(thead th:hover .v-icon) {
  opacity: 1;
}

/* ===== CIAŁO TABELI ===== */
.modern-table :deep(.v-table__wrapper) {
  flex: 1;
  overflow-y: auto;
}

.modern-table :deep(tbody tr) {
  transition: all 0.15s ease;
}

.modern-table :deep(tbody tr:hover) {
  background: var(--table-row-hover) !important;
}

.modern-table :deep(tbody tr.v-data-table__selected) {
  background: var(--table-row-selected) !important;
}

.modern-table :deep(tbody td) {
  padding: 12px !important;
  border-bottom: 1px solid var(--table-border) !important;
  font-size: 0.875rem;
}

/* Ostatni wiersz bez borderu */
.modern-table :deep(tbody tr:last-child td) {
  border-bottom: none !important;
}

/* ===== ZEBRA STRIPES ===== */
.modern-table :deep(tbody tr:nth-child(even)) {
  background: rgba(var(--v-theme-on-surface), 0.02);
}

.modern-table :deep(tbody tr:nth-child(even):hover) {
  background: var(--table-row-hover) !important;
}

/* ===== BRAK DANYCH ===== */
.no-data-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

/* ===== STOPKA / PAGINACJA ===== */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgb(var(--v-theme-surface));
  border-top: 1px solid rgba(var(--v-border-color), 0.12);
  gap: 16px;
  flex-wrap: wrap;
  min-height: 52px;
}

.footer-info {
  display: flex;
  align-items: center;
  min-width: 150px;
}

.selected-info {
  display: flex;
  align-items: center;
  color: rgb(var(--v-theme-primary));
  font-weight: 500;
}

.footer-pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pagination-text {
  min-width: 120px;
  text-align: center;
}

.footer-per-page {
  display: flex;
  align-items: center;
}

.per-page-select {
  width: 85px;
}

.per-page-select :deep(.v-field) {
  border-radius: 8px;
}

.per-page-select :deep(.v-field__input) {
  padding: 6px 8px;
  min-height: 36px;
}

/* ===== SCROLLBAR ===== */
.modern-table :deep(.v-table__wrapper)::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.modern-table :deep(.v-table__wrapper)::-webkit-scrollbar-track {
  background: transparent;
}

.modern-table :deep(.v-table__wrapper)::-webkit-scrollbar-thumb {
  background: rgba(var(--v-theme-on-surface), 0.2);
  border-radius: 4px;
}

.modern-table :deep(.v-table__wrapper)::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.3);
}

/* ===== CHECKBOX ===== */
.modern-table :deep(.v-checkbox-btn) {
  min-height: unset;
}

.modern-table :deep(.v-selection-control) {
  min-height: unset;
}

/* ===== RESPONSYWNOŚĆ ===== */
@media (max-width: 768px) {
  .table-footer {
    flex-direction: column;
    gap: 12px;
  }

  .footer-info,
  .footer-pagination,
  .footer-per-page {
    width: 100%;
    justify-content: center;
  }
}
</style>
