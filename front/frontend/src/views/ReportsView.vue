<template>
  <v-container fluid>
    <v-row>
      <!-- KOLUMNA Z FILTRAMI -->
      <v-col cols="12" md="4" lg="3">
        <v-card :loading="reportsStore.isLoadingOptions">
          <v-card-title class="d-flex align-center">
            <v-icon start>mdi-filter-variant</v-icon>
            Parametry Raportu
          </v-card-title>
          <v-divider></v-divider>

          <v-form @submit.prevent="handleGenerateReport">
            <v-card-text>
              <!-- Filtry daty -->
              <h3 class="text-subtitle-1 mb-2">Zakres dat utworzenia</h3>
              <v-text-field
                v-model="parameters.date_from"
                label="Data od"
                type="date"
                clearable
              ></v-text-field>
              <v-text-field
                v-model="parameters.date_to"
                label="Data do"
                type="date"
                clearable
              ></v-text-field>

              <v-divider class="my-4"></v-divider>

              <!-- Filtry po relacjach -->
              <h3 class="text-subtitle-1 mb-2">Filtry główne</h3>
              <v-select
                v-model="parameters.clients"
                :items="filterOptions?.clients || []"
                item-title="name"
                item-value="id"
                label="Klienci"
                multiple
                chips
                clearable
              ></v-select>
              <v-select
                v-model="parameters.technicians"
                :items="filterOptions?.technicians || []"
                item-title="name"
                item-value="id"
                label="Serwisanci"
                multiple
                chips
                clearable
              ></v-select>
              <v-select
                v-model="parameters.device_brands"
                :items="filterOptions?.brands || []"
                item-title="name"
                item-value="id"
                label="Producenci urządzeń"
                multiple
                chips
                clearable
              ></v-select>

              <v-divider class="my-4"></v-divider>

              <!-- Filtry po statusach/typach -->
              <h3 class="text-subtitle-1 mb-2">Szczegóły zgłoszenia</h3>
              <v-select
                v-model="parameters.ticket_statuses"
                :items="filterOptions?.ticket_statuses || []"
                item-title="text"
                item-value="value"
                label="Statusy zgłoszeń"
                multiple
                chips
                clearable
              ></v-select>
              <v-select
                v-model="parameters.ticket_types"
                :items="filterOptions?.ticket_types || []"
                item-title="text"
                item-value="value"
                label="Typy zgłoszeń"
                multiple
                chips
                clearable
              ></v-select>
              <v-select
                v-model="parameters.ticket_resolutions"
                :items="filterOptions?.ticket_resolutions || []"
                item-title="text"
                item-value="value"
                label="Wynik rozwiązania"
                multiple
                chips
                clearable
              ></v-select>
            </v-card-text>

            <v-divider></v-divider>

            <v-card-actions>
              <v-btn
                variant="text"
                @click="reportsStore.clearParameters"
              >
                Wyczyść
              </v-btn>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                type="submit"
                variant="flat"
                :loading="reportsStore.isLoading"
                prepend-icon="mdi-play-circle-outline"
              >
                Generuj Raport
              </v-btn>
            </v-card-actions>
          </v-form>
        </v-card>
      </v-col>

      <!-- KOLUMNA Z WYNIKAMI -->
      <v-col cols="12" md="8" lg="9">
        <v-card>
          <v-toolbar flat>
            <v-toolbar-title>
              Wyniki Raportu ({{ results.length }} {{ results.length === 1 ? 'rekord' : (results.length > 1 && results.length < 5 ? 'rekordy' : 'rekordów') }})
            </v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn
              variant="outlined"
              prepend-icon="mdi-file-pdf-box"
              :disabled="results.length === 0 || reportsStore.isLoading"
              @click="reportsStore.exportReport('pdf')"
            >
              Eksportuj PDF
            </v-btn>
          </v-toolbar>
          <v-divider></v-divider>

          <v-alert v-if="reportsStore.error" type="error" closable class="ma-4">
            {{ reportsStore.error }}
          </v-alert>

          <DataTable
            :items="results"
            :headers="reportHeaders"
            :loading="reportsStore.isLoading"
            item-key="ticket_number"
            no-data-text="Wprowadź parametry i wygeneruj raport, aby zobaczyć wyniki."
          >
          </DataTable>
          </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useReportsStore } from '@/stores/reports';
import { storeToRefs } from 'pinia';
import DataTable from '@/components/DataTable.vue'; // Upewnij się, że ścieżka jest poprawna

const reportsStore = useReportsStore();
const { parameters, filterOptions, results } = storeToRefs(reportsStore);

// Definicja nagłówków dla naszej tabeli wyników
const reportHeaders = [
  { title: 'Nr Zgłoszenia', key: 'ticket_number' },
  { title: 'Tytuł', key: 'title', sortable: true },
  { title: 'Data Utworzenia', key: 'created_at', sortable: true },
  { title: 'Klient', key: 'client_name', sortable: true },
  { title: 'NIP', key: 'client_nip' },
  { title: 'Urządzenie', key: 'device_model' },
  { title: 'Serwisant', key: 'assigned_technician_name', sortable: true },
  { title: 'Status', key: 'status_display', sortable: true },
  { title: 'Typ', key: 'ticket_type_display', sortable: true },
  { title: 'Rozwiązanie', key: 'resolution_display', sortable: true },
];

onMounted(() => {
  // Pobierz opcje dla filtrów przy pierwszym załadowaniu komponentu
  if (!reportsStore.filterOptions) {
    reportsStore.fetchFilterOptions();
  }
});

const handleGenerateReport = () => {
  reportsStore.runReport();
};
</script>

<style scoped>
/* Możesz dodać tu specyficzne style dla widoku raportów */
h3 {
  color: rgba(0,0,0,0.6);
}
</style>
